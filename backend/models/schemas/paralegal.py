from pydantic import BaseModel, EmailStr
from typing import Optional, List, Dict, Any
from uuid import UUID
from datetime import datetime

# Input schema for creating a new VP
class VirtualParalegalCreate(BaseModel):
    name: str
    email: EmailStr
    phone: Optional[str] = None
    whatsapp: Optional[str] = None
    owner_id: UUID

# Input schema for updating a VP
class VirtualParalegalUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    whatsapp: Optional[str] = None
    tech_tree_progress: Optional[Dict[str, Dict]] = None

# Output schema for API responses
class VirtualParalegalResponse(BaseModel):
    id: UUID
    name: str
    email: str
    phone: Optional[str]
    whatsapp: Optional[str]
    owner_id: UUID
    abilities: List[UUID] = []
    behaviors: Dict[str, Any] = {}
    tech_tree_progress: Dict[str, Dict] = Field(
        default_factory=lambda: {
            "unlocked_nodes": {},
            "progress": {},
            "metadata": {}
        }
    )
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True