# models/database/workspace/task.py

from datetime import datetime
from enum import Enum
from typing import Optional, TYPE_CHECKING
from sqlalchemy import text, String, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlmodel import Field, SQLModel, Index, Column, ForeignKey, Relationship
from pydantic import validator
from abc import ABC

if TYPE_CHECKING:
    from .project import ProjectBase

class TaskStatus(str, Enum):
    """Status options for tasks"""
    TODO = "todo"
    COMPLETED = "completed"


class TaskBase(SQLModel, ABC):
    """
    Abstract base class representing a task in the LegalVault system.
    Serves as a template for tenant-specific task implementations.
    Contains core properties and metadata for task functionality.
    """
    __abstract__ = True

    # Table configuration
    __table_args__ = (
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
            ForeignKey("projects.project_id", ondelete="CASCADE"),
            nullable=False
        ),
        description="ID of the associated project"
    )
    title: str = Field(
        sa_column=Column(String(255), nullable=False),
        description="Title of the task"
    )
    description: str = Field(
        sa_column=Column(String(1000), nullable=True),
        description="Detailed description of the task"
    )
    status: str = Field(
        sa_column=Column(String, nullable=False),
        default=TaskStatus.TODO.value,
        description="Current status of the task"
    )

    @validator("status")
    def validate_status(cls, v):
        if isinstance(v, TaskStatus):
            return v.value
        if v not in [e.value for e in TaskStatus]:
            raise ValueError(f"Invalid status: {v}")
        return v

    due_date: datetime = Field(
        sa_column=Column(DateTime, nullable=False, index=True),
        description="Due date for the task"
    )
    assigned_to: UUID = Field(
        sa_column=Column(
            UUID(as_uuid=True),
            ForeignKey("enterprise_schema.users.id", ondelete="RESTRICT"),
            nullable=False
        ),
        description="User ID of task assignee"
    )

    # Metadata
    created_at: datetime = Field(
        sa_column=Column(DateTime, nullable=False),
        default_factory=datetime.utcnow,
        description="Timestamp when the task was created"
    )
    updated_at: datetime = Field(
        sa_column=Column(DateTime, nullable=False),
        default_factory=datetime.utcnow,
        description="Timestamp when the task was last updated"
    )
    created_by: UUID = Field(
        sa_column=Column(
            UUID(as_uuid=True),
            ForeignKey("enterprise_schema.users.id", ondelete="RESTRICT"),
            nullable=False
        ),
        description="User ID of task creator"
    )
    modified_by: UUID = Field(
        sa_column=Column(
            UUID(as_uuid=True),
            ForeignKey("enterprise_schema.users.id", ondelete="RESTRICT"),
            nullable=False
        ),
        description="User ID of last modifier"
    )
    completed_at: Optional[datetime] = Field(
        sa_column=Column(DateTime, nullable=True),
        description="Timestamp when the task was completed"
    )

    # Relationships
    project: Optional["ProjectBase"] = Relationship(
        back_populates="task",
        sa_relationship_kwargs={
            "lazy": "selectin",
            "primaryjoin": "and_(foreign(TaskBase.project_id)==ProjectBase.project_id, "
                           "TaskBase.__table__.schema==ProjectBase.__table__.schema)"
        }
    )

    def __repr__(self) -> str:
        """String representation of the Task"""
        return f"Task(id={self.task_id}, title={self.title}, status={self.status})"


class TaskBlueprint(TaskBase, table=True):
    """
    Concrete implementation of TaskBase for the public schema blueprint.
    Serves as a reference for tenant-specific implementations.
    """
    __tablename__ = "task_blueprint"
    __table_args__ = (
        *TaskBase.__table_args__,
        {'schema': 'public'}
    )
