# api/routes/research/search_message.py

from typing import List, Optional, Union
from uuid import UUID
import asyncio
from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime
import json
from contextlib import asynccontextmanager
import logging

from core.database import get_db, get_session_db
from core.auth import get_current_user, get_current_user_from_token
from models.domain.research.search_operations import ResearchOperations
from models.domain.research.search_message_operations import SearchMessageOperations
from models.domain.user_operations import UserOperations
from models.domain.research.research_errors import ValidationError, DatabaseError
from models.schemas.research.search_message import (
    SearchMessageResponse,
    SearchMessageUpdate,
    SearchMessageListResponse,
    SearchMessageCreate
)
from models.database.user import User
from models.enums.research_enums import QueryStatus
from models.dtos.research.search_message_dto import (
    SearchMessageDTO,
    SearchMessageCreateDTO,
    SearchMessageUpdateDTO,
    SearchMessageListDTO
)

# Set up logging
logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/v1/research/searches/{search_id}/messages",
    tags=["research"],
    responses={
        401: {"description": "Authentication required"},
        403: {"description": "Insufficient permissions"},
        429: {"description": "Too many requests"},
        500: {"description": "Internal server error"}
    }
)

stream_router = APIRouter(
    prefix="/v1/research/searches",
    tags=["research"],
    responses={
        401: {"description": "Authentication required"},
        403: {"description": "Insufficient permissions"},
        429: {"description": "Too many requests"},
        500: {"description": "Internal server error"}
    }
)

async def get_user_permissions(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> List[str]:
    """
    Dependency to get user permissions.
    """
    user_ops = UserOperations(db)
    return await user_ops.get_user_permissions(current_user.id)

async def search_message_dto_to_response(
    message_dto: SearchMessageDTO,
    db: AsyncSession
) -> SearchMessageResponse:
    """Convert DTO to response schema with search title"""
    if not message_dto.search_title:
        search_ops = ResearchOperations(db)
        search = await search_ops.get_search_by_id(
            message_dto.search_id,
            execution_options={"no_parameters": True, "use_server_side_cursors": False}
        )
        message_dto.search_title = search.title if search else None
    
    return SearchMessageResponse(
        id=message_dto.id,
        search_id=message_dto.search_id,
        search_title=message_dto.search_title,
        role=message_dto.role,
        content=message_dto.get_structured_content().to_dict(),
        sequence=message_dto.sequence,
        status=message_dto.status,
        created_at=message_dto.created_at,
        updated_at=message_dto.updated_at
    )

async def search_message_list_dto_to_response(message_list_dto: Union[SearchMessageListDTO, tuple]) -> SearchMessageListResponse:
    """Convert SearchMessageListDTO to SearchMessageListResponse for API layer."""
    if isinstance(message_list_dto, tuple):
        items_data = message_list_dto[0] if len(message_list_dto) > 0 else []
        total = message_list_dto[1] if len(message_list_dto) > 1 else 0
        offset = message_list_dto[2] if len(message_list_dto) > 2 else 0
        limit = message_list_dto[3] if len(message_list_dto) > 3 else 20
    else:
        items_data = message_list_dto.items
        total = message_list_dto.total
        offset = message_list_dto.offset
        limit = message_list_dto.limit

    items = [await search_message_dto_to_response(msg, db) for msg in items_data]
    
    return SearchMessageListResponse(
        items=items,
        total=total,
        offset=offset,
        limit=limit
    )

@router.get("/messages/{message_id}", response_model=SearchMessageResponse)
async def get_message(
    search_id: UUID,
    message_id: UUID,
    current_user: User = Depends(get_current_user),
    user_permissions: List[str] = Depends(get_user_permissions),
    db: AsyncSession = Depends(get_db)
):
    """Get a specific message by ID."""
    message_ops = SearchMessageOperations(db)
    message = await message_ops.get_message_by_id(
        message_id,
        execution_options={"no_parameters": True, "use_server_side_cursors": False}
    )
    
    if not message:
        raise HTTPException(status_code=404, detail="Message not found")
    
    # Verify user has access to the search this message belongs to
    search_ops = ResearchOperations(db)
    has_access = await search_ops.check_user_access(
        search_id=search_id,
        user_id=current_user.id,
        user_permissions=user_permissions,
        execution_options={"no_parameters": True, "use_server_side_cursors": False}
    )
    
    if not has_access:
        raise HTTPException(status_code=403, detail="Access denied")
    
    return await search_message_dto_to_response(message, db)

@router.get("/messages", response_model=SearchMessageListResponse)
async def list_messages(
    search_id: UUID,
    limit: int = Query(100, ge=1, le=500, description="Maximum number of messages"),
    offset: int = Query(0, ge=0, description="Pagination offset"),
    current_user: User = Depends(get_current_user),
    user_permissions: List[str] = Depends(get_user_permissions),
    db: AsyncSession = Depends(get_db)
):
    """
    List all messages for a specific search with pagination.
    
    Returns messages in sequence order (oldest first).
    """
    # Verify user has access to the search
    search_ops = ResearchOperations(db)
    has_access = await search_ops.check_user_access(
        search_id=search_id,
        user_id=current_user.id,
        user_permissions=user_permissions,
        execution_options={"no_parameters": True, "use_server_side_cursors": False}
    )
    
    if not has_access:
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Get messages with pagination
    message_ops = SearchMessageOperations(db)
    messages = await message_ops.get_messages_list_response(
        search_id, 
        limit, 
        offset,
        execution_options={"no_parameters": True, "use_server_side_cursors": False}
    )
    
    return await search_message_list_dto_to_response(messages)

@router.post("/messages", response_model=SearchMessageResponse)
async def create_message(
    search_id: UUID,
    message: SearchMessageCreate,
    current_user: User = Depends(get_current_user),
    user_permissions: List[str] = Depends(get_user_permissions),
    db: AsyncSession = Depends(get_db)
):
    """Create a new message in a search."""
    # Verify user has access to the search
    search_ops = ResearchOperations(db)
    has_access = await search_ops.check_user_access(
        search_id=search_id,
        user_id=current_user.id,
        user_permissions=user_permissions,
        execution_options={"no_parameters": True, "use_server_side_cursors": False}
    )
    
    if not has_access:
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Create message
    message_ops = SearchMessageOperations(db)
    message_dto = SearchMessageCreateDTO(
        search_id=search_id,
        role=message.role,
        content=message.content,
        sequence=message.sequence if hasattr(message, 'sequence') else None,
        status=message.status if hasattr(message, 'status') else QueryStatus.PENDING
    )
    
    created_message = await message_ops.create_message_with_commit(
        message_dto,
        execution_options={"no_parameters": True, "use_server_side_cursors": False}
    )
    
    if not created_message:
        raise HTTPException(status_code=500, detail="Failed to create message")
    
    return await search_message_dto_to_response(created_message, db)

@router.patch("/messages/{message_id}", response_model=SearchMessageResponse)
async def update_message(
    search_id: UUID,
    message_id: UUID,
    data: SearchMessageUpdate,
    current_user: User = Depends(get_current_user),
    user_permissions: List[str] = Depends(get_user_permissions),
    db: AsyncSession = Depends(get_db)
):
    """
    Update a message's content.
    
    Note: This should generally be limited to user messages, not assistant responses.
    """
    # Verify message exists and user has access
    message_ops = SearchMessageOperations(db)
    message = await message_ops.get_message_by_id(
        message_id,
        execution_options={"no_parameters": True, "use_server_side_cursors": False}
    )
    
    if not message:
        raise HTTPException(status_code=404, detail="Message not found")
    
    # Verify user has access to the search this message belongs to
    search_ops = ResearchOperations(db)
    has_access = await search_ops.check_user_access(
        search_id=search_id,
        user_id=current_user.id,
        user_permissions=user_permissions,
        execution_options={"no_parameters": True, "use_server_side_cursors": False}
    )
    
    if not has_access:
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Only allow updating user messages, not assistant responses
    if message.role != "user":
        raise HTTPException(
            status_code=403,
            detail="Cannot update assistant messages"
        )
    
    # Create update DTO and perform update
    update_dto = SearchMessageUpdateDTO(**data.model_dump(exclude_unset=True))
    success = await message_ops.update_message(
        message_id,
        update_dto,
        execution_options={"no_parameters": True, "use_server_side_cursors": False}
    )
    
    if not success:
        raise HTTPException(status_code=500, detail="Failed to update message")
    
    # Return updated message
    updated_message = await message_ops.get_message_by_id(
        message_id,
        execution_options={"no_parameters": True, "use_server_side_cursors": False}
    )
    return await search_message_dto_to_response(updated_message, db)

@router.delete("/messages/{message_id}", status_code=204)
async def delete_message(
    search_id: UUID,
    message_id: UUID,
    current_user: User = Depends(get_current_user),
    user_permissions: List[str] = Depends(get_user_permissions),
    db: AsyncSession = Depends(get_db)
):
    """
    Delete a specific message.
    
    Note: This should be used with caution as it may break conversation flow.
    """
    # Verify message exists
    message_ops = SearchMessageOperations(db)
    message = await message_ops.get_message_by_id(message_id)
    
    if not message:
        raise HTTPException(status_code=404, detail="Message not found")
    
    # Verify user has access to the search this message belongs to
    search_ops = ResearchOperations(db)
    has_access = await search_ops.check_user_access(
        search_id=search_id,
        user_id=current_user.id,
        user_permissions=user_permissions,
        execution_options={"no_parameters": True, "use_server_side_cursors": False}
    )
    
    if not has_access:
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Delete the message
    success = await message_ops.delete_message(
        message_id,
        execution_options={"no_parameters": True, "use_server_side_cursors": False}
    )
    
    if not success:
        raise HTTPException(status_code=500, detail="Failed to delete message")
    
    return None

@stream_router.get("/{search_id}/stream", response_class=StreamingResponse)
async def stream_search_messages(
    request: Request,
    search_id: UUID,
    token: Optional[str] = Query(None, description="Authentication token (for SSE)"),
    current_user: Optional[User] = Depends(get_current_user),  
    token_user: Optional[User] = Depends(get_current_user_from_token),  
    db: AsyncSession = Depends(get_db)  
) -> StreamingResponse:
    """
    Stream search messages in real-time using Server-Sent Events (SSE).
    Supports both header-based and token-based authentication.
    Uses raw SQL queries for pgBouncer compatibility.
    """
    # Authenticate user through either method
    authenticated_user = current_user or token_user
    if not authenticated_user:
        raise HTTPException(
            status_code=401,
            detail="Authentication required"
        )

    async def event_generator():
        try:
            # Get operations instances with pgBouncer compatibility options
            operations = SearchMessageOperations(db)
            search_ops = ResearchOperations(db)
            
            # Verify search access using raw SQL
            user_permissions = await get_user_permissions(authenticated_user, db)
            has_access = await search_ops.check_user_access_raw(
                search_id=search_id,
                user_id=authenticated_user.id,
                user_permissions=user_permissions,
                execution_options={"no_parameters": True, "use_server_side_cursors": False}
            )
            
            if not has_access:
                yield "event: error\ndata: " + json.dumps({"message": "Access denied"}) + "\n\n"
                return

            # Send initial connection event
            yield "event: connected\ndata: {}\n\n"
            
            # Initialize message buffer for collecting chunks
            message_buffer = []
            last_save_time = datetime.now()
            
            try:
                while True:
                    if await request.is_disconnected():
                        logger.debug(f"Client disconnected from SSE stream for search {search_id}")
                        break
                    
                    # Get new message chunks using raw SQL with pgBouncer options
                    try:
                        new_chunks = await operations.get_messages_raw(
                            search_id=search_id,
                            user_id=authenticated_user.id,
                            execution_options={"no_parameters": True, "use_server_side_cursors": False}
                        )
                        
                        if new_chunks:
                            # Add chunks to buffer
                            message_buffer.extend(new_chunks)
                            
                            # Stream chunks to frontend
                            for chunk in new_chunks:
                                yield f"event: chunk\ndata: {json.dumps({'content': chunk})}\n\n"
                            
                            # Save to database periodically using raw SQL
                            if (datetime.now() - last_save_time).seconds >= 5:
                                await operations.save_message_chunks_raw(
                                    search_id=search_id,
                                    chunks=message_buffer,
                                    execution_options={"no_parameters": True, "use_server_side_cursors": False}
                                )
                                message_buffer = []  # Clear buffer after saving
                                last_save_time = datetime.now()
                        
                        # Send heartbeat if no new chunks
                        elif (datetime.now() - last_save_time).seconds >= 30:
                            yield "event: heartbeat\ndata: {}\n\n"
                            last_save_time = datetime.now()
                        
                        await asyncio.sleep(0.1)
                        
                    except Exception as e:
                        logger.error(f"Error in streaming loop: {str(e)}")
                        yield f"event: error\ndata: {json.dumps({'error': 'Error processing message chunks'})}\n\n"
                        await asyncio.sleep(1)  # Wait before retrying
                
            finally:
                # Save any remaining chunks before closing
                if message_buffer:
                    try:
                        await operations.save_message_chunks_raw(
                            search_id=search_id,
                            chunks=message_buffer,
                            execution_options={"no_parameters": True, "use_server_side_cursors": False}
                        )
                    except Exception as e:
                        logger.error(f"Error saving final chunks: {str(e)}")
                
                yield "event: complete\ndata: {}\n\n"
        
        except Exception as e:
            logger.error(f"Error in SSE stream: {str(e)}")
            yield f"event: error\ndata: {json.dumps({'error': str(e)})}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Content-Type": "text/event-stream"
        }
    )
