# api/routes/research/search_message.py

from typing import List, Optional
from uuid import UUID
import asyncio
from fastapi import APIRouter, Depends, HTTPException, Query, WebSocket, WebSocketDisconnect, status
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db
from core.auth import get_current_user, get_user_permissions, decode_access_token
from models.domain.research.search_operations import ResearchOperations
from models.domain.research.search_message_operations import SearchMessageOperations
from models.schemas.research.search_message import (
    SearchMessageResponse,
    SearchMessageUpdate,
    SearchMessageListResponse,
    SearchMessageForwardRequest
)

router = APIRouter(
    prefix="/research/messages",
    tags=["research"]
)


@router.get("/{message_id}", response_model=SearchMessageResponse)
async def get_message(
    message_id: UUID,
    current_user: dict = Depends(get_current_user),
    user_permissions: List[str] = Depends(get_user_permissions),
    db: AsyncSession = Depends(get_db)
):
    """
    Get a specific message by ID.
    
    Retrieves the full details of a message within a search conversation.
    """
    message_ops = SearchMessageOperations(db)
    message = await message_ops.get_message_by_id(message_id)
    
    if not message:
        raise HTTPException(status_code=404, detail="Message not found")
    
    # Verify user has access to the search this message belongs to
    search_ops = ResearchOperations(db)
    search = await search_ops.get_search_by_id(message.search_id)
    
    if not search or (str(search["user_id"]) != str(current_user["id"]) and "admin" not in user_permissions):
        raise HTTPException(status_code=403, detail="Not authorized to access this message")
    
    return message


@router.get("/search/{search_id}", response_model=SearchMessageListResponse)
async def list_messages(
    search_id: UUID,
    limit: int = Query(100, ge=1, le=500, description="Maximum number of messages"),
    offset: int = Query(0, ge=0, description="Pagination offset"),
    current_user: dict = Depends(get_current_user),
    user_permissions: List[str] = Depends(get_user_permissions),
    db: AsyncSession = Depends(get_db)
):
    """
    List all messages for a specific search with pagination.
    
    Returns messages in sequence order (oldest first).
    """
    # Verify user has access to the search
    search_ops = ResearchOperations(db)
    search = await search_ops.get_search_by_id(search_id)
    
    if not search or (str(search["user_id"]) != str(current_user["id"]) and "admin" not in user_permissions):
        raise HTTPException(status_code=403, detail="Not authorized to access this search")
    
    # Get messages with pagination
    message_ops = SearchMessageOperations(db)
    return await message_ops.get_messages_list_response(search_id, limit, offset)


@router.patch("/{message_id}", response_model=SearchMessageResponse)
async def update_message(
    message_id: UUID,
    data: SearchMessageUpdate,
    current_user: dict = Depends(get_current_user),
    user_permissions: List[str] = Depends(get_user_permissions),
    db: AsyncSession = Depends(get_db)
):
    """
    Update a message's content.
    
    Note: This should generally be limited to user messages, not assistant responses.
    """
    # Verify message exists and user has access
    message_ops = SearchMessageOperations(db)
    message = await message_ops.get_message_by_id(message_id)
    
    if not message:
        raise HTTPException(status_code=404, detail="Message not found")
    
    # Verify user has access to the search this message belongs to
    search_ops = ResearchOperations(db)
    search = await search_ops.get_search_by_id(message.search_id)
    
    if not search or str(search["user_id"]) != str(current_user["id"]):
        raise HTTPException(status_code=403, detail="Not authorized to update this message")
    
    # Only allow updating user messages, not assistant responses
    if message.role != "user" and "admin" not in user_permissions:
        raise HTTPException(
            status_code=403,
            detail="Cannot update assistant messages"
        )
    
    # Update the message
    success = await message_ops.update_message(message_id, data.model_dump(exclude_unset=True))
    
    if not success:
        raise HTTPException(status_code=500, detail="Failed to update message")
    
    # Return updated message
    updated_message = await message_ops.get_message_by_id(message_id)
    return updated_message


@router.delete("/{message_id}", status_code=204)
async def delete_message(
    message_id: UUID,
    current_user: dict = Depends(get_current_user),
    user_permissions: List[str] = Depends(get_user_permissions),
    db: AsyncSession = Depends(get_db)
):
    """
    Delete a specific message.
    
    Note: This should be used with caution as it may break conversation flow.
    Admin privileges are required.
    """
    # Only admins can delete messages
    if "admin" not in user_permissions:
        raise HTTPException(
            status_code=403,
            detail="Admin privileges required to delete messages"
        )
    
    # Verify message exists
    message_ops = SearchMessageOperations(db)
    message = await message_ops.get_message_by_id(message_id)
    
    if not message:
        raise HTTPException(status_code=404, detail="Message not found")
    
    # Delete the message
    success = await message_ops.delete_message(message_id)
    
    if not success:
        raise HTTPException(status_code=500, detail="Failed to delete message")
    
    return None


@router.post("/{message_id}/forward")
async def forward_message(
    message_id: UUID,
    data: SearchMessageForwardRequest,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Forward a message to another destination (email, user, etc.).
    
    This endpoint handles the preparation of the message for forwarding.
    The actual delivery mechanism depends on the destination type.
    """
    # Verify message exists and user has access
    message_ops = SearchMessageOperations(db)
    message = await message_ops.get_message_by_id(message_id)
    
    if not message:
        raise HTTPException(status_code=404, detail="Message not found")
    
    # Verify user has access to the search this message belongs to
    search_ops = ResearchOperations(db)
    search = await search_ops.get_search_by_id(message.search_id)
    
    if not search or str(search["user_id"]) != str(current_user["id"]):
        raise HTTPException(status_code=403, detail="Not authorized to forward this message")
    
    # Format message for forwarding using domain model
    from models.domain.research.search_message import ResearchMessage
    message_domain = ResearchMessage(
        content=message.content,
        role=message.role,
        message_id=message.id,
        sequence=message.sequence
    )
    
    # Prepare forwarding data
    forward_data = message_domain.forward_message(
        destination=data.destination,
        destination_type=data.destination_type
    )
    
    # Here you would integrate with your messaging service based on destination_type
    # For now, we'll just return the formatted message
    return {
        "status": "success",
        "message": "Message prepared for forwarding",
        "formatted_message": message_domain.format_for_external_sharing(),
        "forward_data": forward_data
    }


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
    # Authenticate user from token
    try:
        user_data = decode_access_token(token)
        if not user_data:
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
            return
        user_id = user_data.get("sub")
    except Exception:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return
    
    # Verify user has access to the search
    search_ops = ResearchOperations(db)
    search = await search_ops.get_search_by_id(search_id)
    
    if not search or str(search["user_id"]) != str(user_id):
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return
    
    await websocket.accept()
    
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
    
    try:
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
                
                if command == "get_latest":
                    # Fetch latest messages
                    message_ops = SearchMessageOperations(db)
                    messages = await message_ops.list_messages_by_search(
                        search_id=search_id,
                        limit=data.get("limit", 10),
                        offset=data.get("offset", 0)
                    )
                    
                    # Convert to dict for JSON serialization
                    messages_data = [m.model_dump() for m in messages]
                    
                    await websocket.send_json({
                        "type": "messages",
                        "data": messages_data
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
        await websocket.close(code=status.WS_1011_INTERNAL_ERROR)
    finally:
        # Cancel the heartbeat task if it's still running
        if 'heartbeat_task' in locals() and not heartbeat_task.done():
            heartbeat_task.cancel()
            try:
                await heartbeat_task
            except asyncio.CancelledError:
                pass
