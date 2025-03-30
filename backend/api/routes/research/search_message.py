# api/routes/research/search_message.py

from typing import List, Optional, Union
from uuid import UUID
import asyncio
from fastapi import APIRouter, Depends, HTTPException, Query, WebSocket, WebSocketDisconnect, status, Request
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime
import json
import asyncio
from contextlib import asynccontextmanager

from typing import List, Optional, Union
from uuid import UUID
import asyncio
from fastapi import APIRouter, Depends, HTTPException, Query, WebSocket, WebSocketDisconnect, status
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime

from core.database import get_db
from core.auth import get_current_user
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


router = APIRouter(
    prefix="/research/messages",
    tags=["research"]
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

@router.get("/{message_id}", response_model=SearchMessageResponse)
async def get_message(
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
        search_id=message.search_id,
        user_id=current_user.id,
        user_permissions=user_permissions,
        execution_options={"no_parameters": True, "use_server_side_cursors": False}
    )
    
    if not has_access:
        raise HTTPException(status_code=403, detail="Access denied")
    
    return await search_message_dto_to_response(message, db)

@router.get("/search/{search_id}", response_model=SearchMessageListResponse)
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

@router.post("/search/{search_id}", response_model=SearchMessageResponse)
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

@router.patch("/{message_id}", response_model=SearchMessageResponse)
async def update_message(
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
        search_id=message.search_id,
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

@router.delete("/{message_id}", status_code=204)
async def delete_message(
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
        search_id=message.search_id,
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


# SSE endpoint for real-time message updates
@router.get("/sse/{search_id}")
async def sse_endpoint(
    request: Request,
    search_id: UUID,
    token: str = Query(..., description="Authentication token"),
    db: AsyncSession = Depends(get_db)
):
    """
    Server-Sent Events (SSE) endpoint for real-time message updates.
    
    Allows clients to receive updates when new messages are added to a search.
    Authentication is handled via token in the query parameters.
    
    Features:
    - Heartbeat mechanism to detect stale connections
    - Real-time message streaming
    - Authentication via token
    - Automatic reconnection handling
    """
    
    async def event_generator():
        try:
            # Define pgBouncer compatibility options
            execution_options = {"no_parameters": True, "use_server_side_cursors": False}
            
            # Authenticate user from token
            try:
                user_ops = UserOperations(db)
                token_data = await user_ops.decode_token(token)
                if not token_data:
                    print("SSE authentication failed: Invalid token")
                    yield "event: error\ndata: " + json.dumps({
                        "message": "Authentication failed: Invalid or expired token"
                    }) + "\n\n"
                    return
                user_id = token_data.user_id
                
                # Get user permissions
                try:
                    user_permissions = await user_ops.get_user_permissions(
                        user_id, 
                        execution_options=execution_options
                    )
                    print(f"SSE authenticated for user {user_id} with permissions {user_permissions}")
                except Exception as e:
                    print(f"Error getting user permissions: {str(e)}")
                    user_permissions = []
                
            except Exception as e:
                print(f"SSE authentication error: {str(e)}")
                yield "event: error\ndata: " + json.dumps({
                    "message": "Authentication error"
                }) + "\n\n"
                return
            
            # Verify user has access to the search
            search_ops = ResearchOperations(db)
            try:
                has_access = await search_ops.check_user_access(
                    search_id=search_id,
                    user_id=user_id,
                    user_permissions=user_permissions,
                    execution_options=execution_options
                )
                
                if not has_access:
                    print(f"SSE access denied: User {user_id} does not have access to search {search_id}")
                    yield "event: error\ndata: " + json.dumps({
                        "message": "Access denied: You do not have permission to access this search"
                    }) + "\n\n"
                    return
                
                print(f"SSE access granted: User {user_id} has access to search {search_id}")
            except Exception as e:
                print(f"SSE error verifying search access: {e}")
                yield "event: error\ndata: " + json.dumps({
                    "message": "Error verifying search access"
                }) + "\n\n"
                return
            
            # Send initial connection established event
            yield "event: connection_established\ndata: " + json.dumps({
                "message": "Connected successfully"
            }) + "\n\n"
            
            # Initialize message operations
            message_ops = SearchMessageOperations(db)
            
            # Set up heartbeat
            heartbeat_interval = 15  # seconds
            last_message_time = asyncio.get_event_loop().time()
            
            while True:
                if await request.is_disconnected():
                    print(f"SSE client disconnected for search {search_id}")
                    break
                
                current_time = asyncio.get_event_loop().time()
                
                # Send heartbeat if no messages sent recently
                if current_time - last_message_time >= heartbeat_interval:
                    yield "event: heartbeat\ndata: " + json.dumps({
                        "timestamp": datetime.utcnow().isoformat()
                    }) + "\n\n"
                    last_message_time = current_time
                    continue
                
                # Get new messages
                try:
                    messages = await message_ops.get_messages_for_search(
                        search_id=search_id,
                        user_id=user_id,
                        user_permissions=user_permissions,
                        execution_options=execution_options
                    )
                    
                    if messages:
                        # Convert messages to response format
                        message_responses = [
                            await search_message_dto_to_response(msg, db)
                            for msg in messages
                        ]
                        
                        # Send messages event
                        yield "event: messages\ndata: " + json.dumps({
                            "messages": [msg.dict() for msg in message_responses]
                        }) + "\n\n"
                        
                        last_message_time = current_time
                
                except Exception as e:
                    print(f"Error fetching messages: {str(e)}")
                    yield "event: error\ndata: " + json.dumps({
                        "message": "Error fetching messages"
                    }) + "\n\n"
                
                # Small delay to prevent tight loop
                await asyncio.sleep(0.1)
        
        except Exception as e:
            print(f"SSE general error: {str(e)}")
            yield "event: error\ndata: " + json.dumps({
                "message": "Internal server error"
            }) + "\n\n"
        
        finally:
            print(f"SSE connection closed for search {search_id}")
    
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"  # Disable proxy buffering
        }
    )

# WebSocket for real-time message updates
@router.websocket("/ws/{search_id}")
async def websocket_endpoint(
    websocket: WebSocket, 
    search_id: UUID, 
    token: str = Query(..., description="Authentication token"),
    db: AsyncSession = Depends(get_db)
):
    """
    WebSocket endpoint for real-time message updates.
    
    Allows clients to receive updates when new messages are added to a search.
    Authentication is handled via token in the query parameters.
    
    Features:
    - Heartbeat mechanism to detect stale connections
    - Command-based interaction (subscribe, get_latest, typing, ping)
    - Authentication via token
    """
    try:
        print(f"WebSocket connection attempt for search {search_id}")
        await websocket.accept()
        print(f"WebSocket connection accepted for search {search_id}")
        
        # Define pgBouncer compatibility options
        execution_options = {"no_parameters": True, "use_server_side_cursors": False}
        
        # Authenticate user from token
        try:
            user_ops = UserOperations(db)
            token_data = await user_ops.decode_token(token)
            if not token_data:
                print("WebSocket authentication failed: Invalid token")
                await websocket.send_json({
                    "type": "error",
                    "message": "Authentication failed: Invalid or expired token"
                })
                await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
                return
            user_id = token_data.user_id
            
            # Get user permissions
            try:
                user_permissions = await user_ops.get_user_permissions(
                    user_id, 
                    execution_options=execution_options
                )
                print(f"WebSocket authenticated for user {user_id} with permissions {user_permissions}")
            except Exception as e:
                print(f"Error getting user permissions: {str(e)}")
                user_permissions = []
            
        except Exception as e:
            print(f"WebSocket authentication error: {str(e)}")
            await websocket.send_json({
                "type": "error",
                "message": "Authentication error"
            })
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
            return
        
        # Verify user has access to the search
        search_ops = ResearchOperations(db)
        try:
            # Check user access using the check_user_access method
            has_access = await search_ops.check_user_access(
                search_id=search_id,
                user_id=user_id,
                user_permissions=user_permissions,
                execution_options=execution_options
            )
            
            if not has_access:
                print(f"WebSocket access denied: User {user_id} does not have access to search {search_id}")
                await websocket.send_json({
                    "type": "error",
                    "message": "Access denied: You do not have permission to access this search"
                })
                await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
                return
            
            print(f"WebSocket access granted: User {user_id} has access to search {search_id}")
        except Exception as e:
            error_message = str(e).lower()
            print(f"WebSocket error verifying search access: {e}")
            
            # Handle pgBouncer prepared statement errors
            if ("prepared statement" in error_message or 
                "duplicatepreparedstatementerror" in error_message or 
                "invalidsqlstatementnameerror" in error_message or
                "protocolviolationerror" in error_message):
                print(f"pgBouncer prepared statement error encountered during access check: {str(e)}")
                try:
                    # Try to create a fresh session and retry
                    from sqlalchemy.ext.asyncio import AsyncSession
                    from core.database import async_engine
                    
                    print("Creating fresh session to retry access check after pgBouncer error")
                    async with AsyncSession(async_engine) as fresh_db:
                        # Create a new instance with the fresh session
                        fresh_ops = ResearchOperations(fresh_db)
                        # Retry the operation with explicit execution options
                        has_access = await fresh_ops.check_user_access(
                            search_id=search_id,
                            user_id=user_id,
                            user_permissions=user_permissions,
                            execution_options=execution_options
                        )
                        
                        if not has_access:
                            print(f"WebSocket access denied after retry: User {user_id} does not have access to search {search_id}")
                            await websocket.send_json({
                                "type": "error",
                                "message": "Access denied: You do not have permission to access this search"
                            })
                            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
                            return
                        
                        print(f"WebSocket access granted after retry: User {user_id} has access to search {search_id}")
                except Exception as retry_error:
                    print(f"Error in retry attempt for access check: {str(retry_error)}")
                    await websocket.send_json({
                        "type": "error",
                        "message": "Failed to verify search access. Please try again."
                    })
                    await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
                    return
            else:
                await websocket.send_json({
                    "type": "error",
                    "message": "Failed to verify search access"
                })
                await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
                return
        
        # Send initial message
        await websocket.send_json({
            "type": "connection_established",
            "search_id": str(search_id),
            "message": "Connected to message updates for search"
        })
        
        # Set up heartbeat task
        heartbeat_interval = 30  # seconds
        last_heartbeat = asyncio.get_event_loop().time()
        
        # Set up subscription for message updates
        # This is a simplified example - in a real implementation, you would
        # set up a proper subscription system using something like Redis pub/sub
        # or a similar mechanism to notify this WebSocket when new messages are added
        
        # Create a task for sending periodic heartbeats
        async def send_heartbeat():
            nonlocal last_heartbeat
            while True:
                await asyncio.sleep(heartbeat_interval)
                current_time = asyncio.get_event_loop().time()
                
                # If we haven't received a ping in 2.5x the heartbeat interval, consider the connection stale
                if current_time - last_heartbeat > (heartbeat_interval * 2.5):
                    print(f"WebSocket connection for search {search_id} is stale. Closing.")
                    await websocket.close(code=status.WS_1000_NORMAL_CLOSURE)
                    return
                
                # Send a heartbeat
                await websocket.send_json({
                    "type": "heartbeat",
                    "timestamp": current_time
                })
        
        # Start the heartbeat task
        heartbeat_task = asyncio.create_task(send_heartbeat())
        
        # Function to handle pgBouncer errors and retry operations
        async def execute_with_retry(operation_func, *args, **kwargs):
            try:
                # Ensure execution_options is included
                if 'execution_options' not in kwargs:
                    kwargs['execution_options'] = execution_options
                return await operation_func(*args, **kwargs)
            except Exception as e:
                error_message = str(e).lower()
                print(f"Error in WebSocket operation: {str(e)}")
                
                # Handle pgBouncer prepared statement errors
                if ("prepared statement" in error_message or 
                    "duplicatepreparedstatementerror" in error_message or 
                    "invalidsqlstatementnameerror" in error_message or
                    "protocolviolationerror" in error_message):
                    print(f"pgBouncer prepared statement error encountered: {str(e)}")
                    try:
                        # Try to create a fresh session and retry
                        from sqlalchemy.ext.asyncio import AsyncSession
                        from core.database import async_engine
                        
                        print("Creating fresh session to retry operation after pgBouncer error")
                        async with AsyncSession(async_engine) as fresh_db:
                            # Create a new instance with the fresh session
                            if operation_func.__self__.__class__.__name__ == "SearchMessageOperations":
                                fresh_ops = SearchMessageOperations(fresh_db)
                            elif operation_func.__self__.__class__.__name__ == "ResearchOperations":
                                fresh_ops = ResearchOperations(fresh_db)
                            elif operation_func.__self__.__class__.__name__ == "UserOperations":
                                fresh_ops = UserOperations(fresh_db)
                            else:
                                raise ValueError(f"Unknown operation class: {operation_func.__self__.__class__.__name__}")
                            
                            # Get the method with the same name from the fresh instance
                            method_name = operation_func.__name__
                            fresh_method = getattr(fresh_ops, method_name)
                            
                            # Retry the operation with explicit execution options
                            if 'execution_options' not in kwargs:
                                kwargs['execution_options'] = execution_options
                            return await fresh_method(*args, **kwargs)
                    except Exception as retry_error:
                        print(f"Error in retry attempt: {str(retry_error)}")
                        raise retry_error
                else:
                    raise e
        
        try:
            while True:
                # Wait for commands from the client with a timeout
                try:
                    # Use a timeout to ensure we can check for stale connections
                    data = await asyncio.wait_for(
                        websocket.receive_json(),
                        timeout=heartbeat_interval * 3
                    )
                    
                    # Update last heartbeat time whenever we receive any message
                    last_heartbeat = asyncio.get_event_loop().time()
                    
                    command = data.get("command")
                    print(f"Received command: {command} for search {search_id}")
                    
                    if command == "get_latest":
                        # Fetch latest messages
                        message_ops = SearchMessageOperations(db)
                        try:
                            # Use the retry helper function
                            messages = await execute_with_retry(
                                message_ops.list_messages_by_search,
                                search_id=search_id,
                                limit=data.get("limit", 10),
                                offset=data.get("offset", 0)
                            )
                            
                            # Convert to dict for JSON serialization
                            messages_data = []
                            for m in messages.items:
                                message_dict = m.model_dump()
                                # Convert UUIDs to strings for JSON serialization
                                if 'id' in message_dict and isinstance(message_dict['id'], UUID):
                                    message_dict['id'] = str(message_dict['id'])
                                if 'search_id' in message_dict and isinstance(message_dict['search_id'], UUID):
                                    message_dict['search_id'] = str(message_dict['search_id'])
                                messages_data.append(message_dict)
                            
                            await websocket.send_json({
                                "type": "messages",
                                "data": messages_data,
                                "total": messages.total,
                                "offset": messages.offset,
                                "limit": messages.limit
                            })
                        except Exception as e:
                            print(f"Error fetching latest messages: {e}")
                            await websocket.send_json({
                                "type": "error",
                                "message": "Failed to fetch latest messages"
                            })
                    
                    elif command == "typing":
                        # Client is typing - could broadcast to other connected clients
                        # This would be used in a collaborative environment
                        pass
                    
                    elif command == "subscribe":
                        # Subscribe to specific message types or events
                        # This is a placeholder for a more sophisticated subscription system
                        message_types = data.get("message_types", ["user", "assistant"])
                        await websocket.send_json({
                            "type": "subscription",
                            "status": "success",
                            "subscribed_to": message_types
                        })
                    
                    elif command == "ping":
                        # Client sent a ping, respond with a pong
                        await websocket.send_json({
                            "type": "pong",
                            "timestamp": asyncio.get_event_loop().time()
                        })
                
                except asyncio.TimeoutError:
                    # No message received within timeout, check if connection is still alive
                    current_time = asyncio.get_event_loop().time()
                    if current_time - last_heartbeat > (heartbeat_interval * 2.5):
                        print(f"WebSocket connection for search {search_id} timed out. Closing.")
                        await websocket.close(code=status.WS_1000_NORMAL_CLOSURE)
                        break
        except WebSocketDisconnect:
            # Handle disconnect
            print(f"WebSocket disconnected for search {search_id}")
        except Exception as e:
            # Log the error
            print(f"WebSocket error for search {search_id}: {str(e)}")
            await websocket.send_json({
                "type": "error",
                "message": "Internal server error"
            })
            await websocket.close(code=status.WS_1011_INTERNAL_ERROR)
        finally:
            # Cancel the heartbeat task if it's still running
            if 'heartbeat_task' in locals() and not heartbeat_task.done():
                heartbeat_task.cancel()
                try:
                    await heartbeat_task
                except asyncio.CancelledError:
                    pass
    except Exception as e:
        print(f"Unexpected WebSocket error: {str(e)}")
        # Try to close the connection if possible
        try:
            await websocket.send_json({
                "type": "error",
                "message": "Internal server error"
            })
            await websocket.close(code=status.WS_1011_INTERNAL_ERROR)
        except Exception:
            pass
