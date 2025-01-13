# models/schemas/longterm_memory/educational_knowledge.py

from pydantic import BaseModel
import uuid
from typing import Optional, List
from models.database.longterm_memory.educational_knowledge import EducationType

class EducationalKnowledgeCreate(BaseModel):
    """Schema for creating a new educational knowledge prompt."""
    vp_id: uuid.UUID
    education_type: EducationType
    prompt: str

class EducationalKnowledgeRead(BaseModel):
    """Schema for reading an educational knowledge prompt."""
    id: int
    vp_id: uuid.UUID
    education_type: EducationType
    prompt: str

class EducationalKnowledgeUpdate(BaseModel):
    """Schema for updating an educational knowledge prompt."""
    prompt: str

class EducationalKnowledgeList(BaseModel):
    """Schema for listing all educational knowledge prompts for a VP."""
    items: List[EducationalKnowledgeRead]