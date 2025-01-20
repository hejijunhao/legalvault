# models/domain/workspace/contact.py

from datetime import datetime
from typing import Optional
from uuid import UUID
from models.database.workspace.contact import ContactType, ContactStatus


class Contact:
    """Domain model for Contact"""
    
    def __init__(
        self,
        contact_id: UUID,
        first_name: str,
        last_name: str,
        email: str,
        phone: Optional[str],
        title: Optional[str],
        organization: Optional[str],
        contact_type: ContactType,
        status: ContactStatus,
        notes: Optional[str],
        created_at: datetime,
        updated_at: datetime,
        created_by: UUID,
        modified_by: Optional[UUID]
    ):
        self.contact_id = contact_id
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.phone = phone
        self.title = title
        self.organization = organization
        self.contact_type = contact_type
        self.status = status
        self.notes = notes
        self.created_at = created_at
        self.updated_at = updated_at
        self.created_by = created_by
        self.modified_by = modified_by

    @property
    def full_name(self) -> str:
        """Get the contact's full name"""
        return f"{self.first_name} {self.last_name}"

    def is_active(self) -> bool:
        """Check if the contact is active"""
        return self.status == ContactStatus.ACTIVE

    def is_internal(self) -> bool:
        """Check if the contact is internal"""
        return self.contact_type == ContactType.INTERNAL