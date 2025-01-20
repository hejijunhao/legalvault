# models/schemas/integrations/credentials.py

from datetime import datetime
from typing import Dict, Optional
from uuid import UUID
from pydantic import BaseModel, Field


class CredentialsBase(BaseModel):
    """Base Credentials schema with common attributes"""
    integration_id: UUID
    credentials: Dict = Field(
        ...,
        description="Encrypted credentials for the integration"
    )
    metadata: Dict = Field(default={})


class CredentialsCreate(CredentialsBase):
    """Schema for creating new credentials"""
    expires_at: Optional[datetime] = None
    refresh_token: Optional[str] = None


class CredentialsUpdate(BaseModel):
    """Schema for updating existing credentials"""
    credentials: Optional[Dict] = None
    is_active: Optional[bool] = None
    expires_at: Optional[datetime] = None
    refresh_token: Optional[str] = None
    metadata: Optional[Dict] = None


class CredentialsRead(CredentialsBase):
    """Schema for reading credentials information"""
    credential_id: UUID
    user_id: UUID
    is_active: bool
    expires_at: Optional[datetime] = None
    created_at: datetime
    modified_at: datetime
    last_used_at: Optional[datetime] = None
    refresh_token: Optional[str] = None

    class Config:
        from_attributes = True


class CredentialsWithIntegration(CredentialsRead):
    """Schema for reading credentials with integration details"""
    integration_name: str
    integration_auth_type: str
    integration_icon_url: Optional[str] = None