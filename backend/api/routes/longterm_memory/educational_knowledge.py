# api/routes/longterm_memory/educational_knowledge.py

from fastapi import APIRouter, HTTPException
import uuid
from models.domain.longterm_memory.operations_educational_knowledge import (
    EducationalKnowledgeOperation,
    EducationalKnowledgeOperationInput,
    EducationalKnowledgeOperationOutput
)
from models.database.longterm_memory.educational_knowledge import EducationType
from services.workflow.longterm_memory.educational_knowledge_workflow import EducationalKnowledgeWorkflow
from typing import Dict, List


router = APIRouter(prefix="/longterm-memory/educational-knowledge", tags=["longterm_memory"])


@router.get("/{vp_id}")
async def get_all_educational_knowledge(vp_id: uuid.UUID) -> List[Dict]:
    """Get all educational knowledge for a specific VP."""
    workflow = EducationalKnowledgeWorkflow()
    operation_input = EducationalKnowledgeOperationInput(
        operation=EducationalKnowledgeOperation.GET_ALL,
        vp_id=vp_id
    )
    result = await workflow.process_operation(operation_input)
    if not result.success:
        raise HTTPException(status_code=404, detail=result.error)
    return result.data_list


@router.get("/{vp_id}/{education_type}")
async def get_educational_knowledge(vp_id: uuid.UUID, education_type: EducationType) -> Dict:
    """Get specific educational knowledge for a VP."""
    workflow = EducationalKnowledgeWorkflow()
    operation_input = EducationalKnowledgeOperationInput(
        operation=EducationalKnowledgeOperation.GET,
        vp_id=vp_id,
        education_type=education_type
    )
    result = await workflow.process_operation(operation_input)
    if not result.success:
        raise HTTPException(status_code=404, detail=result.error)
    return result.data


@router.post("/")
async def create_educational_knowledge(
    vp_id: uuid.UUID,
    education_type: EducationType,
    prompt: str
) -> Dict:
    """Create new educational knowledge."""
    workflow = EducationalKnowledgeWorkflow()
    operation_input = EducationalKnowledgeOperationInput(
        operation=EducationalKnowledgeOperation.CREATE,
        vp_id=vp_id,
        education_type=education_type,
        prompt=prompt
    )
    result = await workflow.process_operation(operation_input)
    if not result.success:
        raise HTTPException(status_code=400, detail=result.error)
    return result.data


@router.put("/{vp_id}/{education_type}")
async def update_educational_knowledge(
    vp_id: uuid.UUID,
    education_type: EducationType,
    prompt: str
) -> Dict:
    """Update existing educational knowledge."""
    workflow = EducationalKnowledgeWorkflow()
    operation_input = EducationalKnowledgeOperationInput(
        operation=EducationalKnowledgeOperation.UPDATE,
        vp_id=vp_id,
        education_type=education_type,
        prompt=prompt
    )
    result = await workflow.process_operation(operation_input)
    if not result.success:
        raise HTTPException(status_code=404, detail=result.error)
    return result.data


@router.delete("/{vp_id}/{education_type}")
async def delete_educational_knowledge(vp_id: uuid.UUID, education_type: EducationType) -> Dict:
    """Delete educational knowledge."""
    workflow = EducationalKnowledgeWorkflow()
    operation_input = EducationalKnowledgeOperationInput(
        operation=EducationalKnowledgeOperation.DELETE,
        vp_id=vp_id,
        education_type=education_type
    )
    result = await workflow.process_operation(operation_input)
    if not result.success:
        raise HTTPException(status_code=404, detail=result.error)
    return {"success": True}