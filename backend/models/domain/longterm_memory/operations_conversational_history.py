# models/domain/longterm_memory/operations_conversational_history.py

from enum import Enum
from typing import Optional, Dict
from pydantic import BaseModel
from uuid import UUID


class ConversationalHistoryOperation(str, Enum):
    """Enumeration of possible conversational history operations."""
    GET = "get"
    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"

    @property
    def requires_prompts(self) -> bool:
        """Check if operation requires prompts."""
        return self in [self.CREATE, self.UPDATE]


class ConversationalHistoryOperationInput(BaseModel):
    """Input schema for conversational history operations."""
    operation: ConversationalHistoryOperation
    vp_id: UUID
    summary: Optional[str] = None
    context: Optional[str] = None
    interaction_count: Optional[int] = None


class ConversationalHistoryOperationOutput(BaseModel):
    """Output schema for conversational history operations."""
    success: bool
    data: Optional[Dict] = None
    error: Optional[str] = None