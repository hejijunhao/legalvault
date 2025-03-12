# api/routes/research/search_message.py

from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, WebSocket, WebSocketDisconnect, status
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db
from core.auth import get_current_user, get_user_permissions, decode_access_token
from models.domain.research.search_operations import ResearchOperations
from models.domain.research.search_message_operations import SearchMessageOperations
from models.schemas.research.search_message import (
    MessageResponse,
    MessageUpdate,
    MessageListResponse,
    MessageForwardRequest
)

router = APIRouter(
    prefix="/research/messages",
    tags=["research"]
)


@router.get("/{message_id}", response_model=MessageResponse)
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
    search = await search_ops.get_search_by_id(message["search_id"])
    
    if not search or (str(search["user_id"]) != str(current_user["id"]) and "admin" not in user_permissions):
        raise HTTPException(status_code=403, detail="Not authorized to access this message")
    
    return message


@router.get("/search/{search_id}", response_model=MessageListResponse)
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
    
    # Get messages
    message_ops = SearchMessageOperations(db)
    messages = await message_ops.list_messages_by_search(search_id, limit, offset)
    
    # Get total count for pagination using the optimized count method
    total = await message_ops.count_messages_by_search(search_id)
    
    return {
        "items": messages,
        "total": total,
        "offset": offset,
        "limit": limit
    }


@router.patch("/{message_id}", response_model=MessageResponse)
async def update_message(
    message_id: UUID,
    data: MessageUpdate,
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
    search = await search_ops.get_search_by_id(message["search_id"])
    
    if not search or str(search["user_id"]) != str(current_user["id"]):
        raise HTTPException(status_code=403, detail="Not authorized to update this message")
    
    # Only allow updating user messages, not assistant responses
    if message["role"] != "user" and "admin" not in user_permissions:
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
    data: MessageForwardRequest,
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
    search = await search_ops.get_search_by_id(message["search_id"])
    
    if not search or str(search["user_id"]) != str(current_user["id"]):
        raise HTTPException(status_code=403, detail="Not authorized to forward this message")
    
    # Format message for forwarding using domain model
    from models.domain.research.search_message import ResearchMessage
    message_domain = ResearchMessage(
        content=message["content"],
        role=message["role"],
        message_id=message_id
    )
    
    formatted_message = message_domain.format_for_external_sharing()
    
    # Here you would implement the actual forwarding logic based on destination_type
    # This is a placeholder that would be replaced with actual implementation
    if data.destination_type == "email":
        # Send email logic would go here
        return {"status": "success", "message": "Message forwarded to email", "formatted_content": formatted_message}
    elif data.destination_type == "user":
        # Forward to another user logic would go here
        return {"status": "success", "message": "Message forwarded to user", "formatted_content": formatted_message}
    elif data.destination_type == "whatsapp":
        # WhatsApp integration would go here
        return {"status": "success", "message": "Message forwarded to WhatsApp", "formatted_content": formatted_message}
    elif data.destination_type == "slack":
        # Slack integration would go here
        return {"status": "success", "message": "Message forwarded to Slack", "formatted_content": formatted_message}
    
    # This shouldn't be reached due to Pydantic validation
    raise HTTPException(status_code=400, detail="Invalid destination type")


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
    """
    # Authenticate user from token
    try:
        payload = decode_access_token(token)
        user_id = payload.get("sub")
        if not user_id:
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
            return
        
        # Get user enterprise_id from token if available
        user_enterprise_id = payload.get("enterprise_id")
    except Exception as e:
        print(f"WebSocket authentication error: {str(e)}")
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return
    
    # Verify user has access to the search
    search_ops = ResearchOperations(db)
    search = await search_ops.get_search_by_id(search_id)
    
    if not search:
        await websocket.close(code=status.WS_1003_UNSUPPORTED_DATA)
        return
    
    # Verify user owns the search
    if str(search["user_id"]) != str(user_id):
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return
    
    # Verify enterprise match if we have enterprise_id from token
    if user_enterprise_id and str(search["enterprise_id"]) != str(user_enterprise_id):
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return
    
    await websocket.accept()
    
    try:
        # Send initial connection confirmation
        await websocket.send_json({
            "type": "connection_established",
            "search_id": str(search_id)
        })
        
        # In a production implementation, you would set up a background task
        # to watch for new messages and send them to the client
        # For example, using Supabase's real-time features or a message queue
        
        # Simple message handling loop
        while True:
            data = await websocket.receive_json()
            command = data.get("command")
            
            if command == "subscribe":
                # Handle subscription to specific message types
                # This is a placeholder for actual subscription logic
                message_type = data.get("message_type", "all")
                await websocket.send_json({
                    "type": "subscription_confirmed",
                    "message_type": message_type
                })
            
            elif command == "typing":
                # Handle typing indicators
                # In a real implementation, this would broadcast to other connected clients
                is_typing = data.get("is_typing", False)
                await websocket.send_json({
                    "type": "typing_acknowledged",
                    "is_typing": is_typing
                })
    
    except WebSocketDisconnect:
        # Handle disconnect gracefully
        # In a real implementation, you would clean up any subscriptions
        print(f"WebSocket disconnected for search {search_id} and user {user_id}")
        pass
    except Exception as e:
        print(f"WebSocket error: {str(e)}")
        await websocket.close(code=status.WS_1011_INTERNAL_ERROR)




