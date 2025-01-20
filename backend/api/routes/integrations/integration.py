# api/routes/integrations/integration.py

from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session
from models.schemas.integrations.integration import (
    IntegrationCreate,
    IntegrationRead,
    IntegrationUpdate,
    IntegrationWithRelations
)
from models.domain.integrations.operations_integration import IntegrationOperations
from core.database import get_session
from core.auth import get_current_user, require_super_admin

router = APIRouter(prefix="/integrations", tags=["integrations"])


@router.post("/", response_model=IntegrationRead)
async def create_integration(
    data: IntegrationCreate,
    session: Session = Depends(get_session),
    _: UUID = Depends(require_super_admin)  # Only super admins can create integrations
):
    """Create a new integration"""
    operations = IntegrationOperations(session)
    return await operations.create(data)


@router.get("/{integration_id}", response_model=IntegrationWithRelations)
async def get_integration(
    integration_id: UUID,
    session: Session = Depends(get_session),
    _: UUID = Depends(get_current_user)
):
    """Get integration details by ID"""
    operations = IntegrationOperations(session)
    integration = await operations.get(integration_id)
    if not integration:
        raise HTTPException(status_code=404, detail="Integration not found")
    return integration


@router.get("/", response_model=List[IntegrationRead])
async def list_integrations(
    skip: int = 0,
    limit: int = 100,
    active_only: bool = True,
    auth_type: Optional[str] = None,
    session: Session = Depends(get_session),
    _: UUID = Depends(get_current_user)
):
    """List all integrations with optional filtering"""
    operations = IntegrationOperations(session)
    return await operations.list(
        skip=skip,
        limit=limit,
        active_only=active_only,
        auth_type=auth_type
    )


@router.patch("/{integration_id}", response_model=IntegrationRead)
async def update_integration(
    integration_id: UUID,
    data: IntegrationUpdate,
    session: Session = Depends(get_session),
    _: UUID = Depends(require_super_admin)  # Only super admins can update integrations
):
    """Update an existing integration"""
    operations = IntegrationOperations(session)
    updated = await operations.update(integration_id, data)
    if not updated:
        raise HTTPException(status_code=404, detail="Integration not found")
    return updated


@router.delete("/{integration_id}")
async def deactivate_integration(
    integration_id: UUID,
    session: Session = Depends(get_session),
    _: UUID = Depends(require_super_admin)  # Only super admins can deactivate integrations
):
    """Deactivate an integration and its associated credentials"""
    operations = IntegrationOperations(session)
    success = await operations.deactivate(integration_id)
    if not success:
        raise HTTPException(status_code=404, detail="Integration not found")
    return {"status": "success", "message": "Integration deactivated"}