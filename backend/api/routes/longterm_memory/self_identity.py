# api/routes/longterm_memory/self_identity.py

from fastapi import APIRouter, HTTPException
from models.domain.longterm_memory.operations_self_identity import (
    SelfIdentityOperation,
    SelfIdentityOperationInput,
    SelfIdentityOperationOutput
)
from services.workflow.longterm_memory.self_identity_workflow import SelfIdentityWorkflow
from typing import Dict


router = APIRouter(prefix="/longterm-memory/self-identity", tags=["longterm_memory"])


@router.get("/{vp_id}")
async def get_self_identity(vp_id: int) -> Dict:
    """Get self-identity for a specific VP."""
    workflow = SelfIdentityWorkflow()
    operation_input = SelfIdentityOperationInput(
        operation=SelfIdentityOperation.GET,
        vp_id=vp_id
    )
    result = await workflow.process_operation(operation_input)
    if not result.success:
        raise HTTPException(status_code=404, detail=result.error)
    return result.data


@router.post("/")
async def create_self_identity(vp_id: int, prompt: str) -> Dict:
    """Create new self-identity."""
    workflow = SelfIdentityWorkflow()
    operation_input = SelfIdentityOperationInput(
        operation=SelfIdentityOperation.CREATE,
        vp_id=vp_id,
        prompt=prompt
    )
    result = await workflow.process_operation(operation_input)
    if not result.success:
        raise HTTPException(status_code=400, detail=result.error)
    return result.data


@router.put("/{vp_id}")
async def update_self_identity(vp_id: int, prompt: str) -> Dict:
    """Update existing self-identity."""
    workflow = SelfIdentityWorkflow()
    operation_input = SelfIdentityOperationInput(
        operation=SelfIdentityOperation.UPDATE,
        vp_id=vp_id,
        prompt=prompt
    )
    result = await workflow.process_operation(operation_input)
    if not result.success:
        raise HTTPException(status_code=404, detail=result.error)
    return result.data


@router.delete("/{vp_id}")
async def delete_self_identity(vp_id: int) -> Dict:
    """Delete self-identity."""
    workflow = SelfIdentityWorkflow()
    operation_input = SelfIdentityOperationInput(
        operation=SelfIdentityOperation.DELETE,
        vp_id=vp_id
    )
    result = await workflow.process_operation(operation_input)
    if not result.success:
        raise HTTPException(status_code=404, detail=result.error)
    return {"success": True}