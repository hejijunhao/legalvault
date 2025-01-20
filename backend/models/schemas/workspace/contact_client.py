# models/schemas/workspace/contact_client.py

from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, constr
from models.database.workspace.contact_client import ContactRole


class ContactClientBase(BaseModel):
    """Base schema for contact-client association"""
    role: ContactRole = ContactRole.OTHER
    department: Optional[constr(max_length=100)] = None


class ContactClientCreate(ContactClientBase):
    """Schema for creating a new contact-client association"""
    contact_id: UUID
    client_id: UUID


class ContactClientUpdate(ContactClientBase):
    """Schema for updating a contact-client association"""
    role: Optional[ContactRole] = None
    department: Optional[constr(max_length=100)] = None


class ContactClientRead(ContactClientBase):
    """Schema for reading contact-client association"""
    contact_id: UUID
    client_id: UUID
    created_at: datetime
    updated_at: datetime
    created_by: Optional[UUID]

    class Config:
        from_attributes = True