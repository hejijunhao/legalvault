from sqlmodel import SQLModel, Field
from typing import Optional
from uuid import UUID, uuid4
from datetime import datetime


class Task(SQLModel, table=True):
    __tablename__ = "tasks"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    title: str = Field(index=True)
    description: str
    status: str = Field(default="pending")
    priority: int = Field(default=1)
    due_date: Optional[datetime] = Field(default=None)
    extracted_from: Optional[str] = Field(default=None)
    source_reference: Optional[str] = Field(default=None)
    assigned_by_paralegal: UUID = Field(foreign_key="virtual_paralegals.id")
    assigned_to_user: UUID = Field(foreign_key="users.id")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)