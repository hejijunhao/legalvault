# backend/api/routes/workspace/notebook.py

from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session

from core.database import get_session
from models.schemas.workspace.notebook import (
    NotebookCreate,
    NotebookUpdate,
    NotebookContentUpdate,
    NotebookResponse,
    NotebookListResponse
)
from services.workflow.workspace.notebook_workflow import NotebookWorkflow
from core.auth import get_current_user, get_user_permissions

router = APIRouter(
    prefix="/workspace/notebooks",
    tags=["notebooks"]
)


@router.post("/{project_id}", response_model=NotebookResponse)
async def create_notebook(
    project_id: UUID,
    data: NotebookCreate,
    current_user: UUID = Depends(get_current_user),
    user_permissions: List[str] = Depends(get_user_permissions),
    session: Session = Depends(get_session)
):
    """
    Create a new notebook for a project.
    """
    workflow = NotebookWorkflow(session)
    return await workflow.create_notebook(project_id, data, current_user, user_permissions)


@router.get("/{notebook_id}", response_model=NotebookResponse)
async def get_notebook(
    notebook_id: UUID,
    current_user: UUID = Depends(get_current_user),
    user_permissions: List[str] = Depends(get_user_permissions),
    session: Session = Depends(get_session)
):
    """
    Get notebook details by ID.
    """
    workflow = NotebookWorkflow(session)
    return await workflow.get_notebook(notebook_id, current_user, user_permissions)


@router.get("/project/{project_id}", response_model=Optional[NotebookResponse])
async def get_project_notebook(
    project_id: UUID,
    current_user: UUID = Depends(get_current_user),
    user_permissions: List[str] = Depends(get_user_permissions),
    session: Session = Depends(get_session)
):
    """
    Get a project's notebook.
    """
    workflow = NotebookWorkflow(session)
    return await workflow.get_project_notebook(project_id, current_user, user_permissions)


@router.patch("/{notebook_id}", response_model=NotebookResponse)
async def update_notebook(
    notebook_id: UUID,
    data: NotebookUpdate,
    current_user: UUID = Depends(get_current_user),
    user_permissions: List[str] = Depends(get_user_permissions),
    session: Session = Depends(get_session)
):
    """
    Update notebook properties.
    """
    workflow = NotebookWorkflow(session)
    return await workflow.update_notebook(notebook_id, data, current_user, user_permissions)


@router.put("/{notebook_id}/content", response_model=NotebookResponse)
async def update_notebook_content(
    notebook_id: UUID,
    data: NotebookContentUpdate,
    current_user: UUID = Depends(get_current_user),
    user_permissions: List[str] = Depends(get_user_permissions),
    session: Session = Depends(get_session)
):
    """
    Update notebook content.
    """
    workflow = NotebookWorkflow(session)
    return await workflow.update_content(notebook_id, data, current_user, user_permissions)


@router.post("/{notebook_id}/archive", response_model=NotebookResponse)
async def archive_notebook(
    notebook_id: UUID,
    current_user: UUID = Depends(get_current_user),
    user_permissions: List[str] = Depends(get_user_permissions),
    session: Session = Depends(get_session)
):
    """
    Archive a notebook.
    """
    workflow = NotebookWorkflow(session)
    return await workflow.archive_notebook(notebook_id, current_user, user_permissions)


@router.post("/{notebook_id}/unarchive", response_model=NotebookResponse)
async def unarchive_notebook(
    notebook_id: UUID,
    current_user: UUID = Depends(get_current_user),
    user_permissions: List[str] = Depends(get_user_permissions),
    session: Session = Depends(get_session)
):
    """
    Unarchive a notebook.
    """
    workflow = NotebookWorkflow(session)
    return await workflow.unarchive_notebook(notebook_id, current_user, user_permissions)


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