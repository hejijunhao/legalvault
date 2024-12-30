from pydantic import BaseModel, EmailStr, Field
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
    profile_picture_id: Optional[int] = None

# Input schema for updating a VP
class VirtualParalegalUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    whatsapp: Optional[str] = None
    profile_picture_id: Optional[int] = None
    tech_tree_progress: Optional[Dict[str, Dict]] = None

# Profile picture response schema for nested data
class ProfilePictureResponse(BaseModel):
    id: int
    name: str
    image_url: str
    display_order: int

# Output schema for API responses
class VirtualParalegalResponse(BaseModel):
    id: UUID
    name: str
    email: str
    phone: Optional[str]
    whatsapp: Optional[str]
    owner_id: UUID
    profile_picture_id: Optional[int]
    profile_picture: Optional[ProfilePictureResponse]
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