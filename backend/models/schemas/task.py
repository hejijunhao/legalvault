from pydantic import BaseModel
from typing import Optional, List
from uuid import UUID
from datetime import datetime

class TaskCreate(BaseModel):
    title: str
    description: str
    priority: int = 1
    due_date: Optional[datetime] = None
    extracted_from: Optional[str] = None  # e.g., "email", "document"
    source_reference: Optional[str] = None  # e.g., email ID or doc ID
    assigned_to_user: UUID

class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    priority: Optional[int] = None
    due_date: Optional[datetime] = None

class TaskResponse(BaseModel):
    id: UUID
    title: str
    description: str
    status: str
    priority: int
    due_date: Optional[datetime]
    extracted_from: Optional[str]
    source_reference: Optional[str]
    assigned_by_paralegal: UUID
    assigned_to_user: UUID
    created_at: datetime
    updated_at: datetime