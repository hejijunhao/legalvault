# models/domain/longterm_memory/operations_actions_history.py

from enum import Enum
from typing import Optional, Dict
from pydantic import BaseModel
from uuid import UUID


class ActionsHistoryOperation(str, Enum):
   """Enumeration of possible actions history operations."""
   GET = "get"
   CREATE = "create"
   UPDATE = "update"
   DELETE = "delete"

   @property
   def requires_prompts(self) -> bool:
       """Check if operation requires prompts."""
       return self in [self.CREATE, self.UPDATE]


class ActionsHistoryOperationInput(BaseModel):
   """Input schema for actions history operations."""
   operation: ActionsHistoryOperation
   vp_id: UUID
   summary: Optional[str] = None
   context: Optional[str] = None
   action_count: Optional[int] = None


class ActionsHistoryOperationOutput(BaseModel):
   """Output schema for actions history operations."""
   success: bool
   data: Optional[Dict] = None
   error: Optional[str] = None