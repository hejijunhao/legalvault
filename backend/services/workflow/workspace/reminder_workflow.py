# services/workflow/workspace/reminder_workflow.py

from typing import List, Optional
from uuid import UUID
from fastapi import HTTPException, Depends
from sqlmodel import Session

from core.database import get_session
from models.database.workspace.reminder import ReminderStatus
from models.permissions import (
    ReminderOperation,
    validate_reminder_operation as validate_operation_constraints
)
from models.schemas.workspace.reminder import (
    ReminderCreate,
    ReminderUpdate,
    ReminderResponse,
    ReminderListResponse
)
from services.executors.workspace.reminder_executor import ReminderExecutor
from services.workflow.workflow_tracker import WorkflowTracker


class ReminderWorkflowError(Exception):
    """Custom exception for workflow-specific errors"""
    pass


class ReminderWorkflow:
    """
    Orchestrates reminder-related workflows, handling operation validation,
    execution tracking, and coordination between services.
    """

    def __init__(
            self,
            session: Session = Depends(get_session),
            tracker: Optional[WorkflowTracker] = None
    ):
        self.session = session
        self.executor = ReminderExecutor(session)
        self.tracker = tracker or WorkflowTracker()

    async def _handle_workflow_error(
            self,
            workflow_id: Optional[str],
            error: Exception,
            operation: ReminderOperation
    ) -> None:
        """Handles workflow errors consistently"""
        if workflow_id:
            await self.tracker.fail_workflow(
                workflow_id,
                error_message=str(error),
                metadata={"operation": operation.value}
            )

        if isinstance(error, HTTPException):
            raise error
        else:
            raise HTTPException(status_code=500, detail="Internal workflow error")

    async def create_reminder(
            self, data: ReminderCreate, user_id: UUID, user_permissions: List[str]
    ) -> ReminderResponse:
        """Workflow for reminder creation."""
        if not validate_operation_constraints(ReminderOperation.CREATE_REMINDER, user_permissions):
            raise HTTPException(status_code=403, detail="Insufficient permissions")

        workflow_id = None
        try:
            workflow_id = await self.tracker.start_workflow(
                operation=ReminderOperation.CREATE_REMINDER,
                user_id=user_id,
                metadata={"project_id": str(data.project_id)}
            )

            reminder = await self.executor.create_reminder(data, user_id)

            await self.tracker.complete_workflow(
                workflow_id,
                metadata={"reminder_id": str(reminder.reminder_id)}
            )

            response = ReminderResponse(
                **reminder.dict(),
                is_overdue=reminder.is_overdue()
            )
            return response

        except Exception as e:
            await self._handle_workflow_error(workflow_id, e, ReminderOperation.CREATE_REMINDER)

    async def update_reminder(
            self,
            reminder_id: UUID,
            data: ReminderUpdate,
            user_id: UUID,
            user_permissions: List[str]
    ) -> ReminderResponse:
        """Workflow for reminder updates."""
        if not validate_operation_constraints(ReminderOperation.UPDATE_REMINDER, user_permissions):
            raise HTTPException(status_code=403, detail="Insufficient permissions")

        workflow_id = None
        try:
            workflow_id = await self.tracker.start_workflow(
                operation=ReminderOperation.UPDATE_REMINDER,
                user_id=user_id,
                metadata={"reminder_id": str(reminder_id)}
            )

            reminder = await self.executor.update_reminder(reminder_id, data, user_id)

            await self.tracker.complete_workflow(workflow_id)

            response = ReminderResponse(
                **reminder.dict(),
                is_overdue=reminder.is_overdue()
            )
            return response

        except Exception as e:
            await self._handle_workflow_error(workflow_id, e, ReminderOperation.UPDATE_REMINDER)

    async def complete_reminder(
            self,
            reminder_id: UUID,
            user_id: UUID,
            user_permissions: List[str]
    ) -> ReminderResponse:
        """Workflow for completing a reminder."""
        if not validate_operation_constraints(ReminderOperation.COMPLETE_REMINDER, user_permissions):
            raise HTTPException(status_code=403, detail="Insufficient permissions")

        workflow_id = None
        try:
            workflow_id = await self.tracker.start_workflow(
                operation=ReminderOperation.COMPLETE_REMINDER,
                user_id=user_id,
                metadata={"reminder_id": str(reminder_id)}
            )

            reminder = await self.executor.complete_reminder(reminder_id, user_id)

            await self.tracker.complete_workflow(workflow_id)

            response = ReminderResponse(
                **reminder.dict(),
                is_overdue=reminder.is_overdue()
            )
            return response

        except Exception as e:
            await self._handle_workflow_error(workflow_id, e, ReminderOperation.COMPLETE_REMINDER)

    async def delete_reminder(
            self,
            reminder_id: UUID,
            user_id: UUID,
            user_permissions: List[str]
    ) -> None:
        """Workflow for deleting a reminder."""
        if not validate_operation_constraints(ReminderOperation.DELETE_REMINDER, user_permissions):
            raise HTTPException(status_code=403, detail="Insufficient permissions")

        workflow_id = None
        try:
            workflow_id = await self.tracker.start_workflow(
                operation=ReminderOperation.DELETE_REMINDER,
                user_id=user_id,
                metadata={"reminder_id": str(reminder_id)}
            )

            await self.executor.delete_reminder(reminder_id)
            await self.tracker.complete_workflow(workflow_id)

        except Exception as e:
            await self._handle_workflow_error(workflow_id, e, ReminderOperation.DELETE_REMINDER)

    async def get_reminder(
            self,
            reminder_id: UUID,
            user_id: UUID,
            user_permissions: List[str]
    ) -> ReminderResponse:
        """Retrieves reminder details."""
        if not validate_operation_constraints(ReminderOperation.GET_REMINDER, user_permissions):
            raise HTTPException(status_code=403, detail="Insufficient permissions")

        try:
            reminder = await self.executor.get_reminder(reminder_id)
            response = ReminderResponse(
                **reminder.dict(),
                is_overdue=reminder.is_overdue()
            )
            return response

        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error retrieving reminder: {str(e)}"
            )

    async def list_project_reminders(
            self,
            project_id: UUID,
            user_id: UUID,
            user_permissions: List[str],
            status: Optional[ReminderStatus] = None
    ) -> List[ReminderListResponse]:
        """Lists all reminders for a specific project."""
        if not validate_operation_constraints(ReminderOperation.LIST_PROJECT_REMINDERS, user_permissions):
            raise HTTPException(status_code=403, detail="Insufficient permissions")

        try:
            reminders = await self.executor.get_project_reminders(project_id, status)
            return [
                ReminderListResponse(
                    **reminder.dict(),
                    is_overdue=reminder.is_overdue()
                )
                for reminder in reminders
            ]

        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error listing project reminders: {str(e)}"
            )