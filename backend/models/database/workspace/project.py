# models/database/workspace/project.py

from datetime import datetime
from enum import Enum
from typing import List, Optional
from sqlalchemy import text
from sqlalchemy.dialects.postgresql import UUID
from sqlmodel import Field, SQLModel, JSON, Column, UniqueConstraint, Index, ForeignKey, Relationship
from .project_client import ProjectClient


class ProjectStatus(str, Enum):
    ACTIVE = "active"
    COMPLETED = "completed"
    ARCHIVED = "archived"


class ConfidentialityLevel(str, Enum):
    PUBLIC = "public"
    CONFIDENTIAL = "confidential"


class ProjectKnowledge(SQLModel):
    """
    Represents the synthesized knowledge about a project, combining LLM-generated insights
    and manual user input in rich text format.
    """
    content: str  # Rich text content containing project knowledge
    last_updated: datetime


class Project(SQLModel, table=True):
    """
    Represents a project in the LegalVault system.
    Contains core properties, metadata, and synthesized project knowledge.
    """
    __tablename__ = "projects"

    # Table configuration
    __table_args__ = (
        {'schema': 'public'},
        UniqueConstraint("name", name="uq_project_name"),
        Index("idx_project_status_practice", "status", "practice_area"),
        Index("idx_project_created_by", "created_by"),
        Index("idx_project_modified", "modified_by", "updated_at"),
        Index("idx_project_tasks", "project_id"),
    )

    model_config = {
        "arbitrary_types_allowed": True,
        "json_schema_extra": {
            "examples": [
                {
                    "name": "Example Project",
                    "status": "active",
                    "practice_area": "Corporate Law"
                }
            ]
        }
    }

    # Core Properties
    project_id: UUID = Field(
        sa_column=Column(
            UUID(as_uuid=True),
            primary_key=True,
            server_default=text("gen_random_uuid()"),
            nullable=False
        ),
        description="Unique identifier for the project"
    )
    name: str = Field(
        max_length=255,
        index=True,
        nullable=False,
        description="Name of the project"
    )
    status: ProjectStatus = Field(
        default=ProjectStatus.ACTIVE,
        nullable=False,
        index=True,
        description="Current status of the project"
    )
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        nullable=False,
        description="Timestamp when the project was created"
    )
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        nullable=False,
        index=True,
        description="Timestamp when the project was last updated"
    )
    created_by: UUID = Field(
        sa_column=Column(
            UUID(as_uuid=True),
            ForeignKey("vault.users.id", ondelete="RESTRICT"),
            nullable=False
        ),
        description="User ID of project creator"
    )
    modified_by: UUID = Field(
        sa_column=Column(
            UUID(as_uuid=True),
            ForeignKey("vault.users.id", ondelete="RESTRICT"),
            nullable=False
        ),
        description="User ID of last modifier"
    )

    # Metadata
    practice_area: str = Field(
        max_length=100,
        nullable=True,
        index=True,
        description="Area of legal practice this project belongs to"
    )
    confidentiality: ConfidentialityLevel = Field(
        default=ConfidentialityLevel.CONFIDENTIAL,
        nullable=False,
        description="Confidentiality level of the project"
    )
    start_date: datetime = Field(
        nullable=True,
        index=True,
        description="Project start date"
    )
    tags: List[str] = Field(
        sa_column=Column(JSON),
        default=[],
        description="List of tags associated with the project"
    )

    # Project Knowledge and Summary
    knowledge: ProjectKnowledge = Field(
        sa_column=Column(JSON),
        default=None,
        description="Synthesized project knowledge combining LLM insights and user input in rich text format"
    )
    summary: str = Field(
        max_length=2000,  # Match schema validation
        nullable=True,
        description="Condensed project summary for LLM context and quick reference"
    )
    summary_updated_at: datetime = Field(
        nullable=True,
        description="Timestamp when the project summary was last updated"
    )

    # Relationships
    notebook: Optional["Notebook"] = Relationship(
        back_populates="project",
        sa_relationship_kwargs={
            "uselist": False,  # One-to-one relationship
            "cascade": "all, delete-orphan",  # Cascade deletion
            "lazy": "selectin",  # Eager loading for better performance
            "primaryjoin": "and_(Project.project_id==Notebook.project_id, "
                           "Project.__table__.schema==Notebook.__table__.schema)"
        }
    )

    reminders: List["Reminder"] = Relationship(
        back_populates="project",
        sa_relationship_kwargs={
            "cascade": "all, delete-orphan",
            "lazy": "selectin",
            "primaryjoin": "and_(Project.project_id==Reminder.project_id, "
                           "Project.__table__.schema==Reminder.__table__.schema)"
        }
    )

    tasks: List["Task"] = Relationship(
        back_populates="project",
        sa_relationship_kwargs={
            "cascade": "all, delete-orphan",
            "lazy": "selectin",
            "primaryjoin": "and_(Project.project_id==Task.project_id, "
                           "Project.__table__.schema==Task.__table__.schema)"
        }
    )

    clients: List["Client"] = Relationship(
        back_populates="projects",
        link_model=ProjectClient,
        sa_relationship_kwargs={
            "lazy": "selectin",
            "primaryjoin": "and_(Project.project_id==ProjectClient.project_id, "
                           "Project.__table__.schema==ProjectClient.__table__.schema)"
        }
    )

    def __repr__(self) -> str:
        """String representation of the Project"""
        return f"Project(id={self.project_id}, name={self.name}, status={self.status})"