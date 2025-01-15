# services/workflow/workspace/project_workflow.py

from typing import List, Optional
from uuid import UUID
from fastapi import HTTPException, Depends
from sqlmodel import Session

from core.database import get_session
from models.database.workspace.project import ProjectStatus
from models.domain.workspace.project import ProjectStateError
from models.domain.workspace.operations_project import (
    ProjectOperation,
    validate_operation_constraints
)
from models.schemas.workspace.project import (
    ProjectCreate,
    ProjectUpdate,
    ProjectKnowledgeUpdate,
    ProjectSummaryUpdate,
    ProjectResponse,
    ProjectListResponse
)
from services.executors.workspace.project_executor import ProjectExecutor
from services.workflow.workflow_tracker import WorkflowTracker


class ProjectWorkflowError(Exception):
    """Custom exception for workflow-specific errors"""
    pass


class ProjectWorkflow:
    """
    Orchestrates project-related workflows, handling operation validation,
    execution tracking, and coordination between services.
    """
    def __init__(
        self,
        session: Session = Depends(get_session),
        tracker: Optional[WorkflowTracker] = None
    ):
        self.session = session
        self.executor = ProjectExecutor(session)
        self.tracker = tracker or WorkflowTracker()

    async def _handle_workflow_error(
        self,
        workflow_id: Optional[str],
        error: Exception,
        operation: ProjectOperation
    ) -> None:
        """Handles workflow errors consistently"""
        if workflow_id:
            await self.tracker.fail_workflow(
                workflow_id,
                error_message=str(error),
                metadata={"operation": operation.value}
            )

        if isinstance(error, ProjectStateError):
            raise HTTPException(status_code=400, detail=str(error))
        elif isinstance(error, HTTPException):
            raise error
        else:
            raise HTTPException(status_code=500, detail="Internal workflow error")

    async def create_project(
        self, data: ProjectCreate, user_id: UUID, user_permissions: List[str]
    ) -> ProjectResponse:
        """
        Workflow for project creation.
        """
        if not validate_operation_constraints(ProjectOperation.CREATE_PROJECT, user_permissions):
            raise HTTPException(status_code=403, detail="Insufficient permissions")

        workflow_id = None
        try:
            workflow_id = await self.tracker.start_workflow(
                operation=ProjectOperation.CREATE_PROJECT,
                user_id=user_id,
                metadata={"project_name": data.name}
            )

            project = await self.executor.create_project(data, user_id)
            await self.tracker.complete_workflow(
                workflow_id,
                metadata={"project_id": str(project.project_id)}
            )

            return ProjectResponse.from_orm(project)

        except Exception as e:
            await self._handle_workflow_error(workflow_id, e, ProjectOperation.CREATE_PROJECT)

    async def update_project(
        self,
        project_id: UUID,
        data: ProjectUpdate,
        user_id: UUID,
        user_permissions: List[str]
    ) -> ProjectResponse:
        """
        Workflow for project updates.
        """
        if not validate_operation_constraints(ProjectOperation.UPDATE_PROJECT, user_permissions):
            raise HTTPException(status_code=403, detail="Insufficient permissions")

        workflow_id = None
        try:
            workflow_id = await self.tracker.start_workflow(
                operation=ProjectOperation.UPDATE_PROJECT,
                user_id=user_id,
                metadata={"project_id": str(project_id)}
            )

            project = await self.executor.update_project(project_id, data, user_id)
            await self.tracker.complete_workflow(workflow_id)

            return ProjectResponse.from_orm(project)

        except Exception as e:
            await self._handle_workflow_error(workflow_id, e, ProjectOperation.UPDATE_PROJECT)

    async def update_knowledge(
        self,
        project_id: UUID,
        data: ProjectKnowledgeUpdate,
        user_id: UUID,
        user_permissions: List[str]
    ) -> ProjectResponse:
        """
        Workflow for updating project knowledge.
        """
        if not validate_operation_constraints(ProjectOperation.UPDATE_KNOWLEDGE, user_permissions):
            raise HTTPException(status_code=403, detail="Insufficient permissions")

        workflow_id = None
        try:
            workflow_id = await self.tracker.start_workflow(
                operation=ProjectOperation.UPDATE_KNOWLEDGE,
                user_id=user_id,
                metadata={"project_id": str(project_id)}
            )

            project = await self.executor.update_knowledge(project_id, data, user_id)
            await self.tracker.complete_workflow(
                workflow_id,
                metadata={"content_length": len(data.content)}
            )

            return ProjectResponse.from_orm(project)

        except Exception as e:
            await self._handle_workflow_error(workflow_id, e, ProjectOperation.UPDATE_KNOWLEDGE)

    async def update_summary(
        self,
        project_id: UUID,
        data: ProjectSummaryUpdate,
        user_id: UUID,
        user_permissions: List[str]
    ) -> ProjectResponse:
        """
        Workflow for updating project summary.
        """
        if not validate_operation_constraints(ProjectOperation.UPDATE_SUMMARY, user_permissions):
            raise HTTPException(status_code=403, detail="Insufficient permissions")

        workflow_id = None
        try:
            workflow_id = await self.tracker.start_workflow(
                operation=ProjectOperation.UPDATE_SUMMARY,
                user_id=user_id,
                metadata={"project_id": str(project_id)}
            )

            project = await self.executor.update_summary(project_id, data, user_id)
            await self.tracker.complete_workflow(workflow_id)

            return ProjectResponse.from_orm(project)

        except Exception as e:
            await self._handle_workflow_error(workflow_id, e, ProjectOperation.UPDATE_SUMMARY)

    async def archive_project(
        self,
        project_id: UUID,
        user_id: UUID,
        user_permissions: List[str]
    ) -> ProjectResponse:
        """
        Workflow for archiving a project.
        """
        if not validate_operation_constraints(ProjectOperation.ARCHIVE_PROJECT, user_permissions):
            raise HTTPException(status_code=403, detail="Insufficient permissions")

        workflow_id = None
        try:
            workflow_id = await self.tracker.start_workflow(
                operation=ProjectOperation.ARCHIVE_PROJECT,
                user_id=user_id,
                metadata={"project_id": str(project_id)}
            )

            project = await self.executor.update_status(
                project_id,
                ProjectStatus.ARCHIVED,
                user_id
            )
            await self.tracker.complete_workflow(workflow_id)

            return ProjectResponse.from_orm(project)

        except Exception as e:
            await self._handle_workflow_error(workflow_id, e, ProjectOperation.ARCHIVE_PROJECT)

    async def list_projects(
        self,
        user_id: UUID,
        user_permissions: List[str],
        status: Optional[ProjectStatus] = None,
        practice_area: Optional[str] = None
    ) -> List[ProjectListResponse]:
        """
        Workflow for listing projects.
        """
        if not validate_operation_constraints(ProjectOperation.LIST_PROJECTS, user_permissions):
            raise HTTPException(status_code=403, detail="Insufficient permissions")

        try:
            projects = await self.executor.list_projects(
                user_id,
                status=status,
                practice_area=practice_area
            )
            return [ProjectListResponse.from_orm(p) for p in projects]

        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error listing projects: {str(e)}"
            )