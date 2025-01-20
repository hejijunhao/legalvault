# api/routes/integrations/oauth.py

from typing import Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlmodel import Session
from models.domain.integrations.operations_integration import IntegrationOperations
from models.domain.integrations.operations_credentials import CredentialsOperations
from models.schemas.integrations.credentials import CredentialsCreate, CredentialsUpdate
from services.executors.integration_executor import IntegrationExecutor
from core.database import get_session
from core.auth import get_current_user

router = APIRouter(prefix="/oauth", tags=["oauth"])


@router.get("/authorize/{integration_id}")
async def start_oauth_flow(
    integration_id: UUID,
    session: Session = Depends(get_session),
    current_user: UUID = Depends(get_current_user)
):
    """Start OAuth flow for an integration"""
    # Get integration details
    int_ops = IntegrationOperations(session)
    integration = await int_ops.get(integration_id)
    if not integration:
        raise HTTPException(status_code=404, detail="Integration not found")
    
    if not integration.requires_oauth():
        raise HTTPException(
            status_code=400,
            detail="This integration does not use OAuth"
        )
    
    # Generate OAuth URL
    executor = IntegrationExecutor()
    auth_url = await executor.get_oauth_url(integration)
    
    return {
        "auth_url": auth_url,
        "integration_name": integration.name
    }


@router.get("/callback/{integration_id}")
async def oauth_callback(
    integration_id: UUID,
    code: str,
    state: Optional[str] = None,
    error: Optional[str] = None,
    session: Session = Depends(get_session),
    current_user: UUID = Depends(get_current_user)
):
    """Handle OAuth callback and create credentials"""
    if error:
        raise HTTPException(
            status_code=400,
            detail=f"OAuth error: {error}"
        )
    
    # Get integration details
    int_ops = IntegrationOperations(session)
    integration = await int_ops.get(integration_id)
    if not integration:
        raise HTTPException(status_code=404, detail="Integration not found")
    
    # Exchange code for tokens
    executor = IntegrationExecutor()
    token_response = await executor.exchange_oauth_code(
        integration=integration,
        code=code
    )
    
    # Create credentials
    cred_ops = CredentialsOperations(session)
    cred_data = CredentialsCreate(
        integration_id=integration_id,
        credentials=token_response.credentials,
        expires_at=token_response.expires_at,
        refresh_token=token_response.refresh_token
    )
    
    await cred_ops.create(cred_data, current_user)
    
    return {
        "status": "success",
        "message": f"Successfully connected to {integration.name}"
    }


@router.post("/refresh/{credential_id}")
async def refresh_oauth_token(
    credential_id: UUID,
    session: Session = Depends(get_session),
    current_user: UUID = Depends(get_current_user)
):
    """Refresh OAuth tokens for credentials"""
    # Get credentials
    cred_ops = CredentialsOperations(session)
    credentials = await cred_ops.get(credential_id)
    if not credentials:
        raise HTTPException(status_code=404, detail="Credentials not found")
    
    # Ensure user owns these credentials
    if credentials.user_id != current_user:
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Get integration details
    int_ops = IntegrationOperations(session)
    integration = await int_ops.get(credentials.integration_id)
    if not integration:
        raise HTTPException(status_code=404, detail="Integration not found")
    
    # Refresh tokens
    executor = IntegrationExecutor()
    token_response = await executor.refresh_oauth_token(
        integration=integration,
        refresh_token=credentials.refresh_token
    )
    
    # Update credentials
    update_data = CredentialsUpdate(
        credentials=token_response.credentials,
        expires_at=token_response.expires_at,
        refresh_token=token_response.refresh_token
    )
    
    await cred_ops.update(credential_id, update_data)
    
    return {
        "status": "success",
        "message": "OAuth tokens refreshed successfully"
    }