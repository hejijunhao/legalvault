# backend/models/database/profile_picture.py
from typing import Optional
from sqlmodel import SQLModel, Field

class VPProfilePicture(SQLModel, table=True):
    __tablename__ = "vp_profile_pictures"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    image_url: str
    display_order: int = Field(default=0, index=True)
    is_active: bool = Field(default=True)