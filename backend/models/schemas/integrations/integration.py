# models/schemas/integrations/integration.py

from datetime import datetime
from typing import Dict, List, Optional
from uuid import UUID
from pydantic import BaseModel, Field, HttpUrl
from models.database.integrations.integration import AuthType


class IntegrationBase(BaseModel):
    """Base Integration schema with common attributes"""
    name: str = Field(..., min_length=1, max_length=100)
    description: str
    auth_type: AuthType
    config: Dict = Field(default={})
    api_version: str = Field(..., min_length=1, max_length=20)
    webhook_url: Optional[HttpUrl] = None
    rate_limit: Optional[int] = None
    required_scopes: List[str] = Field(default=[])
    metadata: Dict = Field(default={})


class IntegrationCreate(IntegrationBase):
    """Schema for creating a new integration"""
    pass


class IntegrationUpdate(BaseModel):
    """Schema for updating an existing integration"""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None
    config: Optional[Dict] = None
    is_active: Optional[bool] = None
    api_version: Optional[str] = Field(None, min_length=1, max_length=20)
    webhook_url: Optional[HttpUrl] = None
    rate_limit: Optional[int] = None
    required_scopes: Optional[List[str]] = None
    metadata: Optional[Dict] = None


class IntegrationRead(IntegrationBase):
    """Schema for reading integration information"""
    integration_id: UUID
    is_active: bool
    created_at: datetime
    modified_at: datetime
    icon_url: Optional[HttpUrl] = None

    class Config:
        from_attributes = True


class IntegrationWithRelations(IntegrationRead):
    """Schema for reading integration with its relationships"""
    active_credentials_count: int = Field(default=0)
    total_abilities: int = Field(default=0)
    required_abilities: int = Field(default=0)