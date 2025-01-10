# models/domain/longterm_memory/operations_self_identity.py

from enum import Enum
from typing import Optional, Dict
from pydantic import BaseModel


class SelfIdentityOperation(str, Enum):
    """Enumeration of possible self-identity operations."""
    GET = "get"
    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"

    @property
    def requires_prompt(self) -> bool:
        """Check if operation requires a prompt."""
        return self in [self.CREATE, self.UPDATE]


class SelfIdentityOperationInput(BaseModel):
    """Input schema for self-identity operations."""
    operation: SelfIdentityOperation
    vp_id: int
    prompt: Optional[str] = None


class SelfIdentityOperationOutput(BaseModel):
    """Output schema for self-identity operations."""
    success: bool
    data: Optional[Dict] = None
    error: Optional[str] = None