# api/routes/longterm_memory/conversational_history.py

from fastapi import APIRouter, HTTPException
from models.domain.longterm_memory.operations_conversational_history import (
    ConversationalHistoryOperation,
    ConversationalHistoryOperationInput,
    ConversationalHistoryOperationOutput
)
from services.workflow.longterm_memory.conversational_history_workflow import (
    ConversationalHistoryWorkflow
)
from typing import Dict, Optional
from uuid import UUID


router = APIRouter(
    prefix="/longterm-memory/conversational-history",
    tags=["longterm_memory"]
)


@router.get("/{vp_id}")
async def get_conversational_history(vp_id: UUID) -> Dict:
    """Get conversational history for a specific VP."""
    workflow = ConversationalHistoryWorkflow()
    operation_input = ConversationalHistoryOperationInput(
        operation=ConversationalHistoryOperation.GET,
        vp_id=vp_id
    )
    result = await workflow.process_operation(operation_input)
    if not result.success:
        raise HTTPException(status_code=404, detail=result.error)
    return result.data


@router.post("/")
async def create_conversational_history(
    vp_id: UUID,
    summary: str,
    context: str,
    interaction_count: Optional[int] = 0
) -> Dict:
    """Create new conversational history."""
    workflow = ConversationalHistoryWorkflow()
    operation_input = ConversationalHistoryOperationInput(
        operation=ConversationalHistoryOperation.CREATE,
        vp_id=vp_id,
        summary=summary,
        context=context,
        interaction_count=interaction_count
    )
    result = await workflow.process_operation(operation_input)
    if not result.success:
        raise HTTPException(status_code=400, detail=result.error)
    return result.data


@router.put("/{vp_id}")
async def update_conversational_history(
    vp_id: UUID,
    summary: Optional[str] = None,
    context: Optional[str] = None,
    interaction_count: Optional[int] = None
) -> Dict:
    """Update existing conversational history."""
    workflow = ConversationalHistoryWorkflow()
    operation_input = ConversationalHistoryOperationInput(
        operation=ConversationalHistoryOperation.UPDATE,
        vp_id=vp_id,
        summary=summary,
        context=context,
        interaction_count=interaction_count
    )
    result = await workflow.process_operation(operation_input)
    if not result.success:
        raise HTTPException(status_code=404, detail=result.error)
    return result.data


@router.delete("/{vp_id}")
async def delete_conversational_history(vp_id: UUID) -> Dict:
    """Delete conversational history."""
    workflow = ConversationalHistoryWorkflow()
    operation_input = ConversationalHistoryOperationInput(
        operation=ConversationalHistoryOperation.DELETE,
        vp_id=vp_id
    )
    result = await workflow.process_operation(operation_input)
    if not result.success:
        raise HTTPException(status_code=404, detail=result.error)
    return {"success": True}