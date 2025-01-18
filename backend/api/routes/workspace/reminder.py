# api/routes/workspace/reminder.py

from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session

from core.database import get_session
from models.database.workspace.reminder import ReminderStatus
from models.schemas.workspace.reminder import (
    ReminderCreate,
    ReminderUpdate,
    ReminderResponse,
    ReminderListResponse
)
from services.workflow.workspace.reminder_workflow import ReminderWorkflow
from core.auth import get_current_user, get_user_permissions

router = APIRouter(
    prefix="/workspace/reminders",
    tags=["reminders"]
)

@router.post("/", response_model=ReminderResponse)
async def create_reminder(
    data: ReminderCreate,
    current_user: UUID = Depends(get_current_user),
    user_permissions: List[str] = Depends(get_user_permissions),
    session: Session = Depends(get_session)
):
    """
    Create a new reminder.
    """
    workflow = ReminderWorkflow(session)
    return await workflow.create_reminder(data, current_user, user_permissions)

@router.get("/{reminder_id}", response_model=ReminderResponse)
async def get_reminder(
    reminder_id: UUID,
    current_user: UUID = Depends(get_current_user),
    user_permissions: List[str] = Depends(get_user_permissions),
    session: Session = Depends(get_session)
):
    """
    Get reminder details by ID.
    """
    workflow = ReminderWorkflow(session)
    return await workflow.get_reminder(reminder_id, current_user, user_permissions)

@router.get("/project/{project_id}", response_model=List[ReminderListResponse])
async def list_project_reminders(
    project_id: UUID,
    status: Optional[ReminderStatus] = Query(None, description="Filter by reminder status"),
    current_user: UUID = Depends(get_current_user),
    user_permissions: List[str] = Depends(get_user_permissions),
    session: Session = Depends(get_session)
):
    """
    List all reminders for a specific project with optional status filter.
    """
    workflow = ReminderWorkflow(session)
    return await workflow.list_project_reminders(
        project_id,
        current_user,
        user_permissions,
        status=status
    )

@router.patch("/{reminder_id}", response_model=ReminderResponse)
async def update_reminder(
    reminder_id: UUID,
    data: ReminderUpdate,
    current_user: UUID = Depends(get_current_user),
    user_permissions: List[str] = Depends(get_user_permissions),
    session: Session = Depends(get_session)
):
    """
    Update reminder details.
    """
    workflow = ReminderWorkflow(session)
    return await workflow.update_reminder(
        reminder_id,
        data,
        current_user,
        user_permissions
    )

@router.post("/{reminder_id}/complete", response_model=ReminderResponse)
async def complete_reminder(
    reminder_id: UUID,
    current_user: UUID = Depends(get_current_user),
    user_permissions: List[str] = Depends(get_user_permissions),
    session: Session = Depends(get_session)
):
    """
    Mark a reminder as completed.
    """
    workflow = ReminderWorkflow(session)
    return await workflow.complete_reminder(
        reminder_id,
        current_user,
        user_permissions
    )

@router.delete("/{reminder_id}")
async def delete_reminder(
    reminder_id: UUID,
    current_user: UUID = Depends(get_current_user),
    user_permissions: List[str] = Depends(get_user_permissions),
    session: Session = Depends(get_session)
):
    """
    Delete a reminder.
    """
    workflow = ReminderWorkflow(session)
    await workflow.delete_reminder(reminder_id, current_user, user_permissions)
    return {"status": "success", "message": "Reminder deleted"}

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