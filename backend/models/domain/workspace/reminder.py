# models/domain/workspace/reminder.py

from datetime import datetime
from typing import Optional
from uuid import UUID
from fastapi import HTTPException
from models.database.workspace.reminder import ReminderStatus


class ReminderStateError(Exception):
    """Custom exception for invalid reminder state transitions"""
    pass


class ReminderDomain:
    """
    Domain model for Reminder entities. Handles business logic, state management,
    and behavior for reminders in the LegalVault system.
    """

    def __init__(
            self,
            reminder_id: UUID,
            project_id: UUID,
            title: str,
            description: Optional[str],
            status: ReminderStatus,
            due_date: datetime,
            created_by: UUID,
            modified_by: UUID,
            created_at: Optional[datetime] = None,
            updated_at: Optional[datetime] = None
    ):
        self.reminder_id = reminder_id
        self.project_id = project_id
        self.title = title
        self.description = description
        self.status = status
        self.due_date = due_date
        self.created_by = created_by
        self.modified_by = modified_by
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at or datetime.utcnow()

    def _validate_active_state(self) -> None:
        """Validates if reminder can be modified"""
        if self.status == ReminderStatus.COMPLETED:
            raise ReminderStateError("Cannot modify a completed reminder")

    def _update_modification_metadata(self, modified_by: UUID) -> None:
        """Updates modification metadata"""
        self.modified_by = modified_by
        self.updated_at = datetime.utcnow()

    def update_status(self, new_status: ReminderStatus, modified_by: UUID) -> None:
        """
        Updates reminder status with validation.

        Args:
            new_status: New status to set
            modified_by: User making the modification

        Raises:
            ReminderStateError: If the state transition is invalid
        """
        if new_status == self.status:
            return

        if new_status == ReminderStatus.PENDING and self.status == ReminderStatus.COMPLETED:
            raise ReminderStateError("Cannot reopen a completed reminder")

        self.status = new_status
        self._update_modification_metadata(modified_by)

    def update_due_date(self, new_due_date: datetime, modified_by: UUID) -> None:
        """
        Updates reminder due date.

        Args:
            new_due_date: New due date to set
            modified_by: User making the modification

        Raises:
            ReminderStateError: If reminder is completed
        """
        self._validate_active_state()
        self.due_date = new_due_date
        self._update_modification_metadata(modified_by)

    def update_details(self, title: Optional[str], description: Optional[str], modified_by: UUID) -> None:
        """
        Updates reminder title and description.

        Args:
            title: New title (optional)
            description: New description (optional)
            modified_by: User making the modification

        Raises:
            ReminderStateError: If reminder is completed
        """
        self._validate_active_state()
        if title is not None:
            self.title = title
        if description is not None:
            self.description = description
        self._update_modification_metadata(modified_by)

    def complete(self, modified_by: UUID) -> None:
        """
        Marks the reminder as completed.

        Args:
            modified_by: User completing the reminder

        Raises:
            ReminderStateError: If reminder is already completed
        """
        if self.status == ReminderStatus.COMPLETED:
            raise ReminderStateError("Reminder is already completed")

        self.status = ReminderStatus.COMPLETED
        self._update_modification_metadata(modified_by)

    def is_overdue(self) -> bool:
        """
        Checks if the reminder is overdue.

        Returns:
            bool: True if reminder is overdue, False otherwise
        """
        return (
                self.status == ReminderStatus.PENDING and
                self.due_date < datetime.utcnow()
        )

    def dict(self) -> dict:
        """Converts domain model to dictionary representation"""
        return {
            'reminder_id': self.reminder_id,
            'project_id': self.project_id,
            'title': self.title,
            'description': self.description,
            'status': self.status,
            'due_date': self.due_date,
            'created_by': self.created_by,
            'modified_by': self.modified_by,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }