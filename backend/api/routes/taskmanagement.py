# backend/api/routes/taskmanagement.py
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session
from typing import List

from core.database import get_session
from models.schemas.ability_taskmanagement import (
    TaskManagementAbilityCreate,
    TaskManagementAbilityUpdate,
    TaskManagementAbilityInDB
)
from services.workflow.taskmanagement_workflow import TaskManagementWorkflow, WorkflowContext
from services.executors.taskmanagement_executor import TaskManagementExecutor

router = APIRouter(prefix="/api/v1/tasks", tags=["tasks"])


@router.post("/", response_model=dict)
async def create_task(
        task_data: dict,
        session: Session = Depends(get_session),
        current_user_id: int = Depends(get_current_user)  # TODO: Implement auth dependency
):
    executor = TaskManagementExecutor(session)
    workflow = TaskManagementWorkflow(executor)

    context = WorkflowContext(
        operation_name="CREATE_TASK",
        input_data=task_data,
        user_id=current_user_id
    )

    result = await workflow.execute_workflow(context)
    if result["status"] == "error":
        raise HTTPException(status_code=400, detail=result["error"])

    return result["data"]


@router.get("/{task_id}", response_model=dict)
async def get_task(
        task_id: int,
        session: Session = Depends(get_session),
        current_user_id: int = Depends(get_current_user)  # TODO: Implement auth dependency
):
    executor = TaskManagementExecutor(session)
    workflow = TaskManagementWorkflow(executor)

    context = WorkflowContext(
        operation_name="GET_TASK",
        input_data={"task_id": task_id},
        user_id=current_user_id
    )

    result = await workflow.execute_workflow(context)
    if result["status"] == "error":
        raise HTTPException(status_code=400, detail=result["error"])

    return result["data"]


@router.get("/", response_model=dict)
async def list_tasks(
        status: str = None,
        priority: str = None,
        page: int = 1,
        page_size: int = 20,
        session: Session = Depends(get_session),
        current_user_id: int = Depends(get_current_user)  # TODO: Implement auth dependency
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

    result = await workflow.execute_workflow(context)
    if result["status"] == "error":
        raise HTTPException(status_code=400, detail=result["error"])

    return result["data"]