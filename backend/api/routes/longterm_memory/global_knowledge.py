# api/routes/longterm_memory/global_knowledge.py

from fastapi import APIRouter, HTTPException
import uuid
from models.domain.longterm_memory.operations_global_knowledge import (
    GlobalKnowledgeOperation,
    GlobalKnowledgeOperationInput,
    GlobalKnowledgeOperationOutput
)
from models.database.longterm_memory.global_knowledge import KnowledgeType
from services.workflow.longterm_memory.global_knowledge_workflow import GlobalKnowledgeWorkflow
from typing import Dict, List


router = APIRouter(prefix="/longterm-memory/global-knowledge", tags=["longterm_memory"])


@router.get("/{vp_id}")
async def get_all_global_knowledge(vp_id: uuid.UUID) -> Dict:
    """Get all global knowledge for a specific VP."""
    workflow = GlobalKnowledgeWorkflow()
    operation_input = GlobalKnowledgeOperationInput(
        operation=GlobalKnowledgeOperation.GET_ALL,
        vp_id=vp_id
    )
    result = await workflow.process_operation(operation_input)
    if not result.success:
        raise HTTPException(status_code=404, detail=result.error)
    return result.data_list


@router.get("/{vp_id}/{knowledge_type}")
async def get_global_knowledge(vp_id: uuid.UUID, knowledge_type: KnowledgeType) -> Dict:
    """Get specific global knowledge for a VP."""
    workflow = GlobalKnowledgeWorkflow()
    operation_input = GlobalKnowledgeOperationInput(
        operation=GlobalKnowledgeOperation.GET,
        vp_id=vp_id,
        knowledge_type=knowledge_type
    )
    result = await workflow.process_operation(operation_input)
    if not result.success:
        raise HTTPException(status_code=404, detail=result.error)
    return result.data


@router.post("/")
async def create_global_knowledge(vp_id: uuid.UUID, knowledge_type: KnowledgeType, prompt: str) -> Dict:
    """Create new global knowledge."""
    workflow = GlobalKnowledgeWorkflow()
    operation_input = GlobalKnowledgeOperationInput(
        operation=GlobalKnowledgeOperation.CREATE,
        vp_id=vp_id,
        knowledge_type=knowledge_type,
        prompt=prompt
    )
    result = await workflow.process_operation(operation_input)
    if not result.success:
        raise HTTPException(status_code=400, detail=result.error)
    return result.data


@router.put("/{vp_id}/{knowledge_type}")
async def update_global_knowledge(vp_id: uuid.UUID, knowledge_type: KnowledgeType, prompt: str) -> Dict:
    """Update existing global knowledge."""
    workflow = GlobalKnowledgeWorkflow()
    operation_input = GlobalKnowledgeOperationInput(
        operation=GlobalKnowledgeOperation.UPDATE,
        vp_id=vp_id,
        knowledge_type=knowledge_type,
        prompt=prompt
    )
    result = await workflow.process_operation(operation_input)
    if not result.success:
        raise HTTPException(status_code=404, detail=result.error)
    return result.data


@router.delete("/{vp_id}/{knowledge_type}")
async def delete_global_knowledge(vp_id: uuid.UUID, knowledge_type: KnowledgeType) -> Dict:
    """Delete global knowledge."""
    workflow = GlobalKnowledgeWorkflow()
    operation_input = GlobalKnowledgeOperationInput(
        operation=GlobalKnowledgeOperation.DELETE,
        vp_id=vp_id,
        knowledge_type=knowledge_type
    )
    result = await workflow.process_operation(operation_input)
    if not result.success:
        raise HTTPException(status_code=404, detail=result.error)
    return {"success": True}