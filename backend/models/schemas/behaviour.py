# /backend/models/schemas/behaviour.py

from datetime import datetime
from pydantic import BaseModel, Field, validator
from typing import Optional
from uuid import UUID
from models.database.behaviours.behaviour import BehaviourStatus

class BehaviourBase(BaseModel):
    name: str
    description: str
    system_prompt: str
    status: BehaviourStatus = Field(default=BehaviourStatus.ACTIVE)

    @validator('system_prompt')
    def validate_system_prompt(cls, v):
        if not v.strip():
            raise ValueError('system_prompt cannot be empty')
        return v

class BehaviourCreate(BehaviourBase):
    pass

class BehaviourUpdate(BehaviourBase):
    name: Optional[str] = None
    description: Optional[str] = None
    system_prompt: Optional[str] = None
    status: Optional[BehaviourStatus] = None

class BehaviourRead(BehaviourBase):
    id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
