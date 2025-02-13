# models/database/workspace/reminder.py

from datetime import datetime
from enum import Enum
from typing import Optional, List, TYPE_CHECKING
from sqlalchemy import text, String, DateTime, Column, ForeignKey, Index
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlmodel import Field, SQLModel, Relationship
from pydantic import validator
from .project import Project
from abc import ABC


class ReminderStatus(str, Enum):
    """Status options for reminders"""
    PENDING = "pending"
    COMPLETED = "completed"


class ReminderMetadata(SQLModel):
    """Additional metadata for reminders"""
    priority: str = Field(default="medium", description="Priority level of the reminder")
    recurrence: Optional[dict] = Field(
        default=None,
        description="Recurrence pattern if reminder repeats"
    )
    notifications: list[dict] = Field(
        default_factory=list,
        description="List of notification settings"
    )
    completion_notes: str = Field(default="", description="Notes upon completion")
    tags: list[str] = Field(default_factory=list, description="Reminder tags")


class ReminderBase(SQLModel, ABC):
    """
    Abstract base class representing a reminder in the LegalVault system.
    Serves as a template for tenant-specific reminder implementations.
    Contains core properties and metadata for reminder functionality.
    """
    __abstract__ = True

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
            ForeignKey("enterprise_schema.projects.project_id", ondelete="CASCADE"),
            nullable=False
        ),
        description="ID of the associated project"
    )
    title: str = Field(
        sa_column=Column(String(255), nullable=False),
        description="Title of the reminder"
    )
    description: str = Field(
        sa_column=Column(String(1000), nullable=True),
        description="Detailed description of the reminder"
    )
    status: str = Field(
        sa_column=Column(String, nullable=False),
        default=ReminderStatus.PENDING.value,
        description="Current status of the reminder"
    )

    @validator("status")
    def validate_status(cls, v):
        if isinstance(v, ReminderStatus):
            return v.value
        if v not in [e.value for e in ReminderStatus]:
            raise ValueError(f"Invalid status: {v}")
        return v

    due_date: datetime = Field(
        sa_column=Column(DateTime, nullable=False, index=True),
        description="Due date for the reminder"
    )

    completed_at: Optional[datetime] = Field(
        sa_column=Column(DateTime, nullable=True),
        description="When the reminder was completed"
    )

    metadata: ReminderMetadata = Field(
        sa_column=Column(JSONB, nullable=False),
        default_factory=ReminderMetadata,
        description="Additional reminder metadata and settings"
    )

    # Metadata
    created_at: datetime = Field(
        sa_column=Column(DateTime, nullable=False),
        default_factory=datetime.utcnow,
        description="When the reminder was created"
    )
    updated_at: datetime = Field(
        sa_column=Column(DateTime, nullable=False),
        default_factory=datetime.utcnow,
        description="When the reminder was last updated"
    )
    created_by: UUID = Field(
        sa_column=Column(
            UUID(as_uuid=True),
            ForeignKey("vault.users.id", ondelete="RESTRICT"),
            nullable=False
        ),
        description="User ID of reminder creator"
    )
    modified_by: UUID = Field(
        sa_column=Column(
            UUID(as_uuid=True),
            ForeignKey("vault.users.id", ondelete="RESTRICT"),
            nullable=False
        ),
        description="User ID of last modifier"
    )

    # Relationships
    project: Optional["Project"] = None

    _project = Relationship(
        back_populates="_reminder",
        sa_relationship_kwargs={
            "lazy": "selectin",
            "primaryjoin": "and_(foreign(ReminderBase.project_id)==ProjectBase.project_id, ReminderBase.__table__.schema==ProjectBase.__table__.schema)"
        }
    )

    def __repr__(self) -> str:
        """String representation of the Reminder"""
        return f"Reminder(id={self.reminder_id}, title={self.title}, status={self.status})"


class ReminderBlueprint(ReminderBase, table=True):
    """
    Concrete implementation of ReminderBase for the public schema blueprint.
    Serves as a reference for tenant-specific implementations.
    """
    __tablename__ = "reminder_blueprint"
    __table_args__ = (
        Index("idx_reminder_project", "project_id"),
        Index("idx_reminder_status", "status"),
        Index("idx_reminder_due", "due_date"),
        Index("idx_reminder_created_by", "created_by"),
        Index("idx_reminder_modified", "modified_by", "updated_at"),
        {'schema': 'public'}
    )


class Reminder(ReminderBase):
    """
    Concrete implementation of ReminderBase for enterprise schemas.
    """
    __tablename__ = "reminders"