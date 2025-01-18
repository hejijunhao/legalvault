# api/routes/workspace/task.py

from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session

from core.database import get_session
from models.database.workspace.task import TaskStatus
from models.schemas.workspace.task import (
    TaskCreate,
    TaskUpdate,
    TaskResponse,
    TaskListResponse
)
from services.workflow.workspace.task_workflow import TaskWorkflow
from core.auth import get_current_user, get_user_permissions

router = APIRouter(
    prefix="/workspace/tasks",
    tags=["tasks"]
)


@router.post("/", response_model=TaskResponse)
async def create_task(
    data: TaskCreate,
    current_user: UUID = Depends(get_current_user),
    user_permissions: List[str] = Depends(get_user_permissions),
    session: Session = Depends(get_session)
):
    """
    Create a new task.
    """
    workflow = TaskWorkflow(session)
    return await workflow.create_task(data, current_user, user_permissions)


@router.get("/{task_id}", response_model=TaskResponse)
async def get_task(
    task_id: UUID,
    current_user: UUID = Depends(get_current_user),
    user_permissions: List[str] = Depends(get_user_permissions),
    session: Session = Depends(get_session)
):
    """
    Get task details by ID.
    """
    workflow = TaskWorkflow(session)
    return await workflow.get_task(task_id, current_user, user_permissions)


@router.get("/project/{project_id}", response_model=List[TaskListResponse])
async def list_project_tasks(
    project_id: UUID,
    status: Optional[TaskStatus] = Query(None, description="Filter by task status"),
    current_user: UUID = Depends(get_current_user),
    user_permissions: List[str] = Depends(get_user_permissions),
    session: Session = Depends(get_session)
):
    """
    List all tasks for a specific project with optional status filter.
    """
    workflow = TaskWorkflow(session)
    return await workflow.list_project_tasks(
        project_id,
        current_user,
        user_permissions,
        status=status
    )


@router.patch("/{task_id}", response_model=TaskResponse)
async def update_task(
    task_id: UUID,
    data: TaskUpdate,
    current_user: UUID = Depends(get_current_user),
    user_permissions: List[str] = Depends(get_user_permissions),
    session: Session = Depends(get_session)
):
    """
    Update task details.
    """
    workflow = TaskWorkflow(session)
    return await workflow.update_task(
        task_id,
        data,
        current_user,
        user_permissions
    )


@router.post("/{task_id}/complete", response_model=TaskResponse)
async def complete_task(
    task_id: UUID,
    current_user: UUID = Depends(get_current_user),
    user_permissions: List[str] = Depends(get_user_permissions),
    session: Session = Depends(get_session)
):
    """
    Mark a task as completed.
    """
    workflow = TaskWorkflow(session)
    return await workflow.complete_task(
        task_id,
        current_user,
        user_permissions
    )


@router.post("/{task_id}/reopen", response_model=TaskResponse)
async def reopen_task(
    task_id: UUID,
    current_user: UUID = Depends(get_current_user),
    user_permissions: List[str] = Depends(get_user_permissions),
    session: Session = Depends(get_session)
):
    """
    Reopen a completed task.
    """
    workflow = TaskWorkflow(session)
    return await workflow.reopen_task(
        task_id,
        current_user,
        user_permissions
    )


@router.delete("/{task_id}")
async def delete_task(
    task_id: UUID,
    current_user: UUID = Depends(get_current_user),
    user_permissions: List[str] = Depends(get_user_permissions),
    session: Session = Depends(get_session)
):
    """
    Delete a task.
    """
    workflow = TaskWorkflow(session)
    await workflow.delete_task(task_id, current_user, user_permissions)
    return {"status": "success", "message": "Task deleted"}


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