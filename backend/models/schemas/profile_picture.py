# models/schemas/profile_picture.py
from typing import Optional
from pydantic import BaseModel

class VPProfilePictureBase(BaseModel):
    name: str
    image_url: str
    display_order: int = 0
    is_active: bool = True

class VPProfilePictureCreate(VPProfilePictureBase):
    pass

class VPProfilePictureRead(VPProfilePictureBase):
    id: int

    class Config:
        from_attributes = True

# models/schemas/virtual_paralegal.py
class ProfilePictureUpdate(BaseModel):
    profile_picture_id: int

class VPProfileResponse(BaseModel):
    message: str
    profile_picture_id: int