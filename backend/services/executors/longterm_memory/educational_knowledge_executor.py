# services/executors/longterm_memory/educational_knowledge_executor.py

import uuid
from typing import Optional, Dict, List
from models.domain.longterm_memory.operations_educational_knowledge import (
    EducationalKnowledgeOperation,
    EducationalKnowledgeOperationInput,
    EducationalKnowledgeOperationOutput
)
from models.database.longterm_memory.educational_knowledge import EducationalKnowledge, EducationType
from core.database import get_session
from sqlmodel import select


class EducationalKnowledgeExecutor:
    """Executor for educational knowledge operations."""

    def __init__(self):
        self.session = next(get_session())

    async def execute(
            self,
            operation_input: EducationalKnowledgeOperationInput
    ) -> EducationalKnowledgeOperationOutput:
        """Execute educational knowledge operation based on input."""
        try:
            if operation_input.operation == EducationalKnowledgeOperation.GET:
                return await self._get_educational_knowledge(
                    operation_input.vp_id,
                    operation_input.education_type
                )
            elif operation_input.operation == EducationalKnowledgeOperation.GET_ALL:
                return await self._get_all_educational_knowledge(operation_input.vp_id)
            elif operation_input.operation == EducationalKnowledgeOperation.CREATE:
                return await self._create_educational_knowledge(
                    operation_input.vp_id,
                    operation_input.education_type,
                    operation_input.prompt
                )
            elif operation_input.operation == EducationalKnowledgeOperation.UPDATE:
                return await self._update_educational_knowledge(
                    operation_input.vp_id,
                    operation_input.education_type,
                    operation_input.prompt
                )
            elif operation_input.operation == EducationalKnowledgeOperation.DELETE:
                return await self._delete_educational_knowledge(
                    operation_input.vp_id,
                    operation_input.education_type
                )

        except Exception as e:
            return EducationalKnowledgeOperationOutput(
                success=False,
                error=str(e)
            )

    async def _get_educational_knowledge(
            self,
            vp_id: uuid.UUID,
            education_type: EducationType
    ) -> EducationalKnowledgeOperationOutput:
        """Get specific educational knowledge for a VP."""
        query = select(EducationalKnowledge).where(
            EducationalKnowledge.vp_id == vp_id,
            EducationalKnowledge.education_type == education_type
        )
        result = self.session.exec(query).first()
        if not result:
            return EducationalKnowledgeOperationOutput(
                success=False,
                error=f"Educational knowledge of type {education_type} not found"
            )
        return EducationalKnowledgeOperationOutput(
            success=True,
            data=result.dict()
        )

    async def _get_all_educational_knowledge(
            self,
            vp_id: uuid.UUID
    ) -> EducationalKnowledgeOperationOutput:
        """Get all educational knowledge for a VP."""
        query = select(EducationalKnowledge).where(EducationalKnowledge.vp_id == vp_id)
        results = self.session.exec(query).all()
        if not results:
            return EducationalKnowledgeOperationOutput(
                success=False,
                error="No educational knowledge found"
            )
        return EducationalKnowledgeOperationOutput(
            success=True,
            data_list=[result.dict() for result in results]
        )

    async def _create_educational_knowledge(
            self,
            vp_id: uuid.UUID,
            education_type: EducationType,
            prompt: str
    ) -> EducationalKnowledgeOperationOutput:
        """Create new educational knowledge."""
        educational_knowledge = EducationalKnowledge(
            vp_id=vp_id,
            education_type=education_type,
            prompt=prompt
        )
        self.session.add(educational_knowledge)
        self.session.commit()
        self.session.refresh(educational_knowledge)
        return EducationalKnowledgeOperationOutput(
            success=True,
            data=educational_knowledge.dict()
        )

    async def _update_educational_knowledge(
            self,
            vp_id: uuid.UUID,
            education_type: EducationType,
            prompt: str
    ) -> EducationalKnowledgeOperationOutput:
        """Update existing educational knowledge."""
        query = select(EducationalKnowledge).where(
            EducationalKnowledge.vp_id == vp_id,
            EducationalKnowledge.education_type == education_type
        )
        result = self.session.exec(query).first()
        if not result:
            return EducationalKnowledgeOperationOutput(
                success=False,
                error=f"Educational knowledge of type {education_type} not found"
            )
        result.prompt = prompt
        self.session.commit()
        self.session.refresh(result)
        return EducationalKnowledgeOperationOutput(
            success=True,
            data=result.dict()
        )

    async def _delete_educational_knowledge(
            self,
            vp_id: uuid.UUID,
            education_type: EducationType
    ) -> EducationalKnowledgeOperationOutput:
        """Delete educational knowledge."""
        query = select(EducationalKnowledge).where(
            EducationalKnowledge.vp_id == vp_id,
            EducationalKnowledge.education_type == education_type
        )
        result = self.session.exec(query).first()
        if not result:
            return EducationalKnowledgeOperationOutput(
                success=False,
                error=f"Educational knowledge of type {education_type} not found"
            )
        self.session.delete(result)
        self.session.commit()
        return EducationalKnowledgeOperationOutput(success=True)