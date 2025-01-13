# services/executors/longterm_memory/conversational_history_executor.py

from typing import Optional, Dict
from models.domain.longterm_memory.operations_conversational_history import (
    ConversationalHistoryOperation,
    ConversationalHistoryOperationInput,
    ConversationalHistoryOperationOutput
)
from models.database.longterm_memory.conversational_history import ConversationalHistory
from core.database import get_session
from sqlmodel import select
from datetime import datetime
from uuid import UUID


class ConversationalHistoryExecutor:
    """Executor for conversational history operations."""

    def __init__(self):
        self.session = next(get_session())

    async def execute(
            self,
            operation_input: ConversationalHistoryOperationInput
    ) -> ConversationalHistoryOperationOutput:
        """Execute conversational history operation based on input."""
        try:
            if operation_input.operation == ConversationalHistoryOperation.GET:
                return await self._get_conversational_history(operation_input.vp_id)
            elif operation_input.operation == ConversationalHistoryOperation.CREATE:
                return await self._create_conversational_history(
                    operation_input.vp_id,
                    operation_input.summary,
                    operation_input.context,
                    operation_input.interaction_count
                )
            elif operation_input.operation == ConversationalHistoryOperation.UPDATE:
                return await self._update_conversational_history(
                    operation_input.vp_id,
                    operation_input.summary,
                    operation_input.context,
                    operation_input.interaction_count
                )
            elif operation_input.operation == ConversationalHistoryOperation.DELETE:
                return await self._delete_conversational_history(operation_input.vp_id)

        except Exception as e:
            return ConversationalHistoryOperationOutput(
                success=False,
                error=str(e)
            )

    async def _get_conversational_history(
            self,
            vp_id: UUID
    ) -> ConversationalHistoryOperationOutput:
        """Get conversational history for a specific VP."""
        query = select(ConversationalHistory).where(
            ConversationalHistory.vp_id == vp_id
        )
        result = self.session.exec(query).first()
        if not result:
            return ConversationalHistoryOperationOutput(
                success=False,
                error="Conversational history not found"
            )
        return ConversationalHistoryOperationOutput(
            success=True,
            data=result.dict()
        )

    async def _create_conversational_history(
            self,
            vp_id: UUID,
            summary: str,
            context: str,
            interaction_count: Optional[int] = 0
    ) -> ConversationalHistoryOperationOutput:
        """Create new conversational history."""
        conv_history = ConversationalHistory(
            vp_id=vp_id,
            summary=summary,
            context=context,
            interaction_count=interaction_count,
            last_updated=datetime.utcnow()
        )
        self.session.add(conv_history)
        self.session.commit()
        self.session.refresh(conv_history)
        return ConversationalHistoryOperationOutput(
            success=True,
            data=conv_history.dict()
        )

    async def _update_conversational_history(
            self,
            vp_id: UUID,
            summary: Optional[str] = None,
            context: Optional[str] = None,
            interaction_count: Optional[int] = None
    ) -> ConversationalHistoryOperationOutput:
        """Update existing conversational history."""
        query = select(ConversationalHistory).where(
            ConversationalHistory.vp_id == vp_id
        )
        result = self.session.exec(query).first()
        if not result:
            return ConversationalHistoryOperationOutput(
                success=False,
                error="Conversational history not found"
            )

        if summary is not None:
            result.summary = summary
        if context is not None:
            result.context = context
        if interaction_count is not None:
            result.interaction_count = interaction_count

        result.last_updated = datetime.utcnow()
        self.session.commit()
        self.session.refresh(result)
        return ConversationalHistoryOperationOutput(
            success=True,
            data=result.dict()
        )

    async def _delete_conversational_history(
            self,
            vp_id: UUID
    ) -> ConversationalHistoryOperationOutput:
        """Delete conversational history."""
        query = select(ConversationalHistory).where(
            ConversationalHistory.vp_id == vp_id
        )
        result = self.session.exec(query).first()
        if not result:
            return ConversationalHistoryOperationOutput(
                success=False,
                error="Conversational history not found"
            )
        self.session.delete(result)
        self.session.commit()
        return ConversationalHistoryOperationOutput(success=True)