# models/database/workspace/reminder.py

from datetime import datetime
from enum import Enum
from typing import Optional
from sqlalchemy import text
from sqlalchemy.dialects.postgresql import UUID
from sqlmodel import Field, SQLModel, Index, Column, ForeignKey, Relationship


class ReminderStatus(str, Enum):
    """Status options for reminders"""
    PENDING = "pending"
    COMPLETED = "completed"


class Reminder(SQLModel, table=True):
    """
    Represents a reminder in the LegalVault system.
    Contains core properties and metadata for reminder functionality.
    """
    __tablename__ = "reminders"

    # Table configuration
    __table_args__ = (
        Index("idx_reminder_project", "project_id"),
        Index("idx_reminder_status", "status"),
        Index("idx_reminder_due_date", "due_date"),
        Index("idx_reminder_created_by", "created_by"),
        Index("idx_reminder_modified", "modified_by", "updated_at")
    )

    model_config = {
        "arbitrary_types_allowed": True,
        "json_schema_extra": {
            "examples": [
                {
                    "title": "Review Contract Draft",
                    "description": "Review latest version of merger agreement",
                    "status": "pending",
                    "due_date": "2024-02-01T15:00:00Z"
                }
            ]
        }
    }

    # Core Properties
    reminder_id: UUID = Field(
        sa_column=Column(
            UUID(as_uuid=True),
            primary_key=True,
            server_default=text("gen_random_uuid()"),
            nullable=False
        ),
        description="Unique identifier for the reminder"
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
        max_length=255,
        nullable=False,
        description="Title of the reminder"
    )
    description: str = Field(
        max_length=1000,
        nullable=True,
        description="Detailed description of the reminder"
    )
    status: ReminderStatus = Field(
        default=ReminderStatus.PENDING,
        nullable=False,
        index=True,
        description="Current status of the reminder"
    )
    due_date: datetime = Field(
        nullable=False,
        index=True,
        description="Due date for the reminder"
    )

    # Metadata
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        nullable=False,
        description="Timestamp when the reminder was created"
    )
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        nullable=False,
        index=True,
        description="Timestamp when the reminder was last updated"
    )
    created_by: UUID = Field(
        sa_column=Column(
            UUID(as_uuid=True),
            ForeignKey("users.id", ondelete="RESTRICT"),
            nullable=False
        ),
        description="User ID of reminder creator"
    )
    modified_by: UUID = Field(
        sa_column=Column(
            UUID(as_uuid=True),
            ForeignKey("users.id", ondelete="RESTRICT"),
            nullable=False
        ),
        description="User ID of last modifier"
    )

    # Relationships
    project: "Project" = Relationship(
        back_populates="reminders",
        sa_relationship_kwargs={
            "lazy": "selectin"  # Eager loading for better performance
        }
    )

    def __repr__(self) -> str:
        """String representation of the Reminder"""
        return f"Reminder(id={self.reminder_id}, title={self.title}, status={self.status})"