# models/database/workspace/contact.py

from datetime import datetime
from enum import Enum
from typing import Optional, List
from sqlalchemy import text
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlmodel import Field, SQLModel, Index, Column, ForeignKey, Relationship
from .contact_client import ContactClient
from .contact_project import ContactProject


class ContactType(str, Enum):
    """Types of contacts"""
    INTERNAL = "internal"  # Within the organization
    CLIENT = "client"      # Client contact
    EXTERNAL = "external"  # External contact (neither internal nor client)


class ContactStatus(str, Enum):
    """Status options for contacts"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    ARCHIVED = "archived"


class Contact(SQLModel, table=True):
    """
    Represents a contact in the LegalVault system.
    Contains personal information and professional details.
    """
    __tablename__ = "contacts"

    # Table configuration
    __table_args__ = (
        Index("idx_contact_name", "first_name", "last_name"),
        Index("idx_contact_email", "email"),
        Index("idx_contact_type", "contact_type"),
        Index("idx_contact_status", "status"),
        Index("idx_contact_created", "created_by"),
        Index("idx_contact_modified", "modified_by", "updated_at")
    )

    model_config = {
        "arbitrary_types_allowed": True,
        "json_schema_extra": {
            "examples": [
                {
                    "first_name": "John",
                    "last_name": "Doe",
                    "email": "john.doe@example.com",
                    "contact_type": "external"
                }
            ]
        }
    }

    # Core Properties
    contact_id: UUID = Field(
        sa_column=Column(
            UUID(as_uuid=True),
            primary_key=True,
            server_default=text("gen_random_uuid()"),
            nullable=False
        ),
        description="Unique identifier for the contact"
    )
    
    # Personal Information
    first_name: str = Field(
        max_length=100,
        nullable=False,
        description="Contact's first name"
    )
    last_name: str = Field(
        max_length=100,
        nullable=False,
        description="Contact's last name"
    )
    email: str = Field(
        max_length=255,
        nullable=False,
        index=True,
        description="Primary email address"
    )
    phone: Optional[str] = Field(
        max_length=50,
        nullable=True,
        description="Primary phone number"
    )
    
    # Professional Information
    title: Optional[str] = Field(
        max_length=100,
        nullable=True,
        description="Professional title or role"
    )
    organization: Optional[str] = Field(
        max_length=255,
        nullable=True,
        description="Organization or company name"
    )
    contact_type: ContactType = Field(
        default=ContactType.EXTERNAL,
        nullable=False,
        description="Type of contact relationship"
    )
    status: ContactStatus = Field(
        default=ContactStatus.ACTIVE,
        nullable=False,
        description="Current contact status"
    )
    
    # Additional Information
    notes: Optional[str] = Field(
        nullable=True,
        description="Additional notes about the contact"
    )
    
    # Metadata
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        nullable=False,
        description="Timestamp when the contact was created"
    )
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        nullable=False,
        description="Timestamp when the contact was last updated"
    )
    created_by: UUID = Field(
        sa_column=Column(
            UUID(as_uuid=True),
            ForeignKey("users.id", ondelete="RESTRICT"),
            nullable=False
        ),
        description="User ID of contact creator"
    )
    modified_by: UUID = Field(
        sa_column=Column(
            UUID(as_uuid=True),
            ForeignKey("users.id", ondelete="RESTRICT"),
            nullable=False
        ),
        description="User ID of last modifier"
    )

    # Relationships
    clients: List["Client"] = Relationship(
        back_populates="contacts",
        link_model=ContactClient,
        sa_relationship_kwargs={"lazy": "selectin"}
    )

    projects: List["Project"] = Relationship(
        back_populates="contacts",
        link_model=ContactProject,
        sa_relationship_kwargs={"lazy": "selectin"}
    )

    def __repr__(self) -> str:
        """String representation of the Contact"""
        return f"Contact(id={self.contact_id}, name={self.first_name} {self.last_name})"