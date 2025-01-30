# backend/models/database/workspace/notebook.py

from datetime import datetime
from typing import List, Optional, TYPE_CHECKING
from sqlalchemy import text, Text, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlmodel import Field, SQLModel, Column, ForeignKey, Index, Relationship

if TYPE_CHECKING:
    from models.database.workspace.project import Project

class Notebook(SQLModel, table=True):
    """
    Represents a notebook in the LegalVault system.
    Contains rich text content and is associated with a single project.
    """
    __tablename__ = "notebooks"

    # Table configuration
    __table_args__ = (
        {'schema': 'public'},
        Index("idx_notebook_project", "project_id"),
        Index("idx_notebook_modified", "modified_by", "updated_at"),
        Index("idx_notebook_created", "created_by")
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
            ForeignKey("public.projects.project_id", ondelete="CASCADE"),
            nullable=False,
            unique=True  # Ensures one-to-one relationship with project
        ),
        description="Associated project ID"
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
            ForeignKey("vault.users.id", ondelete="RESTRICT"),
            nullable=False
        ),
        description="User ID of notebook creator"
    )
    modified_by: UUID = Field(
        sa_column=Column(
            UUID(as_uuid=True),
            ForeignKey("vault.users.id", ondelete="RESTRICT"),
            nullable=False
        ),
        description="User ID of last modifier"
    )

    # Content
    content: str = Field(
        sa_column=Column(Text),  # Changed from JSON to Text
        default="",
        description="Rich text content of the notebook"
    )
    title: Optional[str] = Field(
        max_length=255,
        nullable=True,
        index=True,
        description="Optional title for the notebook"
    )
    tags: List[str] = Field(
        sa_column=Column(JSON),
        default=[],
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

    project: "Project" = Relationship(
        back_populates="notebook",
        sa_relationship_kwargs={"uselist": False}
    )

    def __repr__(self) -> str:
        """String representation of the Notebook"""
        return f"Notebook(id={self.notebook_id}, project_id={self.project_id}, title={self.title or 'Untitled'})"