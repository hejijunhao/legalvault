# backend/models/database/workspace/notebook.py

from datetime import datetime
from typing import Optional, TYPE_CHECKING
from sqlalchemy import text, Text, JSON, String, ARRAY
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
        default_factory=datetime.utcnow,
        nullable=False,
        description="Timestamp when the notebook was created"
    )
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        nullable=False,
        index=True,
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
    content: str = Field(
        sa_column=Column(Text),
        default="",
        description="Rich text content of the notebook"
    )
    title: Optional[str] = Field(
        max_length=255,
        nullable=True,
        index=True,
        description="Optional title for the notebook"
    )
    tags: list[str] = Field(
        sa_column=Column(
            ARRAY(String),
            nullable=False,
            default=[]
        ),
        description="Tags for categorizing and filtering notebooks"
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
    project: "Project" = Relationship(
        back_populates="notebook",
        sa_relationship_kwargs={
            "uselist": False,
            "primaryjoin": "and_(NotebookBase.project_id==Project.project_id, "
                          "NotebookBase.__table__.schema==Project.__table__.schema)"
        }
    )

    def __repr__(self) -> str:
        """String representation of the Notebook"""
        return f"Notebook(id={self.notebook_id}, project_id={self.project_id}, title={self.title or 'Untitled'})"


class NotebookBlueprint(NotebookBase):
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