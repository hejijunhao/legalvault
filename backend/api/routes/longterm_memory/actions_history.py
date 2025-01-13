# api/routes/longterm_memory/actions_history.py

from fastapi import APIRouter, HTTPException
from models.domain.longterm_memory.operations_actions_history import (
    ActionsHistoryOperation,
    ActionsHistoryOperationInput,
    ActionsHistoryOperationOutput
)
from services.workflow.longterm_memory.actions_history_workflow import (
    ActionsHistoryWorkflow
)
from typing import Dict, Optional
from uuid import UUID


router = APIRouter(
    prefix="/longterm-memory/actions-history",
    tags=["longterm_memory"]
)


@router.get("/{vp_id}")
async def get_actions_history(vp_id: UUID) -> Dict:
    """Get actions history for a specific VP."""
    workflow = ActionsHistoryWorkflow()
    operation_input = ActionsHistoryOperationInput(
        operation=ActionsHistoryOperation.GET,
        vp_id=vp_id
    )
    result = await workflow.process_operation(operation_input)
    if not result.success:
        raise HTTPException(status_code=404, detail=result.error)
    return result.data


@router.post("/")
async def create_actions_history(
    vp_id: UUID,
    summary: str,
    context: str,
    action_count: Optional[int] = 0
) -> Dict:
    """Create new actions history."""
    workflow = ActionsHistoryWorkflow()
    operation_input = ActionsHistoryOperationInput(
        operation=ActionsHistoryOperation.CREATE,
        vp_id=vp_id,
        summary=summary,
        context=context,
        action_count=action_count
    )
    result = await workflow.process_operation(operation_input)
    if not result.success:
        raise HTTPException(status_code=400, detail=result.error)
    return result.data


@router.put("/{vp_id}")
async def update_actions_history(
    vp_id: UUID,
    summary: Optional[str] = None,
    context: Optional[str] = None,
    action_count: Optional[int] = None
) -> Dict:
    """Update existing actions history."""
    workflow = ActionsHistoryWorkflow()
    operation_input = ActionsHistoryOperationInput(
        operation=ActionsHistoryOperation.UPDATE,
        vp_id=vp_id,
        summary=summary,
        context=context,
        action_count=action_count
    )
    result = await workflow.process_operation(operation_input)
    if not result.success:
        raise HTTPException(status_code=404, detail=result.error)
    return result.data


@router.delete("/{vp_id}")
async def delete_actions_history(vp_id: UUID) -> Dict:
    """Delete actions history."""
    workflow = ActionsHistoryWorkflow()
    operation_input = ActionsHistoryOperationInput(
        operation=ActionsHistoryOperation.DELETE,
        vp_id=vp_id
    )
    result = await workflow.process_operation(operation_input)
    if not result.success:
        raise HTTPException(status_code=404, detail=result.error)
    return {"success": True}