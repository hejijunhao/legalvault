# models/schemas/longterm_memory/conversational_history.py

from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from uuid import UUID


class ConversationalHistoryCreate(BaseModel):
    """Schema for creating a new conversational history record."""
    vp_id: UUID
    summary: str
    context: str
    interaction_count: int = 0


class ConversationalHistoryRead(BaseModel):
    """Schema for reading a conversational history record."""
    id: int
    vp_id: UUID
    summary: str
    context: str
    last_updated: datetime
    interaction_count: int


class ConversationalHistoryUpdate(BaseModel):
    """Schema for updating a conversational history record."""
    summary: Optional[str] = None
    context: Optional[str] = None
    interaction_count: Optional[int] = None