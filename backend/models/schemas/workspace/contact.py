# models/schemas/workspace/contact.py

from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, EmailStr
from models.database.workspace.contact import ContactType, ContactStatus


class ContactBase(BaseModel):
    """Base Contact schema with common attributes"""
    first_name: constr(min_length=1, max_length=100)
    last_name: constr(min_length=1, max_length=100)
    email: EmailStr
    phone: Optional[constr(max_length=50)] = None
    title: Optional[constr(max_length=100)] = None
    organization: Optional[constr(max_length=255)] = None
    contact_type: ContactType = ContactType.EXTERNAL
    status: ContactStatus = ContactStatus.ACTIVE
    notes: Optional[str] = None


class ContactCreate(ContactBase):
    """Schema for creating a new contact"""
    pass


class ContactUpdate(BaseModel):
    """Schema for updating an existing contact"""
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    title: Optional[str] = None
    organization: Optional[str] = None
    contact_type: Optional[ContactType] = None
    status: Optional[ContactStatus] = None
    notes: Optional[str] = None


class ContactRead(ContactBase):
    """Schema for reading contact information"""
    contact_id: UUID
    created_at: datetime
    updated_at: datetime
    created_by: UUID
    modified_by: Optional[UUID]

    class Config:
        from_attributes = True