# models/schemas/auth/user.py

from pydantic import BaseModel, EmailStr, validator
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

    @validator('password')
    def validate_password(cls, v):
        if len(v) < 6:
            raise ValueError("Password should be at least 6 characters.")
        return v

class UserProfile(BaseModel):
    id: UUID
    email: EmailStr
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    name: Optional[str] = None
    role: str
    virtual_paralegal_id: Optional[UUID] = None
    enterprise_id: Optional[UUID] = None
    created_at: datetime
    last_login: Optional[datetime] = None