# models/database/workspace/contact_project.py

from datetime import datetime
from enum import Enum
from typing import Optional
from sqlalchemy import Column, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlmodel import Field, SQLModel, ForeignKey


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


class ContactProject(SQLModel, table=True):
    """
    Association table for the many-to-many relationship between Contacts and Projects.
    """
    __tablename__ = "contact_projects"

    __table_args__ = (
        {'schema': 'public'},
        Index("idx_contact_project_role", "role"),
        Index("idx_contact_project_created", "created_by")
    )
    
    contact_id: UUID = Field(
        default=None,
        sa_column=Column(
            ForeignKey("public.contacts.contact_id", ondelete="CASCADE"),
            primary_key=True,
            nullable=False
        )
    )
    project_id: UUID = Field(
        default=None,
        sa_column=Column(
            ForeignKey("public.projects.project_id", ondelete="CASCADE"),
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

    class Config:
        arbitrary_types_allowed = True