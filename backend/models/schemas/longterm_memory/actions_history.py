# models/schemas/longterm_memory/actions_history.py

from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from uuid import UUID


class ActionsHistoryCreate(BaseModel):
   """Schema for creating a new actions history record."""
   vp_id: UUID
   summary: str
   context: str
   action_count: int = 0


class ActionsHistoryRead(BaseModel):
   """Schema for reading an actions history record."""
   id: int
   vp_id: UUID
   summary: str
   context: str
   last_updated: datetime
   action_count: int


class ActionsHistoryUpdate(BaseModel):
   """Schema for updating an actions history record."""
   summary: Optional[str] = None
   context: Optional[str] = None
   action_count: Optional[int] = None