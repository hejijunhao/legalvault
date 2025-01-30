# models/database/workspace/contact_client.py

from datetime import datetime
from enum import Enum
from typing import Optional
from sqlalchemy import Column, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlmodel import Field, SQLModel, ForeignKey


class ContactRole(str, Enum):
    """Role of the contact at the client organization"""
    PRIMARY = "primary"          # Main point of contact
    SECONDARY = "secondary"      # Backup contact
    LEGAL = "legal"             # Legal representative
    TECHNICAL = "technical"      # Technical contact
    BILLING = "billing"         # Billing/Finance contact
    ADMINISTRATIVE = "administrative"  # Administrative contact
    OTHER = "other"             # Other role


class ContactClient(SQLModel, table=True):
    """
    Association table for the many-to-many relationship between Contacts and Clients.
    """
    __tablename__ = "contact_clients"

    __table_args__ = (
        {'schema': 'public'},
        Index("idx_contact_client_role", "role"),
        Index("idx_contact_client_created", "created_by")
    )
    
    contact_id: UUID = Field(
        default=None,
        sa_column=Column(
            ForeignKey("public.contacts.contact_id", ondelete="CASCADE"),
            primary_key=True,
            nullable=False
        )
    )
    client_id: UUID = Field(
        default=None,
        sa_column=Column(
            ForeignKey("public.clients.client_id", ondelete="CASCADE"),
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

    class Config:
        arbitrary_types_allowed = True