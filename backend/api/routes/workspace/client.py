# api/routes/workspace/client.py

from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session

from core.database import get_session
from models.database.workspace.client import ClientStatus, LegalEntityType
from models.schemas.workspace.client import (
    ClientCreate,
    ClientUpdate,
    ClientProfileUpdate,
    ClientTagsUpdate,
    ClientResponse,
    ClientListResponse
)
from services.workflow.workspace.client_workflow import ClientWorkflow
from core.auth import get_current_user, get_user_permissions

router = APIRouter(
    prefix="/workspace/clients",
    tags=["clients"]
)


@router.post("/", response_model=ClientResponse)
async def create_client(
    data: ClientCreate,
    current_user: UUID = Depends(get_current_user),
    user_permissions: List[str] = Depends(get_user_permissions),
    session: Session = Depends(get_session)
):
    """
    Create a new client.

    Creates a new client record with the provided details. Requires appropriate
    permissions to create clients.
    """
    workflow = ClientWorkflow(session)
    return await workflow.create_client(data, current_user, user_permissions)


@router.get("/{client_id}", response_model=ClientResponse)
async def get_client(
    client_id: UUID,
    current_user: UUID = Depends(get_current_user),
    user_permissions: List[str] = Depends(get_user_permissions),
    session: Session = Depends(get_session)
):
    """
    Get client details by ID.

    Retrieves detailed information about a specific client. Access to sensitive
    information is controlled by user permissions.
    """
    workflow = ClientWorkflow(session)
    return await workflow.get_client(client_id, current_user, user_permissions)


@router.get("/", response_model=List[ClientListResponse])
async def list_clients(
    status: Optional[ClientStatus] = Query(None, description="Filter by client status"),
    legal_entity_type: Optional[LegalEntityType] = Query(None, description="Filter by entity type"),
    tags: Optional[List[str]] = Query(None, description="Filter by tags"),
    current_user: UUID = Depends(get_current_user),
    user_permissions: List[str] = Depends(get_user_permissions),
    session: Session = Depends(get_session)
):
    """
    List all clients with optional filters.

    Retrieves a list of clients, optionally filtered by status, entity type,
    or tags. Returns a simplified view of client information.
    """
    workflow = ClientWorkflow(session)
    return await workflow.list_clients(
        current_user,
        user_permissions,
        status=status,
        legal_entity_type=legal_entity_type,
        tags=tags
    )


@router.get("/search/", response_model=List[ClientListResponse])
async def search_clients(
    q: str = Query(..., min_length=2, description="Search term"),
    limit: int = Query(10, ge=1, le=100, description="Maximum number of results"),
    current_user: UUID = Depends(get_current_user),
    user_permissions: List[str] = Depends(get_user_permissions),
    session: Session = Depends(get_session)
):
    """
    Search for clients.

    Searches for clients by name or other relevant fields. Returns a simplified
    view of matching client information.
    """
    workflow = ClientWorkflow(session)
    return await workflow.search_clients(q, current_user, user_permissions, limit)


@router.patch("/{client_id}", response_model=ClientResponse)
async def update_client(
    client_id: UUID,
    data: ClientUpdate,
    current_user: UUID = Depends(get_current_user),
    user_permissions: List[str] = Depends(get_user_permissions),
    session: Session = Depends(get_session)
):
    """
    Update client details.

    Updates the specified client information. Different aspects of the update
    may require different permissions.
    """
    workflow = ClientWorkflow(session)
    return await workflow.update_client(
        client_id,
        data,
        current_user,
        user_permissions
    )


@router.patch("/{client_id}/profile", response_model=ClientResponse)
async def update_client_profile(
    client_id: UUID,
    data: ClientProfileUpdate,
    current_user: UUID = Depends(get_current_user),
    user_permissions: List[str] = Depends(get_user_permissions),
    session: Session = Depends(get_session)
):
    """
    Update client profile.

    Updates the client's profile summary and related information.
    """
    workflow = ClientWorkflow(session)
    return await workflow.update_profile(
        client_id,
        data,
        current_user,
        user_permissions
    )


@router.patch("/{client_id}/tags", response_model=ClientResponse)
async def update_client_tags(
    client_id: UUID,
    data: ClientTagsUpdate,
    current_user: UUID = Depends(get_current_user),
    user_permissions: List[str] = Depends(get_user_permissions),
    session: Session = Depends(get_session)
):
    """
    Update client tags.

    Updates the list of tags associated with the client.
    """
    workflow = ClientWorkflow(session)
    return await workflow.update_tags(
        client_id,
        data,
        current_user,
        user_permissions
    )


@router.post("/{client_id}/deactivate", response_model=ClientResponse)
async def deactivate_client(
    client_id: UUID,
    current_user: UUID = Depends(get_current_user),
    user_permissions: List[str] = Depends(get_user_permissions),
    session: Session = Depends(get_session)
):
    """
    Deactivate a client.

    Marks a client as inactive. This requires specific permissions and may affect
    related operations.
    """
    workflow = ClientWorkflow(session)
    return await workflow.deactivate_client(
        client_id,
        current_user,
        user_permissions
    )


@router.post("/{client_id}/reactivate", response_model=ClientResponse)
async def reactivate_client(
    client_id: UUID,
    current_user: UUID = Depends(get_current_user),
    user_permissions: List[str] = Depends(get_user_permissions),
    session: Session = Depends(get_session)
):
    """
    Reactivate a client.

    Reactivates an inactive client. This requires specific permissions.
    """
    workflow = ClientWorkflow(session)
    return await workflow.reactivate_client(
        client_id,
        current_user,
        user_permissions
    )


@router.delete("/{client_id}")
async def delete_client(
    client_id: UUID,
    current_user: UUID = Depends(get_current_user),
    user_permissions: List[str] = Depends(get_user_permissions),
    session: Session = Depends(get_session)
):
    """
    Delete a client.

    Permanently deletes a client record. This is a high-impact operation that
    requires specific permissions.
    """
    workflow = ClientWorkflow(session)
    await workflow.delete_client(client_id, current_user, user_permissions)
    return {"status": "success", "message": "Client deleted"}


# Error Handlers
@router.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return {
        "status_code": exc.status_code,
        "detail": exc.detail
    }


@router.exception_handler(Exception)
async def general_exception_handler(request, exc):
    return {
        "status_code": 500,
        "detail": "Internal server error"
    }