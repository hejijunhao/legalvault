# services/workflow/workspace/task_workflow.py

from typing import List, Optional
from uuid import UUID
from fastapi import HTTPException, Depends
from sqlmodel import Session

from core.database import get_session
from models.database.workspace.task import TaskStatus
from models.domain.workspace.operations_task import (
    TaskOperation,
    validate_operation_constraints
)
from models.schemas.workspace.task import (
    TaskCreate,
    TaskUpdate,
    TaskResponse,
    TaskListResponse
)
from services.executors.workspace.task_executor import TaskExecutor
from services.workflow.workflow_tracker import WorkflowTracker


class TaskWorkflowError(Exception):
    """Custom exception for workflow-specific errors"""
    pass


class TaskWorkflow:
    """
    Orchestrates task-related workflows, handling operation validation,
    execution tracking, and coordination between services.
    """

    def __init__(
            self,
            session: Session = Depends(get_session),
            tracker: Optional[WorkflowTracker] = None
    ):
        self.session = session
        self.executor = TaskExecutor(session)
        self.tracker = tracker or WorkflowTracker()

    async def _handle_workflow_error(
            self,
            workflow_id: Optional[str],
            error: Exception,
            operation: TaskOperation
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

    async def create_task(
            self, data: TaskCreate, user_id: UUID, user_permissions: List[str]
    ) -> TaskResponse:
        """Workflow for task creation."""
        if not validate_operation_constraints(TaskOperation.CREATE_TASK, user_permissions):
            raise HTTPException(status_code=403, detail="Insufficient permissions")

        workflow_id = None
        try:
            workflow_id = await self.tracker.start_workflow(
                operation=TaskOperation.CREATE_TASK,
                user_id=user_id,
                metadata={"project_id": str(data.project_id)}
            )

            task = await self.executor.create_task(data, user_id)

            await self.tracker.complete_workflow(
                workflow_id,
                metadata={"task_id": str(task.task_id)}
            )

            response = TaskResponse(
                **task.dict(),
                is_overdue=task.is_overdue()
            )
            return response

        except Exception as e:
            await self._handle_workflow_error(workflow_id, e, TaskOperation.CREATE_TASK)

    async def update_task(
            self,
            task_id: UUID,
            data: TaskUpdate,
            user_id: UUID,
            user_permissions: List[str]
    ) -> TaskResponse:
        """Workflow for task updates."""
        if not validate_operation_constraints(TaskOperation.UPDATE_TASK, user_permissions):
            raise HTTPException(status_code=403, detail="Insufficient permissions")

        workflow_id = None
        try:
            workflow_id = await self.tracker.start_workflow(
                operation=TaskOperation.UPDATE_TASK,
                user_id=user_id,
                metadata={"task_id": str(task_id)}
            )

            task = await self.executor.update_task(task_id, data, user_id)

            await self.tracker.complete_workflow(workflow_id)

            response = TaskResponse(
                **task.dict(),
                is_overdue=task.is_overdue()
            )
            return response

        except Exception as e:
            await self._handle_workflow_error(workflow_id, e, TaskOperation.UPDATE_TASK)

    async def complete_task(
            self,
            task_id: UUID,
            user_id: UUID,
            user_permissions: List[str]
    ) -> TaskResponse:
        """Workflow for completing a task."""
        if not validate_operation_constraints(TaskOperation.COMPLETE_TASK, user_permissions):
            raise HTTPException(status_code=403, detail="Insufficient permissions")

        workflow_id = None
        try:
            workflow_id = await self.tracker.start_workflow(
                operation=TaskOperation.COMPLETE_TASK,
                user_id=user_id,
                metadata={"task_id": str(task_id)}
            )

            task = await self.executor.complete_task(task_id, user_id)

            await self.tracker.complete_workflow(workflow_id)

            response = TaskResponse(
                **task.dict(),
                is_overdue=task.is_overdue()
            )
            return response

        except Exception as e:
            await self._handle_workflow_error(workflow_id, e, TaskOperation.COMPLETE_TASK)

    async def reopen_task(
            self,
            task_id: UUID,
            user_id: UUID,
            user_permissions: List[str]
    ) -> TaskResponse:
        """Workflow for reopening a task."""
        if not validate_operation_constraints(TaskOperation.REOPEN_TASK, user_permissions):
            raise HTTPException(status_code=403, detail="Insufficient permissions")

        workflow_id = None
        try:
            workflow_id = await self.tracker.start_workflow(
                operation=TaskOperation.REOPEN_TASK,
                user_id=user_id,
                metadata={"task_id": str(task_id)}
            )

            task = await self.executor.reopen_task(task_id, user_id)

            await self.tracker.complete_workflow(workflow_id)

            response = TaskResponse(
                **task.dict(),
                is_overdue=task.is_overdue()
            )
            return response

        except Exception as e:
            await self._handle_workflow_error(workflow_id, e, TaskOperation.REOPEN_TASK)

    async def delete_task(
            self,
            task_id: UUID,
            user_id: UUID,
            user_permissions: List[str]
    ) -> None:
        """Workflow for deleting a task."""
        if not validate_operation_constraints(TaskOperation.DELETE_TASK, user_permissions):
            raise HTTPException(status_code=403, detail="Insufficient permissions")

        workflow_id = None
        try:
            workflow_id = await self.tracker.start_workflow(
                operation=TaskOperation.DELETE_TASK,
                user_id=user_id,
                metadata={"task_id": str(task_id)}
            )

            await self.executor.delete_task(task_id)
            await self.tracker.complete_workflow(workflow_id)

        except Exception as e:
            await self._handle_workflow_error(workflow_id, e, TaskOperation.DELETE_TASK)

    async def get_task(
            self,
            task_id: UUID,
            user_id: UUID,
            user_permissions: List[str]
    ) -> TaskResponse:
        """Retrieves task details."""
        if not validate_operation_constraints(TaskOperation.GET_TASK, user_permissions):
            raise HTTPException(status_code=403, detail="Insufficient permissions")

        try:
            task = await self.executor.get_task(task_id)
            response = TaskResponse(
                **task.dict(),
                is_overdue=task.is_overdue()
            )
            return response

        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error retrieving task: {str(e)}"
            )

    async def list_project_tasks(
            self,
            project_id: UUID,
            user_id: UUID,
            user_permissions: List[str],
            status: Optional[TaskStatus] = None
    ) -> List[TaskListResponse]:
        """Lists all tasks for a specific project."""
        if not validate_operation_constraints(TaskOperation.LIST_PROJECT_TASKS, user_permissions):
            raise HTTPException(status_code=403, detail="Insufficient permissions")

        try:
            tasks = await self.executor.get_project_tasks(project_id, status)
            return [
                TaskListResponse(
                    **task.dict(),
                    is_overdue=task.is_overdue()
                )
                for task in tasks
            ]

        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error listing project tasks: {str(e)}"
            )