# models/domain/longterm_memory/operations_global_knowledge.py
import uuid
from enum import Enum
from typing import Optional, Dict, List
from pydantic import BaseModel
from models.database.longterm_memory.global_knowledge import KnowledgeType


class GlobalKnowledgeOperation(str, Enum):
    """Enumeration of possible global knowledge operations."""
    GET = "get"
    GET_ALL = "get_all"  # New operation to get all knowledge types for a VP
    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"

    @property
    def requires_prompt(self) -> bool:
        """Check if operation requires a prompt."""
        return self in [self.CREATE, self.UPDATE]

    @property
    def requires_knowledge_type(self) -> bool:
        """Check if operation requires a knowledge type."""
        return self in [self.GET, self.CREATE, self.UPDATE, self.DELETE]


class GlobalKnowledgeOperationInput(BaseModel):
    """Input schema for global knowledge operations."""
    operation: GlobalKnowledgeOperation
    vp_id: uuid.UUID
    knowledge_type: Optional[KnowledgeType] = None
    prompt: Optional[str] = None


class GlobalKnowledgeOperationOutput(BaseModel):
    """Output schema for global knowledge operations."""
    success: bool
    data: Optional[Dict] = None
    data_list: Optional[List[Dict]] = None  # For GET_ALL operation
    error: Optional[str] = None