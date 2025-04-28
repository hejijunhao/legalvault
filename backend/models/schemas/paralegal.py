# models/schemas/paralegal.py

from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, Field
from typing import Optional

class VirtualParalegalBase(BaseModel):
    """Base schema for Virtual Paralegal data."""
    first_name: str = Field(..., min_length=1, max_length=50)
    last_name: str = Field(..., min_length=1, max_length=50)
    email: Optional[str] = Field(None, max_length=100)
    phone: Optional[str] = Field(None, max_length=20)
    whatsapp: Optional[str] = Field(None, max_length=20)
    gender: Optional[str] = Field(None, max_length=20)
    profile_picture_id: Optional[UUID] = None

class VirtualParalegalCreate(VirtualParalegalBase):
    """Schema for creating a new Virtual Paralegal."""
    pass

class VirtualParalegalUpdate(BaseModel):
    """Schema for updating a Virtual Paralegal."""
    first_name: Optional[str] = Field(None, min_length=1, max_length=50)
    last_name: Optional[str] = Field(None, min_length=1, max_length=50)
    email: Optional[str] = Field(None, max_length=100)
    phone: Optional[str] = Field(None, max_length=20)
    whatsapp: Optional[str] = Field(None, max_length=20)
    gender: Optional[str] = Field(None, max_length=20)
    profile_picture_id: Optional[UUID] = None

class VirtualParalegalResponse(VirtualParalegalBase):
    """Schema for Virtual Paralegal responses."""
    id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True