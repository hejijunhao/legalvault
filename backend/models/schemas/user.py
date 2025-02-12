# models/schemas/user.py

from pydantic import BaseModel
from typing import Optional
from uuid import UUID

class UserCreate(BaseModel):
    email: str
    name: str
    role: str = "lawyer"  # default role

class UserResponse(BaseModel):
    id: UUID
    email: str
    name: str
    paralegal_id: Optional[UUID]  # Link to their VP