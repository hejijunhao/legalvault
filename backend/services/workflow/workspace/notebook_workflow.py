# backend/services/workflow/workspace/notebook_workflow.py

from typing import List, Optional
from uuid import UUID
from fastapi import HTTPException, Depends
from sqlmodel import Session

from core.database import get_session
from models.domain.workspace.notebook import NotebookStateError
from models.permissions import (
    NotebookOperation,
    validate_notebook_operation as validate_operation_constraints
)
from models.schemas.workspace.notebook import (
    NotebookCreate,
    NotebookUpdate,
    NotebookContentUpdate,
    NotebookResponse,
    NotebookListResponse
)
from services.executors.workspace.notebook_executor import NotebookExecutor
from services.workflow.workflow_tracker import WorkflowTracker


class NotebookWorkflowError(Exception):
    """Custom exception for workflow-specific errors"""
    pass


class NotebookWorkflow:
    """
    Orchestrates notebook-related workflows, handling operation validation,
    execution tracking, and coordination between services.
    """

    def __init__(
            self,
            session: Session = Depends(get_session),
            tracker: Optional[WorkflowTracker] = None
    ):
        self.session = session
        self.executor = NotebookExecutor(session)
        self.tracker = tracker or WorkflowTracker()

    async def _handle_workflow_error(
            self,
            workflow_id: Optional[str],
            error: Exception,
            operation: NotebookOperation
    ) -> None:
        """Handles workflow errors consistently"""
        await self.session.rollback()  # Added transaction rollback

        if workflow_id:
            await self.tracker.fail_workflow(
                workflow_id,
                error_message=str(error),
                metadata={"operation": operation.value}
            )

        if isinstance(error, NotebookStateError):
            raise HTTPException(status_code=400, detail=str(error))
        elif isinstance(error, HTTPException):
            raise error
        else:
            raise HTTPException(status_code=500, detail="Internal workflow error")

    async def create_notebook(
            self,
            project_id: UUID,
            data: NotebookCreate,
            user_id: UUID,
            user_permissions: List[str]
    ) -> NotebookResponse:
        """
        Workflow for notebook creation.
        """
        if not validate_operation_constraints(NotebookOperation.CREATE_NOTEBOOK, user_permissions):
            raise HTTPException(status_code=403, detail="Insufficient permissions")

        workflow_id = None
        try:
            workflow_id = await self.tracker.start_workflow(
                operation=NotebookOperation.CREATE_NOTEBOOK,
                user_id=user_id,
                metadata={"project_id": str(project_id)}
            )

            notebook = await self.executor.create_notebook(project_id, data, user_id)
            await self.tracker.complete_workflow(
                workflow_id,
                metadata={"notebook_id": str(notebook.notebook_id)}
            )

            return NotebookResponse.from_orm(notebook)

        except Exception as e:
            await self._handle_workflow_error(workflow_id, e, NotebookOperation.CREATE_NOTEBOOK)

    async def update_notebook(
            self,
            notebook_id: UUID,
            data: NotebookUpdate,
            user_id: UUID,
            user_permissions: List[str]
    ) -> NotebookResponse:
        """
        Workflow for notebook updates.
        """
        if not validate_operation_constraints(NotebookOperation.UPDATE_CONTENT, user_permissions):
            raise HTTPException(status_code=403, detail="Insufficient permissions")

        workflow_id = None
        try:
            workflow_id = await self.tracker.start_workflow(
                operation=NotebookOperation.UPDATE_CONTENT,
                user_id=user_id,
                metadata={"notebook_id": str(notebook_id)}
            )

            notebook = await self.executor.update_notebook(notebook_id, data, user_id)
            await self.tracker.complete_workflow(workflow_id)

            return NotebookResponse.from_orm(notebook)

        except Exception as e:
            await self._handle_workflow_error(workflow_id, e, NotebookOperation.UPDATE_CONTENT)

    async def update_content(
            self,
            notebook_id: UUID,
            data: NotebookContentUpdate,
            user_id: UUID,
            user_permissions: List[str]
    ) -> NotebookResponse:
        """
        Workflow for updating notebook content.
        """
        if not validate_operation_constraints(NotebookOperation.UPDATE_CONTENT, user_permissions):
            raise HTTPException(status_code=403, detail="Insufficient permissions")

        workflow_id = None
        try:
            workflow_id = await self.tracker.start_workflow(
                operation=NotebookOperation.UPDATE_CONTENT,
                user_id=user_id,
                metadata={"notebook_id": str(notebook_id)}
            )

            notebook = await self.executor.update_content(notebook_id, data, user_id)
            await self.tracker.complete_workflow(workflow_id)

            return NotebookResponse.from_orm(notebook)

        except Exception as e:
            await self._handle_workflow_error(workflow_id, e, NotebookOperation.UPDATE_CONTENT)

    async def archive_notebook(
            self,
            notebook_id: UUID,
            user_id: UUID,
            user_permissions: List[str]
    ) -> NotebookResponse:
        """
        Workflow for archiving a notebook.
        """
        if not validate_operation_constraints(NotebookOperation.ARCHIVE_NOTEBOOK, user_permissions):
            raise HTTPException(status_code=403, detail="Insufficient permissions")

        workflow_id = None
        try:
            workflow_id = await self.tracker.start_workflow(
                operation=NotebookOperation.ARCHIVE_NOTEBOOK,
                user_id=user_id,
                metadata={"notebook_id": str(notebook_id)}
            )

            notebook = await self.executor.archive_notebook(notebook_id, user_id)
            await self.tracker.complete_workflow(workflow_id)

            return NotebookResponse.from_orm(notebook)

        except Exception as e:
            await self._handle_workflow_error(workflow_id, e, NotebookOperation.ARCHIVE_NOTEBOOK)

    async def unarchive_notebook(
            self,
            notebook_id: UUID,
            user_id: UUID,
            user_permissions: List[str]
    ) -> NotebookResponse:
        """
        Workflow for unarchiving a notebook.
        """
        if not validate_operation_constraints(NotebookOperation.UNARCHIVE_NOTEBOOK, user_permissions):
            raise HTTPException(status_code=403, detail="Insufficient permissions")

        workflow_id = None
        try:
            workflow_id = await self.tracker.start_workflow(
                operation=NotebookOperation.UNARCHIVE_NOTEBOOK,
                user_id=user_id,
                metadata={"notebook_id": str(notebook_id)}
            )

            notebook = await self.executor.unarchive_notebook(notebook_id, user_id)
            await self.tracker.complete_workflow(workflow_id)

            return NotebookResponse.from_orm(notebook)

        except Exception as e:
            await self._handle_workflow_error(workflow_id, e, NotebookOperation.UNARCHIVE_NOTEBOOK)

    async def get_project_notebook(
            self,
            project_id: UUID,
            user_id: UUID,
            user_permissions: List[str]
    ) -> Optional[NotebookResponse]:
        """
        Workflow for retrieving a project's notebook.
        """
        if not validate_operation_constraints(NotebookOperation.GET_NOTEBOOK, user_permissions):
            raise HTTPException(status_code=403, detail="Insufficient permissions")

        try:
            notebook = await self.executor.get_project_notebook(project_id)
            if notebook:
                return NotebookResponse.from_orm(notebook)
            return None

        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error retrieving notebook: {str(e)}"
            )