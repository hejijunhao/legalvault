# services/executors/workspace/reminder_executor.py

from datetime import datetime
from typing import List, Optional
from uuid import UUID

from sqlmodel import Session, select
from fastapi import HTTPException

from models.database.workspace.reminder import Reminder, ReminderStatus
from models.domain.workspace.reminder import ReminderDomain
from models.schemas.workspace.reminder import ReminderCreate, ReminderUpdate


class ReminderExecutor:
    """
    Executes reminder-related operations and handles database interactions.
    """

    def __init__(self, session: Session):
        self.session = session

    async def create_reminder(self, data: ReminderCreate, user_id: UUID) -> ReminderDomain:
        """Creates a new reminder."""
        try:
            reminder = Reminder(
                project_id=data.project_id,
                title=data.title,
                description=data.description,
                status=ReminderStatus.PENDING,
                due_date=data.due_date,
                created_by=user_id,
                modified_by=user_id
            )

            self.session.add(reminder)
            await self.session.commit()
            await self.session.refresh(reminder)

            return ReminderDomain(**reminder.dict())
        except Exception as e:
            await self.session.rollback()
            raise HTTPException(status_code=400, detail=str(e))

    async def update_reminder(
            self, reminder_id: UUID, data: ReminderUpdate, user_id: UUID
    ) -> ReminderDomain:
        """Updates reminder details."""
        try:
            reminder = await self._get_reminder(reminder_id)

            # Create domain model for business logic
            domain_reminder = ReminderDomain(**reminder.dict())

            # Update fields through domain model
            if data.title is not None or data.description is not None:
                domain_reminder.update_details(data.title, data.description, user_id)

            if data.status is not None:
                domain_reminder.update_status(data.status, user_id)

            if data.due_date is not None:
                domain_reminder.update_due_date(data.due_date, user_id)

            # Update database model
            for field, value in data.dict(exclude_unset=True).items():
                setattr(reminder, field, value)

            reminder.modified_by = user_id
            reminder.updated_at = datetime.utcnow()

            await self.session.commit()
            await self.session.refresh(reminder)

            return ReminderDomain(**reminder.dict())
        except Exception as e:
            await self.session.rollback()
            raise HTTPException(status_code=400, detail=str(e))

    async def complete_reminder(self, reminder_id: UUID, user_id: UUID) -> ReminderDomain:
        """Marks a reminder as completed."""
        try:
            reminder = await self._get_reminder(reminder_id)

            # Create domain model for business logic
            domain_reminder = ReminderDomain(**reminder.dict())
            domain_reminder.complete(user_id)

            # Update database model
            reminder.status = ReminderStatus.COMPLETED
            reminder.modified_by = user_id
            reminder.updated_at = datetime.utcnow()

            await self.session.commit()
            await self.session.refresh(reminder)

            return ReminderDomain(**reminder.dict())
        except Exception as e:
            await self.session.rollback()
            raise HTTPException(status_code=400, detail=str(e))

    async def delete_reminder(self, reminder_id: UUID) -> None:
        """Deletes a reminder."""
        try:
            reminder = await self._get_reminder(reminder_id)
            await self.session.delete(reminder)
            await self.session.commit()
        except Exception as e:
            await self.session.rollback()
            raise HTTPException(status_code=400, detail=str(e))

    async def get_reminder(self, reminder_id: UUID) -> ReminderDomain:
        """Retrieves a reminder by ID."""
        reminder = await self._get_reminder(reminder_id)
        return ReminderDomain(**reminder.dict())

    async def list_reminders(
            self,
            user_id: UUID,
            project_id: Optional[UUID] = None,
            status: Optional[ReminderStatus] = None
    ) -> List[ReminderDomain]:
        """Lists reminders with optional filters."""
        try:
            query = select(Reminder)

            if project_id:
                query = query.where(Reminder.project_id == project_id)
            if status:
                query = query.where(Reminder.status == status)

            # Order by due date and status for consistency
            query = query.order_by(Reminder.due_date.asc(), Reminder.status)

            result = await self.session.execute(query)
            reminders = result.scalars().all()

            return [ReminderDomain(**reminder.dict()) for reminder in reminders]
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))

    async def get_project_reminders(
            self,
            project_id: UUID,
            status: Optional[ReminderStatus] = None
    ) -> List[ReminderDomain]:
        """Retrieves all reminders for a specific project."""
        try:
            query = select(Reminder).where(Reminder.project_id == project_id)

            if status:
                query = query.where(Reminder.status == status)

            # Order by due date and status
            query = query.order_by(Reminder.due_date.asc(), Reminder.status)

            result = await self.session.execute(query)
            reminders = result.scalars().all()

            return [ReminderDomain(**reminder.dict()) for reminder in reminders]
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))

    async def _get_reminder(self, reminder_id: UUID) -> Reminder:
        """Helper method to get reminder by ID."""
        reminder = await self.session.get(Reminder, reminder_id)
        if not reminder:
            raise HTTPException(status_code=404, detail="Reminder not found")
        return reminder