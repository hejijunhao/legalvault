# services/executors/longterm_memory/global_knowledge_executor.py
import uuid
from typing import Optional, Dict, List
from models.domain.longterm_memory.operations_global_knowledge import (
    GlobalKnowledgeOperation,
    GlobalKnowledgeOperationInput,
    GlobalKnowledgeOperationOutput
)
from models.database.longterm_memory.global_knowledge import GlobalKnowledge, KnowledgeType
from core.database import get_session
from sqlmodel import select


class GlobalKnowledgeExecutor:
    """Executor for global knowledge operations."""

    def __init__(self):
        self.session = next(get_session())

    async def execute(
            self,
            operation_input: GlobalKnowledgeOperationInput
    ) -> GlobalKnowledgeOperationOutput:
        """Execute global knowledge operation based on input."""
        try:
            if operation_input.operation == GlobalKnowledgeOperation.GET:
                return await self._get_global_knowledge(
                    operation_input.vp_id,
                    operation_input.knowledge_type
                )
            elif operation_input.operation == GlobalKnowledgeOperation.GET_ALL:
                return await self._get_all_global_knowledge(operation_input.vp_id)
            elif operation_input.operation == GlobalKnowledgeOperation.CREATE:
                return await self._create_global_knowledge(
                    operation_input.vp_id,
                    operation_input.knowledge_type,
                    operation_input.prompt
                )
            elif operation_input.operation == GlobalKnowledgeOperation.UPDATE:
                return await self._update_global_knowledge(
                    operation_input.vp_id,
                    operation_input.knowledge_type,
                    operation_input.prompt
                )
            elif operation_input.operation == GlobalKnowledgeOperation.DELETE:
                return await self._delete_global_knowledge(
                    operation_input.vp_id,
                    operation_input.knowledge_type
                )

        except Exception as e:
            return GlobalKnowledgeOperationOutput(
                success=False,
                error=str(e)
            )

    async def _get_global_knowledge(
            self,
            vp_id: uuid.UUID,
            knowledge_type: KnowledgeType
    ) -> GlobalKnowledgeOperationOutput:
        """Get specific global knowledge for a VP."""
        query = select(GlobalKnowledge).where(
            GlobalKnowledge.vp_id == vp_id,
            GlobalKnowledge.knowledge_type == knowledge_type
        )
        result = self.session.exec(query).first()
        if not result:
            return GlobalKnowledgeOperationOutput(
                success=False,
                error=f"Global knowledge of type {knowledge_type} not found"
            )
        return GlobalKnowledgeOperationOutput(
            success=True,
            data=result.dict()
        )

    async def _get_all_global_knowledge(
            self,
            vp_id: uuid.UUID
    ) -> GlobalKnowledgeOperationOutput:
        """Get all global knowledge for a VP."""
        query = select(GlobalKnowledge).where(GlobalKnowledge.vp_id == vp_id)
        results = self.session.exec(query).all()
        if not results:
            return GlobalKnowledgeOperationOutput(
                success=False,
                error="No global knowledge found"
            )
        return GlobalKnowledgeOperationOutput(
            success=True,
            data_list=[result.dict() for result in results]
        )

    async def _create_global_knowledge(
            self,
            vp_id: uuid.UUID,
            knowledge_type: KnowledgeType,
            prompt: str
    ) -> GlobalKnowledgeOperationOutput:
        """Create new global knowledge."""
        global_knowledge = GlobalKnowledge(
            vp_id=vp_id,
            knowledge_type=knowledge_type,
            prompt=prompt
        )
        self.session.add(global_knowledge)
        self.session.commit()
        self.session.refresh(global_knowledge)
        return GlobalKnowledgeOperationOutput(
            success=True,
            data=global_knowledge.dict()
        )

    async def _update_global_knowledge(
            self,
            vp_id: uuid.UUID,
            knowledge_type: KnowledgeType,
            prompt: str
    ) -> GlobalKnowledgeOperationOutput:
        """Update existing global knowledge."""
        query = select(GlobalKnowledge).where(
            GlobalKnowledge.vp_id == vp_id,
            GlobalKnowledge.knowledge_type == knowledge_type
        )
        result = self.session.exec(query).first()
        if not result:
            return GlobalKnowledgeOperationOutput(
                success=False,
                error=f"Global knowledge of type {knowledge_type} not found"
            )
        result.prompt = prompt
        self.session.commit()
        self.session.refresh(result)
        return GlobalKnowledgeOperationOutput(
            success=True,
            data=result.dict()
        )

    async def _delete_global_knowledge(
            self,
            vp_id: uuid.UUID,
            knowledge_type: KnowledgeType
    ) -> GlobalKnowledgeOperationOutput:
        """Delete global knowledge."""
        query = select(GlobalKnowledge).where(
            GlobalKnowledge.vp_id == vp_id,
            GlobalKnowledge.knowledge_type == knowledge_type
        )
        result = self.session.exec(query).first()
        if not result:
            return GlobalKnowledgeOperationOutput(
                success=False,
                error=f"Global knowledge of type {knowledge_type} not found"
            )
        self.session.delete(result)
        self.session.commit()
        return GlobalKnowledgeOperationOutput(success=True)