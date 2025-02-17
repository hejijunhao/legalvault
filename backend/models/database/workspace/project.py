# models/database/workspace/project.py

from datetime import datetime
from enum import Enum
from typing import Optional, List, Dict, TYPE_CHECKING
from sqlalchemy import text, ARRAY, String, UniqueConstraint, DateTime
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlmodel import Field, SQLModel, JSON, Column, Index, ForeignKey, Relationship
from abc import ABC
from pydantic import validator

if TYPE_CHECKING:
    from .notebook import NotebookBase
    from .reminder import ReminderBase
    from .task import TaskBase
    from .project_client import ProjectClientBase
    from .contact_project import ContactProjectBase


class ProjectStatus(str, Enum):
    ACTIVE = "active"
    COMPLETED = "completed"
    ARCHIVED = "archived"


class ConfidentialityLevel(str, Enum):
    """Confidentiality levels for projects"""
    PUBLIC = "public"
    CONFIDENTIAL = "confidential"


class ProjectKnowledge(SQLModel):
    """
    Represents the synthesized knowledge about a project, combining LLM-generated insights
    and manual user input in rich text format.
    """
    content: str = Field(default="", description="Rich text content containing project knowledge")
    last_updated: datetime = Field(default_factory=datetime.utcnow)
    summary: str = Field(default="", description="Brief summary of the project knowledge")
    tags: list[str] = Field(default_factory=list, description="Knowledge tags for categorization")


class ProjectBase(SQLModel, ABC):
    """
    Abstract base class representing a project in the LegalVault system.
    Serves as a template for tenant-specific project implementations.
    Contains core properties, metadata, and synthesized project knowledge.
    """
    __abstract__ = True

    # Table configuration
    __table_args__ = (
        UniqueConstraint("name", name="uq_project_name"),
        Index("idx_project_status_practice", "status", "practice_area"),
        Index("idx_project_created_by", "created_by"),
        Index("idx_project_modified", "modified_by", "updated_at"),
        Index("idx_project_tasks", "project_id")
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
        sa_column=Column(String(255), nullable=False, index=True),
        description="Name of the project"
    )
    status: str = Field(
        sa_column=Column(String, nullable=False),
        default=ProjectStatus.ACTIVE.value,
        description="Current status of the project"
    )
    created_at: datetime = Field(
        sa_column=Column(DateTime, nullable=False),
        default_factory=datetime.utcnow,
        description="When the project was created"
    )
    updated_at: datetime = Field(
        sa_column=Column(DateTime, nullable=False),
        default_factory=datetime.utcnow,
        description="When the project was last updated"
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
        sa_column=Column(String(100), nullable=True, index=True),
        description="Area of legal practice this project belongs to"
    )
    confidentiality: str = Field(
        sa_column=Column(String, nullable=False),
        default=ConfidentialityLevel.CONFIDENTIAL.value,
        description="Confidentiality level of the project"
    )
    start_date: Optional[datetime] = Field(
        sa_column=Column(DateTime, nullable=True),
        description="Project start date"
    )
    end_date: Optional[datetime] = Field(
        sa_column=Column(DateTime, nullable=True),
        description="Project end date"
    )
    tags: list[str] = Field(
        sa_column=Column(ARRAY(String), nullable=False, default=list),
        description="List of tags associated with the project"
    )

    # Project Knowledge and Summary
    knowledge: ProjectKnowledge = Field(
        sa_column=Column(JSON, nullable=True),
        default_factory=ProjectKnowledge,
        description="Synthesized project knowledge combining LLM insights and user input"
    )
    summary: str = Field(
        sa_column=Column(String(2000), nullable=True),
        description="Condensed project summary for LLM context and quick reference"
    )
    summary_updated_at: datetime = Field(
        nullable=True,
        description="Timestamp when the project summary was last updated"
    )

    # Relationships
    notebook: Optional["NotebookBase"] = Relationship(
        back_populates="project",
        sa_relationship_kwargs={
            "uselist": False,
            "cascade": "all, delete-orphan",
            "lazy": "selectin",
            "primaryjoin": "and_(foreign(ProjectBase.project_id)==NotebookBase.project_id, "
                           "ProjectBase.__table__.schema==NotebookBase.__table__.schema)"
        }
    )

    reminder: Optional[List["ReminderBase"]] = Relationship(
        back_populates="project",
        sa_relationship_kwargs={
            "cascade": "all, delete-orphan",
            "lazy": "selectin",
            "primaryjoin": "and_(foreign(ProjectBase.project_id)==ReminderBase.project_id, "
                           "ProjectBase.__table__.schema==ReminderBase.__table__.schema)"
        }
    )

    task: Optional[List["TaskBase"]] = Relationship(
        back_populates="project",
        sa_relationship_kwargs={
            "cascade": "all, delete-orphan",
            "lazy": "selectin",
            "primaryjoin": "and_(foreign(ProjectBase.project_id)==TaskBase.project_id, "
                           "ProjectBase.__table__.schema==TaskBase.__table__.schema)"
        }
    )

    contact_project: Optional[List["ContactProjectBase"]] = Relationship(
        back_populates="project",
        link_model="ContactProjectBase",
        sa_relationship_kwargs={
            "lazy": "selectin",
            "cascade": "all",
            "primaryjoin": (
                "and_(foreign(ProjectBase.project_id)==ContactProjectBase.project_id, "
                "ProjectBase.__table__.schema==ContactProjectBase.__table__.schema)"
            ),
            "secondaryjoin": (
                "and_(ContactProjectBase.contact_id==ContactBase.contact_id, "
                "ContactProjectBase.__table__.schema==ContactBase.__table__.schema)"
            )
        }
    )

    project_client: Optional[List["ProjectClientBase"]] = Relationship(
        back_populates="project",
        link_model="ProjectClientBase",
        sa_relationship_kwargs={
            "lazy": "selectin",
            "cascade": "all",
            "primaryjoin": (
                "and_(foreign(ProjectBase.project_id)==ProjectClientBase.project_id, "
                "ProjectBase.__table__.schema==ProjectClientBase.__table__.schema)"
            ),
            "secondaryjoin": (
                "and_(ProjectClientBase.client_id==ClientBase.client_id, "
                "ProjectClientBase.__table__.schema==ClientBase.__table__.schema)"
            )
        }
    )

    @validator("status")
    def validate_status(cls, v):
        if isinstance(v, ProjectStatus):
            return v.value
        if v not in [e.value for e in ProjectStatus]:
            raise ValueError(f"Invalid status: {v}")
        return v

    @validator("confidentiality")
    def validate_confidentiality(cls, v):
        if isinstance(v, ConfidentialityLevel):
            return v.value
        if v not in [e.value for e in ConfidentialityLevel]:
            raise ValueError(f"Invalid confidentiality level: {v}")
        return v

    def __repr__(self) -> str:
        """String representation of the Project"""
        return f"Project(id={self.project_id}, name={self.name}, status={self.status})"


class ProjectBlueprint(ProjectBase, table=True):
    """
    Concrete implementation of ProjectBase for the public schema blueprint.
    Serves as a reference for tenant-specific implementations.
    """
    __tablename__ = "projects"
    __table_args__ = (
        *ProjectBase.__table_args__,
        {'schema': 'public'}
    )

