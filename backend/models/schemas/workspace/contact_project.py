# models/schemas/workspace/contact_project.py

from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, constr
from models.database.workspace.contact_project import ProjectRole


class ContactProjectBase(BaseModel):
    """Base schema for contact-project association"""
    role: ProjectRole = ProjectRole.OTHER
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    notes: Optional[str] = None


class ContactProjectCreate(ContactProjectBase):
    """Schema for creating a new contact-project association"""
    contact_id: UUID
    project_id: UUID


class ContactProjectUpdate(ContactProjectBase):
    """Schema for updating a contact-project association"""
    role: Optional[ProjectRole] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    notes: Optional[str] = None


class ContactProjectRead(ContactProjectBase):
    """Schema for reading contact-project association"""
    contact_id: UUID
    project_id: UUID
    created_at: datetime
    updated_at: datetime
    created_by: Optional[UUID]

    class Config:
        from_attributes = True