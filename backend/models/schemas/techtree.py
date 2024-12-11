from pydantic import BaseModel
from typing import Dict, List, Optional
from datetime import datetime
from enum import Enum


class TechTreeNodeSchema(BaseModel):
    id: str
    name: str
    category: str
    level: int
    description: str
    prerequisites: List[str]
    unlock_conditions: Dict[str, any]
    metadata: Dict[str, any]


class TechTreeBase(BaseModel):
    name: str
    description: str
    structure: Dict[str, TechTreeNodeSchema]
    requirements: Dict[str, any]
    meta_info: Dict[str, any]  # Changed from metadata to meta_info


class TechTreeCreate(TechTreeBase):
    pass


class TechTreeUpdate(TechTreeBase):
    pass


class TechTreeRead(TechTreeBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


class TechTreeProgressRead(BaseModel):
    paralegal_id: str
    unlocked_nodes: Dict[str, datetime]
    progress: Dict[str, float]

    class Config:
        orm_mode = True