# backend/models/database/workspace/notebook.py

from datetime import datetime
from typing import Optional, TYPE_CHECKING
from sqlalchemy import text, Text, JSONB, String, ARRAY, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlmodel import Field, SQLModel, Column, ForeignKey, Index, Relationship
from abc import ABC

if TYPE_CHECKING:
    from .project import Project

class NotebookBase(SQLModel, ABC):
    """
    Abstract base class representing a notebook in the LegalVault system.
    Serves as a template for tenant-specific notebook implementations.
    Contains core properties and metadata for notebook functionality.
    """
    __abstract__ = True

    # Table configuration
    __table_args__ = (
        Index("idx_notebook_project", "project_id"),
        Index("idx_notebook_created_by", "created_by"),
        Index("idx_notebook_modified", "modified_by", "updated_at")
    )

    model_config = {
        "arbitrary_types_allowed": True,
        "json_schema_extra": {
            "examples": [
                {
                    "title": "Project Research Notes",
                    "content": "<rich-text>Initial project research...</rich-text>"
                }
            ]
        }
    }

    # Core Properties
    notebook_id: UUID = Field(
        sa_column=Column(
            UUID(as_uuid=True),
            primary_key=True,
            server_default=text("gen_random_uuid()"),
            nullable=False
        ),
        description="Unique identifier for the notebook"
    )
    project_id: UUID = Field(
        sa_column=Column(
            UUID(as_uuid=True),
            ForeignKey("enterprise_schema.projects.project_id", ondelete="CASCADE"),
            nullable=False
        ),
        description="ID of the associated project"
    )
    created_at: datetime = Field(
        sa_column=Column(DateTime, nullable=False),
        default_factory=datetime.utcnow,
        description="Timestamp when the notebook was created"
    )
    updated_at: datetime = Field(
        sa_column=Column(DateTime, nullable=False, index=True),
        default_factory=datetime.utcnow,
        description="Timestamp when the notebook was last updated"
    )
    created_by: UUID = Field(
        sa_column=Column(
            UUID(as_uuid=True),
            ForeignKey("enterprise_schema.users.id", ondelete="RESTRICT"),
            nullable=False
        ),
        description="User ID of notebook creator"
    )
    modified_by: UUID = Field(
        sa_column=Column(
            UUID(as_uuid=True),
            ForeignKey("enterprise_schema.users.id", ondelete="RESTRICT"),
            nullable=False
        ),
        description="User ID of last modifier"
    )

    # Content
    title: str = Field(
        sa_column=Column(String(255), nullable=True, index=True),
        description="Optional title for the notebook"
    )
    content: str = Field(
        sa_column=Column(Text, nullable=False),
        default="",
        description="Rich text content of the notebook"
    )
    metadata: NotebookMetadata = Field(
        sa_column=Column(JSONB, nullable=False),
        default_factory=NotebookMetadata,
        description="Additional notebook metadata"
    )
    tags: list[str] = Field(
        sa_column=Column(ARRAY(String), nullable=False, default=list),
        description="List of tags for categorization"
    )

    # Metadata
    last_modified_content: datetime = Field(
        default_factory=datetime.utcnow,
        nullable=False,
        description="Timestamp of last content modification"
    )
    is_archived: bool = Field(
        default=False,
        nullable=False,
        index=True,
        description="Flag indicating if the notebook is archived"
    )


    # Relationships
    project: Optional["Project"] = None

    _project = Relationship(
        back_populates="_notebook",
        sa_relationship_kwargs={
            "lazy": "selectin",
            "primaryjoin": "and_(foreign(NotebookBase.project_id)==ProjectBase.project_id, NotebookBase.__table__.schema==ProjectBase.__table__.schema)"
        }
    )

    def __repr__(self) -> str:
        """String representation of the Notebook"""
        return f"Notebook(id={self.notebook_id}, project_id={self.project_id}, title={self.title or 'Untitled'})"


class NotebookMetadata(SQLModel):
    """Additional metadata for notebooks"""
    version: int = Field(default=1, description="Version number of the notebook")
    revision_history: list[dict] = Field(
        default_factory=list,
        description="History of notebook revisions"
    )
    contributors: list[UUID] = Field(
        default_factory=list,
        description="List of users who have contributed"
    )
    last_viewed: Optional[datetime] = Field(default=None)
    references: list[dict] = Field(
        default_factory=list,
        description="External references and citations"
    )
    attachments: list[dict] = Field(
        default_factory=list,
        description="List of attached files"
    )


class NotebookBlueprint(NotebookBase, table=True):
    """
    Concrete implementation of NotebookBase for the public schema blueprint.
    Serves as a reference for tenant-specific implementations.
    """
    __tablename__ = "notebook_blueprint"
    __table_args__ = (
        Index("idx_notebook_project", "project_id"),
        Index("idx_notebook_created_by", "created_by"),
        Index("idx_notebook_modified", "modified_by", "updated_at"),
        {'schema': 'public'}
    )


class Notebook(NotebookBase):
    """
    Concrete implementation of NotebookBase for enterprise schemas.
    """
    __tablename__ = "notebooks"