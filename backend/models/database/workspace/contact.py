# models/database/workspace/contact.py

from datetime import datetime
from enum import Enum
from typing import Optional, List, TYPE_CHECKING
from sqlalchemy import text, String, ARRAY, JSONB, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlmodel import Field, SQLModel, Index, Column, ForeignKey, Relationship
from abc import ABC

if TYPE_CHECKING:
    from .project import ProjectBase
    from .client import ClientBase
    from .contact_client import ContactClientBase
    from .contact_project import ContactProjectBase

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


class ContactMetadata(SQLModel):
    """Contact metadata and additional information"""
    notes: str = Field(default="", description="Additional notes about the contact")
    last_interaction: Optional[datetime] = Field(default=None)
    preferred_language: str = Field(default="en")
    timezone: str = Field(default="UTC")
    communication_preferences: dict = Field(
        default_factory=lambda: {
            "email": True,
            "phone": True,
            "mail": False
        }
    )


class ContactBase(SQLModel, ABC):
    """
    Abstract base class representing a contact in the LegalVault system.
    Serves as a template for tenant-specific contact implementations.
    Contains personal information and professional details.
    """
    __abstract__ = True

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
        sa_column=Column(String(100), nullable=False),
        description="Contact's first name"
    )
    last_name: str = Field(
        sa_column=Column(String(100), nullable=False),
        description="Contact's last name"
    )
    email: str = Field(
        sa_column=Column(String(255), nullable=False, index=True),
        description="Primary email address"
    )
    phone: Optional[str] = Field(
        sa_column=Column(String(50), nullable=True),
        description="Primary phone number"
    )
    
    # Professional Information
    title: Optional[str] = Field(
        sa_column=Column(String(100), nullable=True),
        description="Professional title or role"
    )
    organization: Optional[str] = Field(
        sa_column=Column(String(255), nullable=True),
        description="Organization or company name"
    )
    contact_type: str = Field(
        sa_column=Column(String, nullable=False),
        default=ContactType.EXTERNAL.value,
        description="Type of contact (internal, client, or external)"
    )
    status: str = Field(
        sa_column=Column(String, nullable=False),
        default=ContactStatus.ACTIVE.value,
        description="Current status of the contact"
    )
    
    # Additional Information
    metadata: ContactMetadata = Field(
        sa_column=Column(JSONB, nullable=False),
        default_factory=ContactMetadata,
        description="Additional contact metadata and preferences"
    )
    tags: list[str] = Field(
        sa_column=Column(ARRAY(String), nullable=False, default=list),
        description="Contact tags for categorization"
    )
    
    # Metadata
    created_at: datetime = Field(
        sa_column=Column(DateTime, nullable=False),
        default_factory=datetime.utcnow,
        description="When the contact was created"
    )
    updated_at: datetime = Field(
        sa_column=Column(DateTime, nullable=False),
        default_factory=datetime.utcnow,
        description="When the contact was last updated"
    )
    birth_date: Optional[datetime] = Field(
        sa_column=Column(DateTime, nullable=True),
        description="Contact's date of birth"
    )
    created_by: UUID = Field(
        sa_column=Column(
            UUID(as_uuid=True),
            ForeignKey("enterprise_schema.users.id", ondelete="RESTRICT"),
            nullable=False
        ),
        description="User ID of contact creator"
    )
    modified_by: UUID = Field(
        sa_column=Column(
            UUID(as_uuid=True),
            ForeignKey("enterprise_schema.users.id", ondelete="RESTRICT"),
            nullable=False
        ),
        description="User ID of last modifier"
    )

    # Relationships
    client: Optional[List["ClientBase"]] = None
    project: Optional[List["ProjectBase"]] = None
    contact_client: Optional[List["ContactClientBase"]] = None
    contact_project: Optional[List["ContactProjectBase"]] = None

    _client = Relationship(
        back_populates="contact",
        link_model="ContactClientBase",
        sa_relationship_kwargs={
            "lazy": "selectin",
            "cascade": "all",
            "primaryjoin": "and_(foreign(ContactBase.contact_id)==ContactClientBase.contact_id, ContactBase.__table__.schema==ContactClientBase.__table__.schema)",
            "secondaryjoin": "and_(ContactClientBase.client_id==ClientBase.client_id, ContactClientBase.__table__.schema==ClientBase.__table__.schema)"
        }
    )
    _project = Relationship(
        back_populates="contact",
        link_model="ContactProjectBase",
        sa_relationship_kwargs={
            "lazy": "selectin",
            "cascade": "all",
            "primaryjoin": "and_(foreign(ContactBase.contact_id)==ContactProjectBase.contact_id, ContactBase.__table__.schema==ContactProjectBase.__table__.schema)",
            "secondaryjoin": "and_(ContactProjectBase.project_id==ProjectBase.project_id, ContactProjectBase.__table__.schema==ProjectBase.__table__.schema)"
        }
    )
    _contact_client = Relationship(
        back_populates="contact",
        sa_relationship_kwargs={
            "cascade": "all, delete-orphan",
            "lazy": "selectin",
            "primaryjoin": "and_(foreign(ContactBase.contact_id)==ContactClientBase.contact_id, ContactBase.__table__.schema==ContactClientBase.__table__.schema)"
        }
    )
    _contact_project = Relationship(
        back_populates="contact",
        sa_relationship_kwargs={
            "cascade": "all, delete-orphan",
            "lazy": "selectin",
            "primaryjoin": "and_(foreign(ContactBase.contact_id)==ContactProjectBase.contact_id, ContactBase.__table__.schema==ContactProjectBase.__table__.schema)"
        }
    )

    def __repr__(self) -> str:
        """String representation of the Contact"""
        return f"Contact(id={self.contact_id}, name={self.first_name} {self.last_name})"


class ContactBlueprint(ContactBase, table=True):
    """
    Concrete implementation of ContactBase for the public schema blueprint.
    Serves as a reference for tenant-specific implementations.
    """
    __tablename__ = "contact_blueprint"
    __table_args__ = (
        Index("idx_contact_name", "first_name", "last_name"),
        Index("idx_contact_email", "email"),
        Index("idx_contact_created_by", "created_by"),
        Index("idx_contact_modified", "modified_by", "updated_at"),
        {'schema': 'public'}
    )


class Contact(ContactBase):
    """
    Concrete implementation of ContactBase for enterprise schemas.
    """
    __tablename__ = "contacts"