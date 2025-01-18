# models/domain/workspace/task.py

from datetime import datetime
from typing import Optional
from uuid import UUID
from fastapi import HTTPException
from models.database.workspace.task import TaskStatus


class TaskStateError(Exception):
    """Custom exception for invalid task state transitions"""
    pass


class TaskDomain:
    """
    Domain model for Task entities. Handles business logic, state management,
    and behavior for tasks in the LegalVault system.
    """

    def __init__(
            self,
            task_id: UUID,
            project_id: UUID,
            title: str,
            description: Optional[str],
            status: TaskStatus,
            due_date: datetime,
            assigned_to: UUID,
            created_by: UUID,
            modified_by: UUID,
            created_at: Optional[datetime] = None,
            updated_at: Optional[datetime] = None,
            completed_at: Optional[datetime] = None
    ):
        self.task_id = task_id
        self.project_id = project_id
        self.title = title
        self.description = description
        self.status = status
        self.due_date = due_date
        self.assigned_to = assigned_to
        self.created_by = created_by
        self.modified_by = modified_by
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at or datetime.utcnow()
        self.completed_at = completed_at

    def _validate_active_state(self) -> None:
        """Validates if task can be modified"""
        if self.status == TaskStatus.COMPLETED:
            raise TaskStateError("Cannot modify a completed task")

    def _update_modification_metadata(self, modified_by: UUID) -> None:
        """Updates modification metadata"""
        self.modified_by = modified_by
        self.updated_at = datetime.utcnow()

    def update_details(self, title: Optional[str], description: Optional[str], modified_by: UUID) -> None:
        """
        Updates task title and description.

        Args:
            title: New title (optional)
            description: New description (optional)
            modified_by: User making the modification

        Raises:
            TaskStateError: If task is completed
        """
        self._validate_active_state()
        if title is not None:
            self.title = title
        if description is not None:
            self.description = description
        self._update_modification_metadata(modified_by)

    def update_due_date(self, new_due_date: datetime, modified_by: UUID) -> None:
        """
        Updates task due date.

        Args:
            new_due_date: New due date to set
            modified_by: User making the modification

        Raises:
            TaskStateError: If task is completed
        """
        self._validate_active_state()
        self.due_date = new_due_date
        self._update_modification_metadata(modified_by)

    def reassign(self, new_assignee: UUID, modified_by: UUID) -> None:
        """
        Reassigns the task to a different user.

        Args:
            new_assignee: UUID of new assignee
            modified_by: User making the modification

        Raises:
            TaskStateError: If task is completed
        """
        self._validate_active_state()
        self.assigned_to = new_assignee
        self._update_modification_metadata(modified_by)

    def complete(self, modified_by: UUID) -> None:
        """
        Marks the task as completed.

        Args:
            modified_by: User completing the task

        Raises:
            TaskStateError: If task is already completed
        """
        if self.status == TaskStatus.COMPLETED:
            raise TaskStateError("Task is already completed")

        self.status = TaskStatus.COMPLETED
        self.completed_at = datetime.utcnow()
        self._update_modification_metadata(modified_by)

    def reopen(self, modified_by: UUID) -> None:
        """
        Reopens a completed task.

        Args:
            modified_by: User reopening the task

        Raises:
            TaskStateError: If task is not completed
        """
        if self.status != TaskStatus.COMPLETED:
            raise TaskStateError("Can only reopen completed tasks")

        self.status = TaskStatus.TODO
        self.completed_at = None
        self._update_modification_metadata(modified_by)

    def is_overdue(self) -> bool:
        """
        Checks if the task is overdue.

        Returns:
            bool: True if task is overdue, False otherwise
        """
        return (
            self.status == TaskStatus.TODO and
            self.due_date < datetime.utcnow()
        )

    def dict(self) -> dict:
        """Converts domain model to dictionary representation"""
        return {
            'task_id': self.task_id,
            'project_id': self.project_id,
            'title': self.title,
            'description': self.description,
            'status': self.status,
            'due_date': self.due_date,
            'assigned_to': self.assigned_to,
            'created_by': self.created_by,
            'modified_by': self.modified_by,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
            'completed_at': self.completed_at
        }