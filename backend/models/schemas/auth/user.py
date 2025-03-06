# models/schemas/auth/user.py

from pydantic import BaseModel, EmailStr
from typing import Optional
from uuid import UUID
from datetime import datetime

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    first_name: str
    last_name: str
    role: str = "lawyer"  # default role

class UserProfile(BaseModel):
    id: UUID
    email: EmailStr
    first_name: str
    last_name: str
    name: str
    role: str
    virtual_paralegal_id: Optional[UUID] = None
    enterprise_id: Optional[UUID] = None
    created_at: datetime
    last_login: Optional[datetime] = None