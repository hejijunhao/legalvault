# api/routes/integrations/credentials.py

from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session
from models.schemas.integrations.credentials import (
    CredentialsCreate,
    CredentialsRead,
    CredentialsUpdate,
    CredentialsWithIntegration
)
from models.domain.integrations.operations_credentials import CredentialsOperations
from core.database import get_session
from core.auth import get_current_user

router = APIRouter(prefix="/integration-credentials", tags=["integration-credentials"])


@router.post("/", response_model=CredentialsRead)
async def create_credentials(
    data: CredentialsCreate,
    session: Session = Depends(get_session),
    current_user: UUID = Depends(get_current_user)
):
    """Create new integration credentials for the current user"""
    operations = CredentialsOperations(session)
    return await operations.create(data, current_user)


@router.get("/me", response_model=List[CredentialsWithIntegration])
async def list_my_credentials(
    skip: int = 0,
    limit: int = 100,
    active_only: bool = True,
    session: Session = Depends(get_session),
    current_user: UUID = Depends(get_current_user)
):
    """List all credentials for the current user"""
    operations = CredentialsOperations(session)
    return await operations.list_for_user(
        user_id=current_user,
        skip=skip,
        limit=limit,
        active_only=active_only
    )


@router.get("/{credential_id}", response_model=CredentialsWithIntegration)
async def get_credentials(
    credential_id: UUID,
    session: Session = Depends(get_session),
    current_user: UUID = Depends(get_current_user)
):
    """Get credentials by ID"""
    operations = CredentialsOperations(session)
    credentials = await operations.get(credential_id)
    if not credentials:
        raise HTTPException(status_code=404, detail="Credentials not found")
    # Ensure user can only access their own credentials
    if credentials.user_id != current_user:
        raise HTTPException(status_code=403, detail="Access denied")
    return credentials


@router.patch("/{credential_id}", response_model=CredentialsRead)
async def update_credentials(
    credential_id: UUID,
    data: CredentialsUpdate,
    session: Session = Depends(get_session),
    current_user: UUID = Depends(get_current_user)
):
    """Update existing credentials"""
    operations = CredentialsOperations(session)
    # First check if credentials exist and belong to user
    existing = await operations.get(credential_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Credentials not found")
    if existing.user_id != current_user:
        raise HTTPException(status_code=403, detail="Access denied")
    
    updated = await operations.update(credential_id, data)
    return updated


@router.delete("/{credential_id}")
async def deactivate_credentials(
    credential_id: UUID,
    session: Session = Depends(get_session),
    current_user: UUID = Depends(get_current_user)
):
    """Deactivate credentials"""
    operations = CredentialsOperations(session)
    # First check if credentials exist and belong to user
    existing = await operations.get(credential_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Credentials not found")
    if existing.user_id != current_user:
        raise HTTPException(status_code=403, detail="Access denied")
    
    success = await operations.deactivate(credential_id)
    return {"status": "success", "message": "Credentials deactivated"}