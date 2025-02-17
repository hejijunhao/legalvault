# models/database/workspace/contact_client.py

from datetime import datetime
from enum import Enum
from typing import Optional, List, TYPE_CHECKING
from sqlalchemy import Column, Index, String, DateTime
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlmodel import Field, SQLModel, Relationship, ForeignKey
from pydantic import validator
from abc import ABC

if TYPE_CHECKING:
    from .client import ClientBase
    from .contact import ContactBase

class ContactRole(str, Enum):
    """Role of the contact at the client organization"""
    PRIMARY = "primary"          # Main point of contact
    SECONDARY = "secondary"      # Backup contact
    LEGAL = "legal"             # Legal representative
    TECHNICAL = "technical"      # Technical contact
    BILLING = "billing"         # Billing/Finance contact
    ADMINISTRATIVE = "administrative"  # Administrative contact
    OTHER = "other"             # Other role

class ContactClientMetadata(SQLModel):
    """Additional metadata for contact-client relationship"""
    notes: str = Field(default="", description="Additional notes about the relationship")
    last_interaction: Optional[datetime] = Field(default=None)
    interaction_frequency: str = Field(default="as-needed")
    preferred_contact_method: str = Field(default="email")

class ContactClientBase(SQLModel, ABC):
    """
    Abstract base class for the many-to-many relationship between Contacts and Clients.
    Serves as a template for tenant-specific implementations.
    """
    __abstract__ = True

    __table_args__ = (
        Index("idx_contact_client_role", "role"),
        Index("idx_contact_client_created", "created_by")
    )
    
    contact_id: UUID = Field(
        default=None,
        sa_column=Column(
            ForeignKey("contacts.contact_id", ondelete="CASCADE"),
            primary_key=True,
            nullable=False
        )
    )
    client_id: UUID = Field(
        default=None,
        sa_column=Column(
            ForeignKey("clients.client_id", ondelete="CASCADE"),
            primary_key=True,
            nullable=False
        )
    )

    # Additional metadata
    role: str = Field(
        sa_column=Column(String, nullable=False),
        default=ContactRole.OTHER.value,
        description="Role of the contact at the client"
    )

    @validator("role")
    def validate_role(cls, v):
        if isinstance(v, ContactRole):
            return v.value
        if v not in [e.value for e in ContactRole]:
            raise ValueError(f"Invalid role: {v}")
        return v

    department: str = Field(
        sa_column=Column(String(100), nullable=True),
        description="Department within the client organization"
    )
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=Column(DateTime, nullable=False)
    )
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=Column(DateTime, nullable=False)
    )
    created_by: UUID = Field(
        sa_column=Column(
            ForeignKey("vault.users.id", ondelete="SET NULL"),
            nullable=True
        )
    )
    modified_by: UUID = Field(
        sa_column=Column(
            ForeignKey("vault.users.id", ondelete="SET NULL"),
            nullable=True
        )
    )

    contact_client_metadata: ContactClientMetadata = Field(
        sa_column=Column(JSONB, nullable=False),
        default_factory=ContactClientMetadata,
        description="Additional metadata about the contact-client relationship"
    )

    # Relationships
    contact: Optional["ContactBase"] = Relationship(
        back_populates="contact_client",
        sa_relationship_kwargs={
            "lazy": "selectin",
            "primaryjoin": "and_(foreign(ContactClientBase.contact_id)==ContactBase.contact_id, "
                           "ContactClientBase.__table__.schema==ContactBase.__table__.schema)",
            "cascade": "all, delete"
        }
    )
    client: Optional["ClientBase"] = Relationship(
        back_populates="contact_client",
        sa_relationship_kwargs={
            "lazy": "selectin",
            "primaryjoin": "and_(foreign(ContactClientBase.client_id)==ClientBase.client_id, "
                           "ContactClientBase.__table__.schema==ClientBase.__table__.schema)",
            "cascade": "all, delete"
        }
    )

    model_config = {
        "arbitrary_types_allowed": True
    }

class ContactClientBlueprint(ContactClientBase, table=True):
    """
    Concrete implementation of ContactClientBase for the public schema blueprint.
    Serves as a reference for tenant-specific implementations.
    """
    __tablename__ = "contact_client"
    __table_args__ = (
        *ContactClientBase.__table_args__,
        {'schema': 'public'}
    )
