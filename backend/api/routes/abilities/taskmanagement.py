# backend/api/routes/taskmanagement.py
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session
from typing import Optional

from core.database import get_session
from core.auth import get_current_user
from services.workflow.abilities.taskmanagement_workflow import TaskManagementWorkflow, WorkflowContext
from services.executors.abilities.taskmanagement_executor import TaskManagementExecutor

router = APIRouter(prefix="/api/v1/tasks", tags=["tasks"])


@router.post("/", response_model=dict)
def create_task(
        task_data: dict,
        session: Session = Depends(get_session),
        current_user_id: int = Depends(get_current_user)
):
    executor = TaskManagementExecutor(session)
    workflow = TaskManagementWorkflow(executor)

    context = WorkflowContext(
        operation_name="CREATE_TASK",
        input_data=task_data,
        user_id=current_user_id
    )

    result = workflow.execute_workflow(context)
    if result["status"] == "error":
        raise HTTPException(status_code=400, detail=result["error"])

    return result["data"]


@router.get("/{task_id}", response_model=dict)
def get_task(
        task_id: int,
        session: Session = Depends(get_session),
        current_user_id: int = Depends(get_current_user)
):
    executor = TaskManagementExecutor(session)
    workflow = TaskManagementWorkflow(executor)

    context = WorkflowContext(
        operation_name="GET_TASK",
        input_data={"task_id": task_id},
        user_id=current_user_id
    )

    result = workflow.execute_workflow(context)
    if result["status"] == "error":
        raise HTTPException(status_code=400, detail=result["error"])

    return result["data"]


@router.get("/", response_model=dict)
def list_tasks(
        status: Optional[str] = Query(
            None, 
            enum=["pending", "in_progress", "completed"],
            description="Filter tasks by status"
        ),
        priority: Optional[str] = Query(
            None, 
            enum=["low", "medium", "high"],
            description="Filter tasks by priority"
        ),
        page: int = Query(
            default=1, 
            ge=1,
            description="Page number"
        ),
        page_size: int = Query(
            default=20, 
            ge=1, 
            le=100,
            description="Number of items per page"
        ),
        session: Session = Depends(get_session),
        current_user_id: int = Depends(get_current_user)
):
    executor = TaskManagementExecutor(session)
    workflow = TaskManagementWorkflow(executor)

    context = WorkflowContext(
        operation_name="LIST_TASKS",
        input_data={
            "status": status,
            "priority": priority,
            "page": page,
            "page_size": page_size
        },
        user_id=current_user_id
    )

    result = workflow.execute_workflow(context)
    if result["status"] == "error":
        raise HTTPException(status_code=400, detail=result["error"])

    return result["data"]