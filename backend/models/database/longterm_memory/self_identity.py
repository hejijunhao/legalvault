# models/database/longterm_memory/self_identity.py

from sqlmodel import SQLModel, Field, Index
from sqlalchemy import TIMESTAMP, Column, Text, ForeignKey
from typing import Optional
from datetime import datetime
from uuid import uuid4
from sqlalchemy.dialects.postgresql import UUID
from abc import ABC


class SelfIdentityBase(SQLModel, ABC):
    """
    Abstract base class representing a VP's self-identity in the LegalVault system.
    Serves as a template for tenant-specific self-identity implementations.
    Contains core attributes, capabilities, personality traits, and working preferences.
    """
    __abstract__ = True

    __table_args__ = (
        Index("ix_self_identity_vp_id", "vp_id"),
        Index("ix_self_identity_last_updated", "last_updated"),
        {'schema': 'public'}
    )

    model_config = {
        "arbitrary_types_allowed": True,
        "json_schema_extra": {
            "examples": [
                {
                    "prompt": "Core identity attributes and personality traits..."
                }
            ]
        }
    }

    # Core Properties
    id: UUID = Field(
        default_factory=uuid4,
        primary_key=True,
        description="Unique identifier for the self-identity record"
    )
    vp_id: UUID = Field(
        sa_column=Column(
            UUID(as_uuid=True),
            ForeignKey("vault.virtual_paralegals.id"),
            nullable=False
        ),
        description="Foreign key to the Virtual Paralegal"
    )

    # Identity Content
    prompt: str = Field(
        sa_column=Column(Text),
        description="Self-identity system prompt containing core attributes and traits"
    )

    # Metadata
    last_updated: datetime = Field(
        sa_column=Column(TIMESTAMP(timezone=True)),
        default_factory=datetime.utcnow,
        description="Timestamp of last update"
    )

    def __repr__(self) -> str:
        """String representation of the Self Identity"""
        return f"SelfIdentity(id={self.id}, vp_id={self.vp_id})"


class SelfIdentity(SelfIdentityBase):
    """
    Concrete implementation of the SelfIdentityBase template.
    Tenant-specific implementations should inherit from SelfIdentityBase.
    """
    __tablename__ = "longterm_memory_self_identity"