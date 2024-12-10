from pydantic import BaseModel
from typing import Optional, List, Dict
from uuid import UUID
from datetime import datetime

class AbilityCreate(BaseModel):
    name: str
    description: str
    category: str  # e.g., "Communication", "Task Management"
    prerequisites: List[UUID] = []  # Required abilities to unlock this
    tier: int  # Tech tree tier/level
    cost: int  # Cost to unlock (if implementing a point system)
    icon_name: Optional[str] = None  # For UI representation

class AbilityResponse(BaseModel):
    id: UUID
    name: str
    description: str
    category: str
    prerequisites: List[UUID]
    tier: int
    cost: int
    icon_name: Optional[str]
    is_active: bool
    created_at: datetime
    updated_at: datetime

class AbilityTreeResponse(BaseModel):
    categories: Dict[str, List[AbilityResponse]]
    unlocked_abilities: List[UUID]
    available_abilities: List[UUID]  # Abilities that can be unlocked