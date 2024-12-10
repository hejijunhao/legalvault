from sqlmodel import SQLModel, Field
from typing import Optional
from uuid import UUID, uuid4
from datetime import datetime


class VirtualParalegal(SQLModel, table=True):
    __tablename__ = "virtual_paralegals"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    name: str = Field(index=True)
    email: str = Field(unique=True)
    phone: Optional[str] = None
    whatsapp: Optional[str] = None
    owner_id: UUID = Field(foreign_key="users.id")
    abilities: list = Field(default=[])  # Stored as JSON
    behaviors: dict = Field(default={})  # Stored as JSON
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)