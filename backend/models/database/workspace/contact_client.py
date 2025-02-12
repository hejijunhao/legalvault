# models/database/workspace/contact_client.py

from datetime import datetime
from enum import Enum
from typing import Optional, List, TYPE_CHECKING
from sqlalchemy import Column, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlmodel import Field, SQLModel, Relationship, ForeignKey
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
            ForeignKey("enterprise_schema.contacts.contact_id", ondelete="CASCADE"),
            primary_key=True,
            nullable=False
        )
    )
    client_id: UUID = Field(
        default=None,
        sa_column=Column(
            ForeignKey("enterprise_schema.clients.client_id", ondelete="CASCADE"),
            primary_key=True,
            nullable=False
        )
    )

    # Additional metadata
    role: ContactRole = Field(
        default=ContactRole.OTHER,
        nullable=False,
        description="Role of the contact at the client"
    )
    department: Optional[str] = Field(
        max_length=100,
        nullable=True,
        description="Department within the client organization"
    )
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        nullable=False
    )
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        nullable=False
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

    # Linkages
    client: Optional["ClientBase"] = Relationship(
        back_populates="contact_client",
        sa_relationship_kwargs={
            "lazy": "selectin",
            "primaryjoin": "and_(ContactClientBase.client_id==ClientBase.client_id, ContactClientBase.__table__.schema==ClientBase.__table__.schema)"
        }
    )
    contact: Optional["ContactBase"] = Relationship(
        back_populates="contact_client",
        sa_relationship_kwargs={
            "lazy": "selectin",
            "primaryjoin": "and_(ContactClientBase.contact_id==ContactBase.contact_id, ContactClientBase.__table__.schema==ContactBase.__table__.schema)"
        }
    )

    model_config = {
        "arbitrary_types_allowed": True
    }


class ContactClientBlueprint(ContactClientBase):
    """
    Concrete implementation of ContactClientBase for the public schema blueprint.
    Serves as a reference for tenant-specific implementations.
    """
    __tablename__ = "contact_client_blueprint"
    __table_args__ = (
        Index("idx_contact_client_role", "role"),
        Index("idx_contact_client_created", "created_by"),
        {'schema': 'public'}
    )


class ContactClient(ContactClientBase):
    """
    Concrete implementation of ContactClientBase for enterprise schemas.
    """
    __tablename__ = "contact_clients"