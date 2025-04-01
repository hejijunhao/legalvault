# api/routes/research/search_message.py

from typing import List, Optional, Union
from uuid import UUID
import asyncio
from fastapi import APIRouter, Depends, HTTPException, Query, WebSocket, WebSocketDisconnect, status
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime
import logging

from core.database import get_db, get_session_db
from core.auth import get_current_user, get_user_permissions
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

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/research/messages",
    tags=["research"]
)

# [HTTP route helper functions remain unchanged]
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

async def search_message_list_dto_to_response(message_list_dto: Union[SearchMessageListDTO, tuple], db: AsyncSession) -> SearchMessageListResponse:
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

# [HTTP routes remain unchanged]
@router.get("/{message_id}", response_model=SearchMessageResponse)
async def get_message(
    message_id: UUID,
    current_user: User = Depends(get_current_user),
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
    
    search_ops = ResearchOperations(db)
    search = await search_ops.get_search_by_id(
        message.search_id,
        execution_options={"no_parameters": True, "use_server_side_cursors": False}
    )
    
    if not search or search.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    return await search_message_dto_to_response(message, db)

@router.get("/search/{search_id}", response_model=SearchMessageListResponse)
async def list_messages(
    search_id: UUID,
    limit: int = Query(100, ge=1, le=500, description="Maximum number of messages"),
    offset: int = Query(0, ge=0, description="Pagination offset"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """List all messages for a specific search with pagination."""
    search_ops = ResearchOperations(db)
    search = await search_ops.get_search_by_id(
        search_id,
        execution_options={"no_parameters": True, "use_server_side_cursors": False}
    )
    
    if not search or search.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    message_ops = SearchMessageOperations(db)
    messages = await message_ops.get_messages_list_response(
        search_id, 
        limit, 
        offset,
        execution_options={"no_parameters": True, "use_server_side_cursors": False}
    )
    
    return await search_message_list_dto_to_response(messages, db)

@router.post("/search/{search_id}", response_model=SearchMessageResponse)
async def create_message(
    search_id: UUID,
    message: SearchMessageCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a new message in a search."""
    search_ops = ResearchOperations(db)
    search = await search_ops.get_search_by_id(
        search_id,
        execution_options={"no_parameters": True, "use_server_side_cursors": False}
    )
    
    if not search or search.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")
    
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

@router.patch("/{message_id}", response_model=SearchMessageResponse)
async def update_message(
    message_id: UUID,
    data: SearchMessageUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update a message's content."""
    message_ops = SearchMessageOperations(db)
    message = await message_ops.get_message_by_id(
        message_id,
        execution_options={"no_parameters": True, "use_server_side_cursors": False}
    )
    
    if not message:
        raise HTTPException(status_code=404, detail="Message not found")
    
    search_ops = ResearchOperations(db)
    search = await search_ops.get_search_by_id(
        message.search_id,
        execution_options={"no_parameters": True, "use_server_side_cursors": False}
    )
    
    if not search or search.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    if message.role != "user":
        raise HTTPException(status_code=403, detail="Cannot update assistant messages")
    
    update_dto = SearchMessageUpdateDTO(**data.model_dump(exclude_unset=True))
    success = await message_ops.update_message(
        message_id,
        update_dto,
        execution_options={"no_parameters": True, "use_server_side_cursors": False}
    )
    
    if not success:
        raise HTTPException(status_code=500, detail="Failed to update message")
    
    updated_message = await message_ops.get_message_by_id(
        message_id,
        execution_options={"no_parameters": True, "use_server_side_cursors": False}
    )
    return await search_message_dto_to_response(updated_message, db)

@router.delete("/{message_id}", status_code=204)
async def delete_message(
    message_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete a specific message."""
    message_ops = SearchMessageOperations(db)
    message = await message_ops.get_message_by_id(message_id)
    
    if not message:
        raise HTTPException(status_code=404, detail="Message not found")
    
    search_ops = ResearchOperations(db)
    search = await search_ops.get_search_by_id(
        message.search_id,
        execution_options={"no_parameters": True, "use_server_side_cursors": False}
    )
    
    if not search or search.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    success = await message_ops.delete_message(
        message_id,
        execution_options={"no_parameters": True, "use_server_side_cursors": False}
    )
    
    if not success:
        raise HTTPException(status_code=500, detail="Failed to delete message")
    
    return None

# Commented-out WebSocket endpoints section
"""
The following WebSocket endpoints are grouped here and commented out for future use.
They provide real-time functionality but are currently disabled to keep the API lightweight.
To re-enable, simply uncomment the desired endpoint(s).
"""

# @router.websocket("/ws/{search_id}")
# async def websocket_endpoint(
#     websocket: WebSocket, 
#     search_id: UUID, 
#     token: str = Query(..., description="Authentication token")
# ):
#     """
#     WebSocket endpoint for real-time message updates.
#     
#     Allows clients to receive updates when new messages are added to a search.
#     Authentication is handled via get_current_user for consistency with HTTP endpoints.
#     Uses short-lived sessions for each operation, compatible with transaction pooling.
#     
#     Features:
#     - Authentication via get_current_user with proper error handling
#     - Heartbeat mechanism to detect stale connections
#     - Command-based interaction (subscribe, get_latest, typing, ping)
#     - Short-lived database sessions for each operation
#     - Specific WebSocket close codes for different error scenarios
#     """
#     try:
#         logger.info(f"WebSocket connection attempt for search {search_id}")
#         await websocket.accept()
#         logger.info(f"WebSocket connection accepted for search {search_id}")
#         
#         # Authenticate user using get_current_user with a short-lived session
#         async with get_session_db() as db:
#             try:
#                 current_user = await get_current_user(token, db)
#                 logger.info(f"WebSocket authenticated for user {current_user.id}")
#             except HTTPException as e:
#                 logger.info(f"WebSocket authentication failed: {e.detail}")
#                 await websocket.send_json({
#                     "type": "error",
#                     "message": e.detail
#                 })
#                 await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
#                 return
#         
#         # Verify user has access to the search with a new session
#         async with get_session_db() as db:
#             search_ops = ResearchOperations(db)
#             search = await search_ops.get_search_by_id(
#                 search_id,
#                 execution_options={"no_parameters": True, "use_server_side_cursors": False}
#             )
#             
#             if not search:
#                 logger.info(f"Search {search_id} not found")
#                 await websocket.send_json({
#                     "type": "error",
#                     "message": "Search not found"
#                 })
#                 await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
#                 return
#             
#             if search.user_id != current_user.id:
#                 logger.info(f"Access denied: User {current_user.id} does not have access to search {search_id}")
#                 await websocket.send_json({
#                     "type": "error",
#                     "message": "Access denied: You do not have permission to access this search"
#                 })
#                 await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
#                 return
#         
#         logger.info(f"Access granted for search {search_id}")
#         
#         # Send initial success message
#         await websocket.send_json({
#             "type": "connection_established",
#             "search_id": str(search_id),
#             "message": "Connected to message updates for search"
#         })
#         
#         # Set up heartbeat task
#         heartbeat_interval = 30  # seconds
#         last_heartbeat = asyncio.get_event_loop().time()
#         
#         async def send_heartbeat():
#             nonlocal last_heartbeat
#             while True:
#                 await asyncio.sleep(heartbeat_interval)
#                 current_time = asyncio.get_event_loop().time()
#                 
#                 if current_time - last_heartbeat > (heartbeat_interval * 2.5):
#                     logger.info(f"WebSocket connection for search {search_id} is stale. Closing.")
#                     await websocket.close(code=status.WS_1000_NORMAL_CLOSURE)
#                     return
#                 
#                 await websocket.send_json({
#                     "type": "heartbeat",
#                     "timestamp": current_time
#                 })
#         
#         heartbeat_task = asyncio.create_task(send_heartbeat())
#         
#         try:
#             while True:
#                 try:
#                     data = await asyncio.wait_for(
#                         websocket.receive_json(),
#                         timeout=heartbeat_interval * 3
#                     )
#                     
#                     last_heartbeat = asyncio.get_event_loop().time()
#                     command = data.get("command")
#                     logger.info(f"Received command: {command} for search {search_id}")
#                     
#                     if command == "get_latest":
#                         async with get_session_db() as db:
#                             message_ops = SearchMessageOperations(db)
#                             try:
#                                 messages = await message_ops.list_messages_by_search(
#                                     search_id=search_id,
#                                     limit=data.get("limit", 10),
#                                     offset=data.get("offset", 0),
#                                     execution_options={"no_parameters": True, "use_server_side_cursors": False}
#                                 )
#                                 messages_data = [m.model_dump() for m in messages.items]
#                                 await websocket.send_json({
#                                     "type": "messages",
#                                     "data": messages_data,
#                                     "total": messages.total,
#                                     "offset": messages.offset,
#                                     "limit": messages.limit
#                                 })
#                             except Exception as e:
#                                 error_message = str(e).lower()
#                                 logger.error(f"Error fetching latest messages: {e}")
#                                 if ("prepared statement" in error_message or 
#                                     "duplicatepreparedstatementerror" in error_message or 
#                                     "invalidsqlstatementnameerror" in error_message):
#                                     logger.info(f"pgBouncer error: {e}. Retrying with fresh session...")
#                                     async with get_session_db() as fresh_db:
#                                         fresh_ops = SearchMessageOperations(fresh_db)
#                                         messages = await fresh_ops.list_messages_by_search(
#                                             search_id=search_id,
#                                             limit=data.get("limit", 10),
#                                             offset=data.get("offset", 0),
#                                             execution_options={"no_parameters": True, "use_server_side_cursors": False}
#                                         )
#                                         messages_data = [m.model_dump() for m in messages.items]
#                                         await websocket.send_json({
#                                             "type": "messages",
#                                             "data": messages_data,
#                                             "total": messages.total,
#                                             "offset": messages.offset,
#                                             "limit": messages.limit
#                                         })
#                                 else:
#                                     await websocket.send_json({
#                                         "type": "error",
#                                         "message": "Failed to fetch latest messages"
#                                     })
#                     
#                     elif command == "typing":
#                         pass  # Placeholder for collaborative features
#                     
#                     elif command == "subscribe":
#                         message_types = data.get("message_types", ["user", "assistant"])
#                         await websocket.send_json({
#                             "type": "subscription",
#                             "status": "success",
#                             "subscribed_to": message_types
#                         })
#                     
#                     elif command == "ping":
#                         await websocket.send_json({
#                             "type": "pong",
#                             "timestamp": asyncio.get_event_loop().time()
#                         })
#                 
#                 except asyncio.TimeoutError:
#                     current_time = asyncio.get_event_loop().time()
#                     if current_time - last_heartbeat > (heartbeat_interval * 2.5):
#                         logger.info(f"WebSocket connection for search {search_id} timed out. Closing.")
#                         await websocket.close(code=status.WS_1000_NORMAL_CLOSURE)
#                         break
#         except WebSocketDisconnect:
#             logger.info(f"WebSocket disconnected for search {search_id}")
#         except Exception as e:
#             logger.error(f"WebSocket error for search {search_id}: {str(e)}")
#             await websocket.send_json({
#                 "type": "error",
#                 "message": "Internal server error"
#             })
#             await websocket.close(code=status.WS_1011_INTERNAL_ERROR)
#         finally:
#             if 'heartbeat_task' in locals() and not heartbeat_task.done():
#                 heartbeat_task.cancel()
#                 try:
#                     await heartbeat_task
#                 except asyncio.CancelledError:
#                     pass
#     except Exception as e:
#         logger.error(f"Unexpected WebSocket error: {str(e)}")
#         try:
#             await websocket.send_json({
#                 "type": "error",
#                 "message": "Internal server error"
#             })
#             await websocket.close(code=status.WS_1011_INTERNAL_ERROR)
#         except Exception:
#             pass