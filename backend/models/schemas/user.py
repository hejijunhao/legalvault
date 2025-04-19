# models/schemas/user.py

from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from uuid import UUID
from datetime import datetime

class UserCreate(BaseModel):
    """Schema for creating a new user."""
    email: EmailStr = Field(..., description="User's email address")
    first_name: Optional[str] = Field(None, description="User's first name")
    last_name: Optional[str] = Field(None, description="User's last name")
    role: str = Field("lawyer", description="User's role in the system")

    class Config:
        json_schema_extra = {
            "example": {
                "email": "user@example.com",
                "first_name": "John",
                "last_name": "Doe",
                "role": "lawyer"
            }
        }

class UserBase(BaseModel):
    """Base schema with common user fields."""
    id: UUID = Field(..., description="Unique identifier for the user")
    email: EmailStr = Field(..., description="User's email address")
    first_name: Optional[str] = Field(None, description="User's first name")
    last_name: Optional[str] = Field(None, description="User's last name")
    name: Optional[str] = Field(None, description="User's full name")
    role: str = Field(..., description="User's role in the system")
    virtual_paralegal_id: Optional[UUID] = Field(None, description="ID of assigned virtual paralegal")
    enterprise_id: Optional[UUID] = Field(None, description="ID of user's enterprise")
    created_at: datetime = Field(..., description="Timestamp of user creation")
    updated_at: datetime = Field(..., description="Timestamp of last update")

    class Config:
        from_attributes = True

class UserProfile(UserBase):
    """Full user profile including login information."""
    last_login: Optional[datetime] = Field(None, description="Timestamp of last login")

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "email": "user@example.com",
                "first_name": "John",
                "last_name": "Doe",
                "name": "John Doe",
                "role": "lawyer",
                "virtual_paralegal_id": None,
                "enterprise_id": None,
                "created_at": "2025-04-18T08:39:26Z",
                "updated_at": "2025-04-18T08:39:26Z",
                "last_login": "2025-04-18T08:39:26Z"
            }
        }

class UserResponse(UserBase):
    """Basic user response for list views."""
    pass