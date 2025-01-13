# models/domain/longterm_memory/operations_educational_knowledge.py

import uuid
from enum import Enum
from typing import Optional, Dict, List
from pydantic import BaseModel
from models.database.longterm_memory.educational_knowledge import EducationType

class EducationalKnowledgeOperation(str, Enum):
    """Enumeration of possible educational knowledge operations."""
    GET = "get"
    GET_ALL = "get_all"
    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"

    @property
    def requires_prompt(self) -> bool:
        return self in [self.CREATE, self.UPDATE]

    @property
    def requires_education_type(self) -> bool:
        return self in [self.GET, self.CREATE, self.UPDATE, self.DELETE]

class EducationalKnowledgeOperationInput(BaseModel):
    """Input schema for educational knowledge operations."""
    operation: EducationalKnowledgeOperation
    vp_id: uuid.UUID
    education_type: Optional[EducationType] = None
    prompt: Optional[str] = None

class EducationalKnowledgeOperationOutput(BaseModel):
    """Output schema for educational knowledge operations."""
    success: bool
    data: Optional[Dict] = None
    data_list: Optional[List[Dict]] = None
    error: Optional[str] = None