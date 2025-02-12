# models/database/library/collections.py

from datetime import datetime
from typing import Dict, Any, Optional
from uuid import UUID, uuid4
from sqlmodel import Field, SQLModel
from sqlalchemy import Column, Index, ForeignKey
from sqlalchemy.dialects.postgresql import UUID as SQLAlchemyUUID, JSONB
from enum import Enum
from abc import ABC

class CollectionType(str, Enum):
    """Enumeration of possible collection types."""
    CLAUSEBANK = "clausebank"
    CUSTOM = "custom"
    TEMPLATE = "template"
    PRECEDENT = "precedent"
    RESEARCH = "research"

class CollectionBase(SQLModel, ABC):
    """
    Abstract base class representing a collection in the LegalVault system.
    Serves as a template for tenant-specific collection implementations.
    Contains metadata and organization for document collections.
    """
    __abstract__ = True

    __table_args__ = (
        Index("ix_collections_owner_id", "owner_id"),
        Index("ix_collections_name", "name"),
        Index("ix_collections_type", "collection_type")
    )

    model_config = {
        "arbitrary_types_allowed": True,
        "json_schema_extra": {
            "example": {
                "name": "Sample Collection",
                "description": "A sample collection for demonstration",
                "collection_type": "Custom",
                "collection_metadata": {"key": "value"}
            }
        }
    }

    # Core Properties
    id: UUID = Field(
        default_factory=uuid4,
        primary_key=True,
        nullable=False,
        sa_type=SQLAlchemyUUID
    )
    name: str = Field(
        description="Name of the collection"
    )
    description: Optional[str] = Field(
        default=None,
        description="Optional description of the collection"
    )
    owner_id: UUID = Field(
        sa_column=Column(
            "owner_id",
            SQLAlchemyUUID,
            ForeignKey("vault.users.id", ondelete="CASCADE"),
            nullable=False
        ),
        description="User ID of the collection owner"
    )
    is_default: bool = Field(
        default=False,
        description="Whether this is a default collection"
    )
    collection_type: CollectionType = Field(
        description="Type of collection"
    )
    collection_metadata: Dict[str, Any] = Field(
        default_factory=dict,
        sa_column=Column(JSONB),
        description="Additional metadata for the collection"
    )

    # Timestamps
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        nullable=False,
        sa_column_kwargs={"server_default": "now()"},
        description="Timestamp when the collection was created"
    )
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        nullable=False,
        sa_column_kwargs={"server_default": "now()", "onupdate": "now()"},
        description="Timestamp when the collection was last updated"
    )

    def __repr__(self) -> str:
        """String representation of the Collection"""
        return f"Collection(id={self.id}, name={self.name}, type={self.collection_type})"


class CollectionBlueprint(CollectionBase):
    """
    Concrete implementation of CollectionBase for the public schema blueprint.
    Serves as a reference for tenant-specific implementations.
    """
    __tablename__ = "collections_blueprint"
    __table_args__ = (
        Index("ix_collections_owner_id", "owner_id"),
        Index("ix_collections_name", "name"),
        Index("ix_collections_type", "collection_type"),
        {'schema': 'public'}
    )


class Collection(CollectionBase):
    """
    Concrete implementation of CollectionBase for enterprise schemas.
    """
    __tablename__ = "collections"