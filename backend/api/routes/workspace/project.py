# api/routes/workspace/project.py

from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session

from core.database import get_session
from models.database.workspace.project import ProjectStatus
from models.schemas.workspace.project import (
    ProjectCreate,
    ProjectUpdate,
    ProjectKnowledgeUpdate,
    ProjectSummaryUpdate,
    ProjectResponse,
    ProjectListResponse
)
from services.workflow.workspace.project_workflow import ProjectWorkflow
from core.auth import get_current_user, get_user_permissions

router = APIRouter(
    prefix="/workspace/projects",
    tags=["projects"]
)

@router.post("/", response_model=ProjectResponse)
async def create_project(
    data: ProjectCreate,
    current_user: UUID = Depends(get_current_user),
    user_permissions: List[str] = Depends(get_user_permissions),
    session: Session = Depends(get_session)
):
    """
    Create a new project.
    """
    workflow = ProjectWorkflow(session)
    return await workflow.create_project(data, current_user, user_permissions)

@router.get("/{project_id}", response_model=ProjectResponse)
async def get_project(
    project_id: UUID,
    current_user: UUID = Depends(get_current_user),
    user_permissions: List[str] = Depends(get_user_permissions),
    session: Session = Depends(get_session)
):
    """
    Get project details by ID.
    """
    workflow = ProjectWorkflow(session)
    return await workflow.get_project(project_id, current_user, user_permissions)

@router.get("/", response_model=List[ProjectListResponse])
async def list_projects(
    status: Optional[ProjectStatus] = Query(None, description="Filter by project status"),
    practice_area: Optional[str] = Query(None, description="Filter by practice area"),
    current_user: UUID = Depends(get_current_user),
    user_permissions: List[str] = Depends(get_user_permissions),
    session: Session = Depends(get_session)
):
    """
    List all projects with optional filters.
    """
    workflow = ProjectWorkflow(session)
    return await workflow.list_projects(
        current_user,
        user_permissions,
        status=status,
        practice_area=practice_area
    )

@router.patch("/{project_id}", response_model=ProjectResponse)
async def update_project(
    project_id: UUID,
    data: ProjectUpdate,
    current_user: UUID = Depends(get_current_user),
    user_permissions: List[str] = Depends(get_user_permissions),
    session: Session = Depends(get_session)
):
    """
    Update project details.
    """
    workflow = ProjectWorkflow(session)
    return await workflow.update_project(project_id, data, current_user, user_permissions)

@router.put("/{project_id}/knowledge", response_model=ProjectResponse)
async def update_project_knowledge(
    project_id: UUID,
    data: ProjectKnowledgeUpdate,
    current_user: UUID = Depends(get_current_user),
    user_permissions: List[str] = Depends(get_user_permissions),
    session: Session = Depends(get_session)
):
    """
    Update project knowledge content.
    """
    workflow = ProjectWorkflow(session)
    return await workflow.update_knowledge(project_id, data, current_user, user_permissions)

@router.put("/{project_id}/summary", response_model=ProjectResponse)
async def update_project_summary(
    project_id: UUID,
    data: ProjectSummaryUpdate,
    current_user: UUID = Depends(get_current_user),
    user_permissions: List[str] = Depends(get_user_permissions),
    session: Session = Depends(get_session)
):
    """
    Update project summary.
    """
    workflow = ProjectWorkflow(session)
    return await workflow.update_summary(project_id, data, current_user, user_permissions)

@router.post("/{project_id}/archive", response_model=ProjectResponse)
async def archive_project(
    project_id: UUID,
    current_user: UUID = Depends(get_current_user),
    user_permissions: List[str] = Depends(get_user_permissions),
    session: Session = Depends(get_session)
):
    """
    Archive a project.
    """
    workflow = ProjectWorkflow(session)
    return await workflow.archive_project(project_id, current_user, user_permissions)

# Error Handlers
@router.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return {
        "status_code": exc.status_code,
        "detail": exc.detail
    }

@router.exception_handler(Exception)
async def general_exception_handler(request, exc):
    return {
        "status_code": 500,
        "detail": "Internal server error"
    }