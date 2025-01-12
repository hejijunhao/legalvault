# models/schemas/longterm_memory/global_knowledge.py

from pydantic import BaseModel
import uuid
from typing import Optional, List
from models.database.longterm_memory.global_knowledge import KnowledgeType


class GlobalKnowledgeCreate(BaseModel):
    """Schema for creating a new global knowledge prompt."""
    vp_id: uuid.UUID
    knowledge_type: KnowledgeType
    prompt: str


class GlobalKnowledgeRead(BaseModel):
    """Schema for reading a global knowledge prompt."""
    id: int
    vp_id: uuid.UUID
    knowledge_type: KnowledgeType
    prompt: str


class GlobalKnowledgeUpdate(BaseModel):
    """Schema for updating a global knowledge prompt."""
    prompt: str


class GlobalKnowledgeList(BaseModel):
    """Schema for listing all global knowledge prompts for a VP."""
    items: List[GlobalKnowledgeRead]