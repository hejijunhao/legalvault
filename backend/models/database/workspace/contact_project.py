# models/database/workspace/contact_project.py

from datetime import datetime
from enum import Enum
from typing import Optional, TYPE_CHECKING
from sqlalchemy import Column, Index, Relationship
from sqlalchemy.dialects.postgresql import UUID
from sqlmodel import Field, SQLModel, ForeignKey
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


class ContactProjectBase(SQLModel, ABC):
    """
    Abstract base class for the many-to-many relationship between Contacts and Projects.
    Serves as a template for tenant-specific implementations.
    """
    __abstract__ = True

    __table_args__ = (
        Index("idx_contact_project_role", "role"),
        Index("idx_contact_project_created", "created_by"),
        {'schema': 'public'}
    )
    
    contact_id: UUID = Field(
        default=None,
        sa_column=Column(
            ForeignKey("{schema}.contacts.contact_id", ondelete="CASCADE"),
            primary_key=True,
            nullable=False
        )
    )
    project_id: UUID = Field(
        default=None,
        sa_column=Column(
            ForeignKey("{schema}.projects.project_id", ondelete="CASCADE"),
            primary_key=True,
            nullable=False
        )
    )

    # Additional metadata
    role: ProjectRole = Field(
        default=ProjectRole.OTHER,
        nullable=False,
        description="Role of the contact in the project"
    )
    start_date: Optional[datetime] = Field(
        nullable=True,
        description="When the contact joined the project"
    )
    end_date: Optional[datetime] = Field(
        nullable=True,
        description="When the contact left the project"
    )
    notes: Optional[str] = Field(
        nullable=True,
        description="Additional notes about the contact's role"
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

    model_config = {
        "arbitrary_types_allowed": True
    }

    # Relationships
    contact: Optional["ContactBase"] = Relationship(
        back_populates="contact_project",
        sa_relationship_kwargs={
            "lazy": "selectin",
            "primaryjoin": "and_(ContactProjectBase.contact_id==ContactBase.contact_id, "
                           "ContactProjectBase.__table__.schema==ContactBase.__table__.schema)"
        }
    )

    project: Optional["ProjectBase"] = Relationship(
        back_populates="contact_project",
        sa_relationship_kwargs={
            "lazy": "selectin",
            "primaryjoin": "and_(ContactProjectBase.project_id==ProjectBase.project_id, "
                           "ContactProjectBase.__table__.schema==ProjectBase.__table__.schema)"
        }
    )


class ContactProject(ContactProjectBase, table=True):
    """
    Concrete implementation of the ContactProjectBase template.
    Tenant-specific implementations should inherit from ContactProjectBase.
    """
    __tablename__ = "contact_projects"