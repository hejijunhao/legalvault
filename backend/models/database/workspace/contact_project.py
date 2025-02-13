# models/database/workspace/contact_project.py

from datetime import datetime
from enum import Enum
from typing import Optional, List, TYPE_CHECKING
from sqlalchemy import Column, Index, String, DateTime, JSONB
from sqlalchemy.dialects.postgresql import UUID
from sqlmodel import Field, SQLModel, Relationship, ForeignKey
from pydantic import validator
from abc import ABC

if TYPE_CHECKING:
    from .contact import ContactBase
    from .project import ProjectBase

class ProjectRole(str, Enum):
    """Role of the contact in the project"""
    LEAD = "lead"              # Project lead/manager
    ATTORNEY = "attorney"      # Legal counsel
    PARALEGAL = "paralegal"    # Paralegal support
    CONSULTANT = "consultant"  # External consultant
    EXPERT = "expert"         # Subject matter expert
    REVIEWER = "reviewer"     # Document/case reviewer
    SUPPORT = "support"       # Administrative support
    OTHER = "other"          # Other project role


class ContactProjectMetadata(SQLModel):
    """Additional metadata for contact-project relationship"""
    notes: str = Field(default="", description="Additional notes about the contact's role")
    hours_allocated: Optional[int] = Field(default=None)
    responsibilities: list[str] = Field(default_factory=list)
    expertise_areas: list[str] = Field(default_factory=list)


class ContactProjectBase(SQLModel, ABC):
    """
    Abstract base class for the many-to-many relationship between Contacts and Projects.
    Serves as a template for tenant-specific implementations.
    """
    __abstract__ = True

    __table_args__ = (
        Index("idx_contact_project_role", "role"),
        Index("idx_contact_project_created", "created_by")
    )
    
    contact_id: UUID = Field(
        default=None,
        sa_column=Column(
            ForeignKey("enterprise_schema.contacts.contact_id", ondelete="CASCADE"),
            primary_key=True,
            nullable=False
        )
    )
    project_id: UUID = Field(
        default=None,
        sa_column=Column(
            ForeignKey("enterprise_schema.projects.project_id", ondelete="CASCADE"),
            primary_key=True,
            nullable=False
        )
    )

    # Additional metadata
    role: str = Field(
        sa_column=Column(String, nullable=False),
        default=ProjectRole.OTHER.value,
        description="Role of the contact in the project"
    )

    @validator("role")
    def validate_role(cls, v):
        if isinstance(v, ProjectRole):
            return v.value
        if v not in [e.value for e in ProjectRole]:
            raise ValueError(f"Invalid role: {v}")
        return v

    start_date: Optional[datetime] = Field(
        sa_column=Column(DateTime, nullable=True),
        description="When the contact joined the project"
    )
    
    end_date: Optional[datetime] = Field(
        sa_column=Column(DateTime, nullable=True),
        description="When the contact left the project"
    )
    
    metadata: ContactProjectMetadata = Field(
        sa_column=Column(JSONB, nullable=False),
        default_factory=ContactProjectMetadata,
        description="Additional metadata about the contact's role in the project"
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

    model_config = {
        "arbitrary_types_allowed": True
    }

    # Relationships
    _contact: Optional["ContactBase"] = Relationship(
        back_populates="_contact_project",
        sa_relationship_kwargs={
            "lazy": "selectin",
            "primaryjoin": "and_(foreign(ContactProjectBase.contact_id)==ContactBase.contact_id, ContactProjectBase.__table__.schema==ContactBase.__table__.schema)"
        }
    )

    _project: Optional["ProjectBase"] = Relationship(
        back_populates="_contact_project",
        sa_relationship_kwargs={
            "lazy": "selectin",
            "primaryjoin": "and_(foreign(ContactProjectBase.project_id)==ProjectBase.project_id, ContactProjectBase.__table__.schema==ProjectBase.__table__.schema)"
        }
    )


class ContactProjectBlueprint(ContactProjectBase, table=True):
    """
    Concrete implementation of ContactProjectBase for the public schema blueprint.
    Serves as a reference for tenant-specific implementations.
    """
    __tablename__ = "contact_project_blueprint"
    __table_args__ = (
        Index("idx_contact_project_role", "role"),
        Index("idx_contact_project_created", "created_by"),
        {'schema': 'public'}
    )


class ContactProject(ContactProjectBase):
    """
    Concrete implementation of ContactProjectBase for enterprise schemas.
    """
    __tablename__ = "contact_projects"