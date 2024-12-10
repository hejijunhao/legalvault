from sqlmodel import SQLModel, Field
from typing import Optional, Any
from uuid import UUID, uuid4
from datetime import datetime


class Behavior(SQLModel, table=True):
    __tablename__ = "behaviors"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    paralegal_id: UUID = Field(foreign_key="virtual_paralegals.id")
    category: str = Field(index=True)
    setting_key: str = Field(index=True)
    value: Any = Field(default=None)  # Stored as JSON
    is_customizable: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)