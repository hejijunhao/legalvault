# models/database/longterm_memory/self_identity.py

from sqlmodel import SQLModel, Field
from sqlalchemy import Column, Text
from typing import Optional
import uuid

class SelfIdentity(SQLModel, table=True):
    """Database model for VP self-identity system prompts."""
    __tablename__ = "longterm_memory_self_identity"

    id: Optional[int] = Field(default=None, primary_key=True)
    vp_id: uuid.UUID = Field(foreign_key="virtual_paralegals.id")  # Changed to UUID type
    prompt: str = Field(sa_column=Column(Text))