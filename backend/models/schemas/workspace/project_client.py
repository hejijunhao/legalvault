# models/schemas/project_client.py
from datetime import datetime
from uuid import UUID
from pydantic import BaseModel

class ProjectClientBase(BaseModel):
    role: str

class ProjectClientCreate(ProjectClientBase):
    project_id: UUID
    client_id: UUID

class ProjectClientRead(ProjectClientBase):
    project_id: UUID
    client_id: UUID
    created_at: datetime
    updated_at: datetime
    created_by: UUID | None

class ProjectClientUpdate(ProjectClientBase):
    role: str | None = None