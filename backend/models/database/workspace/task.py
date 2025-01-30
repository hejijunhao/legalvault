# models/database/workspace/task.py

from datetime import datetime
from enum import Enum
from typing import Optional
from sqlalchemy import text
from sqlalchemy.dialects.postgresql import UUID
from sqlmodel import Field, SQLModel, Index, Column, ForeignKey, Relationship


class TaskStatus(str, Enum):
    """Status options for tasks"""
    TODO = "todo"
    COMPLETED = "completed"


class Task(SQLModel, table=True):
    """
    Represents a task in the LegalVault system.
    Contains core properties and metadata for task functionality.
    """
    __tablename__ = "tasks"

    # Table configuration
    __table_args__ = (
        {'schema': 'public'},
        Index("idx_task_project", "project_id"),
        Index("idx_task_status", "status"),
        Index("idx_task_due_date", "due_date"),
        Index("idx_task_assigned", "assigned_to"),
        Index("idx_task_created_by", "created_by"),
        Index("idx_task_modified", "modified_by", "updated_at")
    )

    model_config = {
        "arbitrary_types_allowed": True,
        "json_schema_extra": {
            "examples": [
                {
                    "title": "Draft Initial Response",
                    "description": "Prepare first draft of response to client query",
                    "status": "todo",
                    "due_date": "2024-02-01T15:00:00Z"
                }
            ]
        }
    }

    # Core Properties
    task_id: UUID = Field(
        sa_column=Column(
            UUID(as_uuid=True),
            primary_key=True,
            server_default=text("gen_random_uuid()"),
            nullable=False
        ),
        description="Unique identifier for the task"
    )
    project_id: UUID = Field(
        sa_column=Column(
            UUID(as_uuid=True),
            ForeignKey("public.projects.project_id", ondelete="CASCADE"),
            nullable=False
        ),
        description="ID of the associated project"
    )
    title: str = Field(
        max_length=255,
        nullable=False,
        description="Title of the task"
    )
    description: Optional[str] = Field(
        max_length=1000,
        nullable=True,
        description="Detailed description of the task"
    )
    status: TaskStatus = Field(
        default=TaskStatus.TODO,
        nullable=False,
        index=True,
        description="Current status of the task"
    )
    due_date: datetime = Field(
        nullable=False,
        index=True,
        description="Due date for the task"
    )
    assigned_to: UUID = Field(
        sa_column=Column(
            UUID(as_uuid=True),
            ForeignKey("vault.users.id", ondelete="RESTRICT"),
            nullable=False
        ),
        description="User ID of task assignee"
    )

    # Metadata
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        nullable=False,
        description="Timestamp when the task was created"
    )
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        nullable=False,
        index=True,
        description="Timestamp when the task was last updated"
    )
    created_by: UUID = Field(
        sa_column=Column(
            UUID(as_uuid=True),
            ForeignKey("vault.users.id", ondelete="RESTRICT"),
            nullable=False
        ),
        description="User ID of task creator"
    )
    modified_by: UUID = Field(
        sa_column=Column(
            UUID(as_uuid=True),
            ForeignKey("vault.users.id", ondelete="RESTRICT"),
            nullable=False
        ),
        description="User ID of last modifier"
    )
    completed_at: Optional[datetime] = Field(
        nullable=True,
        index=True,
        description="Timestamp when the task was completed"
    )

    # Relationships
    project: "Project" = Relationship(
        back_populates="tasks",
        sa_relationship_kwargs={
            "lazy": "selectin"  # Eager loading for better performance
        }
    )

    def __repr__(self) -> str:
        """String representation of the Task"""
        return f"Task(id={self.task_id}, title={self.title}, status={self.status})"