# models/database/integrations/integration.py

from datetime import datetime
from typing import Dict, List, Optional, TYPE_CHECKING, Any
from uuid import UUID
from enum import Enum
from sqlmodel import Field, SQLModel, Relationship
from sqlalchemy import Column, JSON

if TYPE_CHECKING:
    from .credentials import Credentials
    from .integration_ability import IntegrationAbility

class AuthType(str, Enum):
    OAUTH2 = "oauth2"
    API_KEY = "api_key"
    BASIC = "basic"
    NONE = "none"

class Integration(SQLModel, table=True):
    __tablename__ = "integrations"

    integration_id: UUID = Field(
        default=None,
        primary_key=True,
        nullable=False,
        index=True
    )
    name: str = Field(unique=True, index=True)
    description: str
    auth_type: str
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    modified_at: datetime = Field(default_factory=datetime.utcnow)
    icon_url: Optional[str] = None
    api_version: str
    webhook_url: Optional[str] = None
    rate_limit: Optional[int] = None
    
    # JSON fields with proper Column definitions
    config: Dict[str, Any] = Field(
        default_factory=dict,
        sa_column=Column(JSON)
    )
    required_scopes: List[str] = Field(
        default_factory=list,
        sa_column=Column(JSON)
    )
    integration_metadata: Dict[str, Any] = Field(  # Renamed from metadata
        default_factory=dict,
        sa_column=Column(JSON)
    )

    credentials: List["Credentials"] = Relationship(back_populates="integration")
    abilities: List["IntegrationAbility"] = Relationship(back_populates="integration")

    class Config:
        schema_extra = {
            "example": {
                "name": "Gmail",
                "description": "Google Mail Integration",
                "auth_type": "oauth2",
                "config": {
                    "client_id": "your-client-id",
                    "auth_url": "https://accounts.google.com/o/oauth2/auth",
                    "token_url": "https://oauth2.googleapis.com/token",
                    "scopes": ["https://www.googleapis.com/auth/gmail.readonly"]
                },
                "api_version": "v1",
                "required_scopes": ["https://www.googleapis.com/auth/gmail.readonly"]
            }
        }