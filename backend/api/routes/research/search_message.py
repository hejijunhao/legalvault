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
from models.database.user import User
from models.enums.research_enums import QueryStatus
from models.dtos.research.search_message_dto import (
    SearchMessageDTO,
    SearchMessageCreateDTO,
    SearchMessageUpdateDTO,
    SearchMessageListDTO
)
from models.schemas.research.search_message import (
    SearchMessageResponse,
    SearchMessageUpdate,
    SearchMessageListResponse,
    SearchMessageCreate
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
    logger.info(f"Converting SearchMessageDTO to SearchMessageResponse for message {message_dto.id}")
    if not message_dto.search_title:
        logger.debug(f"Retrieving search title for search {message_dto.search_id}")
        search_ops = ResearchOperations(db)
        search = await search_ops.get_search_by_id(
            message_dto.search_id,
            execution_options={"no_parameters": True, "use_server_side_cursors": False}
        )
        message_dto.search_title = search.title if search else None
        logger.debug(f"Search title for search {message_dto.search_id}: {message_dto.search_title}")
    
    response = SearchMessageResponse(
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
    logger.info(f"Successfully converted message {message_dto.id} to SearchMessageResponse")
    return response

async def search_message_list_dto_to_response(message_list_dto: Union[SearchMessageListDTO, tuple], db: AsyncSession) -> SearchMessageListResponse:
    """Convert SearchMessageListDTO to SearchMessageListResponse for API layer."""
    logger.info("Converting SearchMessageListDTO to SearchMessageListResponse")
    if isinstance(message_list_dto, tuple):
        logger.debug(f"Received tuple for conversion: {message_list_dto}")
        items_data = message_list_dto[0] if len(message_list_dto) > 0 else []
        total = message_list_dto[1] if len(message_list_dto) > 1 else 0
        offset = message_list_dto[2] if len(message_list_dto) > 2 else 0
        limit = message_list_dto[3] if len(message_list_dto) > 3 else 20
    else:
        items_data = message_list_dto.items
        total = message_list_dto.total
        offset = message_list_dto.offset
        limit = message_list_dto.limit

    logger.debug(f"Converting {len(items_data)} message items")
    items = [await search_message_dto_to_response(msg, db) for msg in items_data]
    
    response = SearchMessageListResponse(
        items=items,
        total=total,
        offset=offset,
        limit=limit
    )
    logger.info("Successfully converted SearchMessageListDTO to SearchMessageListResponse")
    return response

# [HTTP routes remain unchanged]
@router.get("/{message_id}", response_model=SearchMessageResponse)
async def get_message(
    message_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get a specific message by ID."""
    logger.info(f"Received get_message request for message {message_id} by user {current_user.id}")
    message_ops = SearchMessageOperations(db)
    logger.info(f"Retrieving message {message_id}")
    message = await message_ops.get_message_by_id(
        message_id,
        execution_options={"no_parameters": True, "use_server_side_cursors": False}
    )
    
    if not message:
        logger.error(f"Message {message_id} not found")
        raise HTTPException(status_code=404, detail="Message not found")
    logger.info(f"Message {message_id} retrieved successfully")
    
    search_ops = ResearchOperations(db)
    logger.info(f"Retrieving search {message.search_id} for authorization")
    search = await search_ops.get_search_by_id(
        message.search_id,
        execution_options={"no_parameters": True, "use_server_side_cursors": False}
    )
    
    if not search or search.user_id != current_user.id:
        logger.error(f"Access denied for message {message_id}: Search not found or unauthorized")
        raise HTTPException(status_code=403, detail="Access denied")
    logger.info(f"User {current_user.id} authorized for message {message_id}")
    
    logger.info(f"Converting message {message_id} to response")
    response = await search_message_dto_to_response(message, db)
    logger.info(f"Returning get_message response for message {message_id}")
    return response

@router.get("/search/{search_id}", response_model=SearchMessageListResponse)
async def list_messages(
    search_id: UUID,
    limit: int = Query(100, ge=1, le=500, description="Maximum number of messages"),
    offset: int = Query(0, ge=0, description="Pagination offset"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """List all messages for a specific search with pagination."""
    logger.info(f"Received list_messages request for search {search_id} by user {current_user.id} with limit={limit}, offset={offset}")
    search_ops = ResearchOperations(db)
    logger.info(f"Retrieving search {search_id} for authorization")
    search = await search_ops.get_search_by_id(
        search_id,
        execution_options={"no_parameters": True, "use_server_side_cursors": False}
    )
    
    if not search or search.user_id != current_user.id:
        logger.error(f"Access denied for search {search_id}: Not found or unauthorized")
        raise HTTPException(status_code=403, detail="Access denied")
    logger.info(f"User {current_user.id} authorized for search {search_id}")
    
    message_ops = SearchMessageOperations(db)
    logger.info(f"Retrieving messages for search {search_id}")
    messages = await message_ops.get_messages_list_response(
        search_id, 
        limit, 
        offset,
        execution_options={"no_parameters": True, "use_server_side_cursors": False}
    )
    logger.info(f"Retrieved {messages.total if hasattr(messages, 'total') else 0} messages for search {search_id}")
    
    logger.info(f"Converting messages for search {search_id} to response")
    response = await search_message_list_dto_to_response(messages, db)
    logger.info(f"Returning list_messages response for search {search_id}")
    return response

@router.post("/search/{search_id}", response_model=SearchMessageResponse)
async def create_message(
    search_id: UUID,
    message: SearchMessageCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a new message in a search."""
    logger.info(f"Received create_message request for search {search_id} by user {current_user.id}")
    search_ops = ResearchOperations(db)
    logger.info(f"Retrieving search {search_id} for authorization")
    search = await search_ops.get_search_by_id(
        search_id,
        execution_options={"no_parameters": True, "use_server_side_cursors": False}
    )
    
    if not search or search.user_id != current_user.id:
        logger.error(f"Access denied for search {search_id}: Not found or unauthorized")
        raise HTTPException(status_code=403, detail="Access denied")
    logger.info(f"User {current_user.id} authorized for search {search_id}")
    
    message_ops = SearchMessageOperations(db)
    logger.debug(f"Creating SearchMessageCreateDTO for search {search_id}")
    message_dto = SearchMessageCreateDTO(
        search_id=search_id,
        role=message.role,
        content=message.content,
        sequence=message.sequence if hasattr(message, 'sequence') else None,
        status=message.status if hasattr(message, 'status') else QueryStatus.PENDING
    )
    
    logger.info(f"Executing create_message for search {search_id}")
    created_message = await message_ops.create_message_with_commit(
        message_dto,
        execution_options={"no_parameters": True, "use_server_side_cursors": False}
    )
    
    if not created_message:
        logger.error(f"Failed to create message for search {search_id}")
        raise HTTPException(status_code=500, detail="Failed to create message")
    logger.info(f"Message created successfully for search {search_id}")
    
    logger.info(f"Converting created message for search {search_id} to response")
    response = await search_message_dto_to_response(created_message, db)
    logger.info(f"Returning create_message response for search {search_id}")
    return response

@router.patch("/{message_id}", response_model=SearchMessageResponse)
async def update_message(
    message_id: UUID,
    data: SearchMessageUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update a message's content."""
    logger.info(f"Received update_message request for message {message_id} by user {current_user.id}")
    message_ops = SearchMessageOperations(db)
    logger.info(f"Retrieving message {message_id}")
    message = await message_ops.get_message_by_id(
        message_id,
        execution_options={"no_parameters": True, "use_server_side_cursors": False}
    )
    
    if not message:
        logger.error(f"Message {message_id} not found")
        raise HTTPException(status_code=404, detail="Message not found")
    logger.info(f"Message {message_id} retrieved successfully")
    
    search_ops = ResearchOperations(db)
    logger.info(f"Retrieving search {message.search_id} for authorization")
    search = await search_ops.get_search_by_id(
        message.search_id,
        execution_options={"no_parameters": True, "use_server_side_cursors": False}
    )
    
    if not search or search.user_id != current_user.id:
        logger.error(f"Access denied for message {message_id}: Search not found or unauthorized")
        raise HTTPException(status_code=403, detail="Access denied")
    logger.info(f"User {current_user.id} authorized for message {message_id}")
    
    if message.role != "user":
        logger.error(f"Cannot update assistant message {message_id}")
        raise HTTPException(status_code=403, detail="Cannot update assistant messages")
    logger.info(f"Message {message_id} is user-editable")
    
    logger.debug(f"Creating SearchMessageUpdateDTO for message {message_id}")
    update_dto = SearchMessageUpdateDTO(**data.model_dump(exclude_unset=True))
    logger.info(f"Executing update_message for message {message_id}")
    success = await message_ops.update_message(
        message_id,
        update_dto,
        execution_options={"no_parameters": True, "use_server_side_cursors": False}
    )
    
    if not success:
        logger.error(f"Failed to update message {message_id}")
        raise HTTPException(status_code=500, detail="Failed to update message")
    logger.info(f"Message {message_id} updated successfully")
    
    logger.info(f"Retrieving updated message {message_id}")
    updated_message = await message_ops.get_message_by_id(
        message_id,
        execution_options={"no_parameters": True, "use_server_side_cursors": False}
    )
    logger.info(f"Converting updated message {message_id} to response")
    response = await search_message_dto_to_response(updated_message, db)
    logger.info(f"Returning update_message response for message {message_id}")
    return response

@router.delete("/{message_id}", status_code=204)
async def delete_message(
    message_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete a specific message."""
    logger.info(f"Received delete_message request for message {message_id} by user {current_user.id}")
    message_ops = SearchMessageOperations(db)
    logger.info(f"Retrieving message {message_id}")
    message = await message_ops.get_message_by_id(message_id)
    
    if not message:
        logger.error(f"Message {message_id} not found")
        raise HTTPException(status_code=404, detail="Message not found")
    logger.info(f"Message {message_id} retrieved successfully")
    
    search_ops = ResearchOperations(db)
    logger.info(f"Retrieving search {message.search_id} for authorization")
    search = await search_ops.get_search_by_id(
        message.search_id,
        execution_options={"no_parameters": True, "use_server_side_cursors": False}
    )
    
    if not search or search.user_id != current_user.id:
        logger.error(f"Access denied for message {message_id}: Search not found or unauthorized")
        raise HTTPException(status_code=403, detail="Access denied")
    logger.info(f"User {current_user.id} authorized for message {message_id}")
    
    logger.info(f"Executing delete_message for message {message_id}")
    success = await message_ops.delete_message(
        message_id,
        execution_options={"no_parameters": True, "use_server_side_cursors": False}
    )
    
    if not success:
        logger.error(f"Failed to delete message {message_id}")
        raise HTTPException(status_code=500, detail="Failed to delete message")
    logger.info(f"Message {message_id} deleted successfully")
    
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
#                 logger.info(f"Authenticating WebSocket user for search {search_id}")
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
#             logger.info(f"Retrieving search {search_id} for WebSocket authorization")
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
#                                 logger.info(f"Fetching latest messages for search {search_id}")
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
#                                 logger.info(f"Sent latest messages for search {search_id}")
#                             except Exception as e:
#                                 error_message = str(e).lower()
#                                 logger.error(f"Error fetching latest messages: {e}")
#                                 if ("prepared statement" in error_message or 
#                                     "duplicatepreparedstatementerror" in error_message or 
#                                     "invalidsqlstatementnameerror" in error_message):
#                                     logger.info(f"pgBouncer error: {e}. Retrying with fresh session...")
#                                     async with get_session_db() as fresh_db:
#                                         fresh_ops = SearchMessageOperations(fresh_db)
#                                         logger.info(f"Retrying message fetch for search {search_id}")
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
#                                         logger.info(f"Retry successful: Sent latest messages for search {search_id}")
#                                 else:
#                                     await websocket.send_json({
#                                         "type": "error",
#                                         "message": "Failed to fetch latest messages"
#                                     })
#                                     logger.info(f"Sent error response for failed message fetch")
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
#                         logger.info(f"Subscribed to message types {message_types} for search {search_id}")
#                     
#                     elif command == "ping":
#                         await websocket.send_json({
#                             "type": "pong",
#                             "timestamp": asyncio.get_event_loop().time()
#                         })
#                         logger.info(f"Sent pong response for search {search_id}")
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