# services/executors/longterm_memory/actions_history_executor.py

from typing import Optional, Dict
from models.domain.longterm_memory.operations_actions_history import (
   ActionsHistoryOperation,
   ActionsHistoryOperationInput,
   ActionsHistoryOperationOutput
)
from models.database.longterm_memory.actions_history import ActionsHistory
from core.database import get_session
from sqlmodel import select
from datetime import datetime
from uuid import UUID


class ActionsHistoryExecutor:
   """Executor for actions history operations."""

   def __init__(self):
       self.session = next(get_session())

   async def execute(
           self,
           operation_input: ActionsHistoryOperationInput
   ) -> ActionsHistoryOperationOutput:
       """Execute actions history operation based on input."""
       try:
           if operation_input.operation == ActionsHistoryOperation.GET:
               return await self._get_actions_history(operation_input.vp_id)
           elif operation_input.operation == ActionsHistoryOperation.CREATE:
               return await self._create_actions_history(
                   operation_input.vp_id,
                   operation_input.summary,
                   operation_input.context,
                   operation_input.action_count
               )
           elif operation_input.operation == ActionsHistoryOperation.UPDATE:
               return await self._update_actions_history(
                   operation_input.vp_id,
                   operation_input.summary,
                   operation_input.context,
                   operation_input.action_count
               )
           elif operation_input.operation == ActionsHistoryOperation.DELETE:
               return await self._delete_actions_history(operation_input.vp_id)

       except Exception as e:
           return ActionsHistoryOperationOutput(
               success=False,
               error=str(e)
           )

   async def _get_actions_history(
           self,
           vp_id: UUID
   ) -> ActionsHistoryOperationOutput:
       """Get actions history for a specific VP."""
       query = select(ActionsHistory).where(
           ActionsHistory.vp_id == vp_id
       )
       result = self.session.exec(query).first()
       if not result:
           return ActionsHistoryOperationOutput(
               success=False,
               error="Actions history not found"
           )
       return ActionsHistoryOperationOutput(
           success=True,
           data=result.dict()
       )

   async def _create_actions_history(
           self,
           vp_id: UUID,
           summary: str,
           context: str,
           action_count: Optional[int] = 0
   ) -> ActionsHistoryOperationOutput:
       """Create new actions history."""
       actions_history = ActionsHistory(
           vp_id=vp_id,
           summary=summary,
           context=context,
           action_count=action_count,
           last_updated=datetime.utcnow()
       )
       self.session.add(actions_history)
       self.session.commit()
       self.session.refresh(actions_history)
       return ActionsHistoryOperationOutput(
           success=True,
           data=actions_history.dict()
       )

   async def _update_actions_history(
           self,
           vp_id: UUID,
           summary: Optional[str] = None,
           context: Optional[str] = None,
           action_count: Optional[int] = None
   ) -> ActionsHistoryOperationOutput:
       """Update existing actions history."""
       query = select(ActionsHistory).where(
           ActionsHistory.vp_id == vp_id
       )
       result = self.session.exec(query).first()
       if not result:
           return ActionsHistoryOperationOutput(
               success=False,
               error="Actions history not found"
           )

       if summary is not None:
           result.summary = summary
       if context is not None:
           result.context = context
       if action_count is not None:
           result.action_count = action_count

       result.last_updated = datetime.utcnow()
       self.session.commit()
       self.session.refresh(result)
       return ActionsHistoryOperationOutput(
           success=True,
           data=result.dict()
       )

   async def _delete_actions_history(
           self,
           vp_id: UUID
   ) -> ActionsHistoryOperationOutput:
       """Delete actions history."""
       query = select(ActionsHistory).where(
           ActionsHistory.vp_id == vp_id
       )
       result = self.session.exec(query).first()
       if not result:
           return ActionsHistoryOperationOutput(
               success=False,
               error="Actions history not found"
           )
       self.session.delete(result)
       self.session.commit()
       return ActionsHistoryOperationOutput(success=True)