# services/executors/workspace/reminder_executor.py

from datetime import datetime
from typing import List, Optional
from uuid import UUID

from sqlmodel import Session, select
from fastapi import HTTPException

from models.database.workspace.reminder import Reminder, ReminderStatus
from models.domain.workspace.reminder import ReminderDomain
from models.schemas.workspace.reminder import ReminderCreate, ReminderUpdate
from services.executors.base_executor import BaseExecutor


class ReminderExecutor(BaseExecutor[Reminder, ReminderDomain]):
    """
    Executes reminder-related operations and handles database interactions.
    Extends BaseExecutor for common CRUD operations.
    """

    def __init__(self, session: Session):
        super().__init__(session, Reminder, "reminder_id", ReminderDomain)

    async def create_reminder(self, data: ReminderCreate, user_id: UUID) -> ReminderDomain:
        """Creates a new reminder."""
        reminder = await self.create(
            {
                "project_id": data.project_id,
                "title": data.title,
                "description": data.description,
                "status": ReminderStatus.PENDING,
                "due_date": data.due_date,
            },
            user_id=user_id,
        )
        return self._to_domain(reminder)

    async def update_reminder(
        self, reminder_id: UUID, data: ReminderUpdate, user_id: UUID
    ) -> ReminderDomain:
        """Updates reminder details."""
        reminder = await self.get_or_404(reminder_id)

        # Create domain model for business logic
        domain_reminder = ReminderDomain(**reminder.dict())

        # Update fields through domain model
        if data.title is not None or data.description is not None:
            domain_reminder.update_details(data.title, data.description, user_id)

        if data.status is not None:
            domain_reminder.update_status(data.status, user_id)

        if data.due_date is not None:
            domain_reminder.update_due_date(data.due_date, user_id)

        # Update database model using base class method
        reminder = await self.update(
            reminder_id, data.dict(exclude_unset=True), user_id
        )
        return self._to_domain(reminder)

    async def complete_reminder(self, reminder_id: UUID, user_id: UUID) -> ReminderDomain:
        """Marks a reminder as completed."""
        reminder = await self.get_or_404(reminder_id)

        # Create domain model for business logic
        domain_reminder = ReminderDomain(**reminder.dict())
        domain_reminder.complete(user_id)

        # Update database model
        reminder.status = ReminderStatus.COMPLETED
        reminder.modified_by = user_id
        reminder.updated_at = datetime.utcnow()

        await self._commit_and_refresh(reminder)
        return self._to_domain(reminder)

    async def delete_reminder(self, reminder_id: UUID) -> None:
        """Deletes a reminder."""
        await self.delete(reminder_id)

    async def get_reminder(self, reminder_id: UUID) -> ReminderDomain:
        """Retrieves a reminder by ID."""
        reminder = await self.get_or_404(reminder_id)
        return self._to_domain(reminder)

    async def list_reminders(
        self,
        user_id: UUID,
        project_id: Optional[UUID] = None,
        status: Optional[ReminderStatus] = None,
    ) -> List[ReminderDomain]:
        """Lists reminders with optional filters."""
        filters = {}
        if project_id:
            filters["project_id"] = project_id
        if status:
            filters["status"] = status

        reminders = await self.list(
            filters=filters,
            order_by=[Reminder.due_date.asc(), Reminder.status],
        )
        return self._to_domain_list(reminders)

    async def get_project_reminders(
        self,
        project_id: UUID,
        status: Optional[ReminderStatus] = None,
    ) -> List[ReminderDomain]:
        """Retrieves all reminders for a specific project."""
        filters = {"project_id": project_id}
        if status:
            filters["status"] = status

        reminders = await self.list(
            filters=filters,
            order_by=[Reminder.due_date.asc(), Reminder.status],
        )
        return self._to_domain_list(reminders)
