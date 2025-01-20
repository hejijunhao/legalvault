# models/database/integrations/credentials.py

from datetime import datetime
from typing import Dict, Optional, Any
from uuid import UUID
from sqlmodel import Field, SQLModel, Relationship
from sqlalchemy import Column
from sqlalchemy.dialects.postgresql import JSONB
from .integration import Integration

class Credentials(SQLModel, table=True):
    __tablename__ = "credentials"

    credential_id: UUID = Field(
        default=None,
        primary_key=True,
        nullable=False,
        index=True
    )
    user_id: UUID = Field(
        foreign_key="users.id",
        index=True,
        nullable=False
    )
    integration_id: UUID = Field(
        foreign_key="integrations.integration_id",
        index=True,
        nullable=False
    )
    # Encrypted credentials stored as JSON
    credentials: Dict[str, Any] = Field(
        default_factory=dict,
        sa_column=Column(JSONB),
        description="Encrypted credentials for the integration"
    )
    is_active: bool = Field(default=True)
    expires_at: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    modified_at: datetime = Field(default_factory=datetime.utcnow)
    last_used_at: Optional[datetime] = None
    refresh_token: Optional[str] = Field(
        default=None,
        description="OAuth2 refresh token if applicable"
    )
    credentials_metadata: Dict = Field(
        default={},
        sa_column=Column(JSONB),
        description="Additional integration-specific metadata"
    )

    integration: Integration = Relationship(back_populates="credentials")

    class Config:
        schema_extra = {
            "example": {
                "credentials": {
                    "access_token": "encrypted_access_token",
                    "token_type": "Bearer",
                    "scope": "read write"
                },
                "metadata": {
                    "account_email": "user@example.com",
                    "account_id": "12345"
                }
            }
        }