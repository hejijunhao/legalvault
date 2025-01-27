# schemas/ability.py
from pydantic import BaseModel
from typing import Dict, List, Optional
from datetime import datetime
from enum import Enum


class AbilityNodeSchema(BaseModel):
    id: str
    name: str
    category: str
    level: int
    description: str
    prerequisites: List[str]
    unlock_conditions: Dict[str, any]
    metadata: Dict[str, any]


class AbilityBase(BaseModel):
    name: str
    description: str
    structure: Dict[str, AbilityNodeSchema]
    requirements: Dict[str, any]
    meta_info: Dict[str, any]  # Changed from metadata to meta_info


class AbilityCreate(AbilityBase):
    pass


class TAbilityUpdate(AbilityBase):
    pass


class TAbilityRead(AbilityBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


class AbilityProgressRead(BaseModel):
    paralegal_id: str
    unlocked_nodes: Dict[str, datetime]
    progress: Dict[str, float]

    class Config:
        orm_mode = True