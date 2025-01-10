# models/schemas/longterm_memory/self_identity.py

from pydantic import BaseModel
from typing import Optional


class SelfIdentityCreate(BaseModel):
    """Schema for creating a new self-identity prompt."""
    vp_id: int
    prompt: str


class SelfIdentityRead(BaseModel):
    """Schema for reading a self-identity prompt."""
    id: int
    vp_id: int
    prompt: str


class SelfIdentityUpdate(BaseModel):
    """Schema for updating a self-identity prompt."""
    prompt: str