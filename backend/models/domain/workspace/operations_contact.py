# models/domain/workspace/operations_contact.py

from datetime import datetime
from typing import List, Optional
from uuid import UUID
from sqlmodel import select, Session
from models.database.workspace.contact import Contact as DBContact
from models.database.workspace.contact_client import ContactClient, ContactRole
from models.schemas.workspace.contact import ContactCreate, ContactUpdate
from models.schemas.workspace.contact_client import ContactClientCreate, ContactClientUpdate
from models.domain.workspace.contact import Contact
from models.database.workspace.contact_project import ContactProject, ProjectRole
from models.schemas.workspace.contact_project import ContactProjectCreate, ContactProjectUpdate


class ContactOperations:
    def __init__(self, session: Session):
        self.session = session

    async def create(self, data: ContactCreate, user_id: UUID) -> Contact:
        """Create a new contact"""
        db_contact = DBContact(
            **data.model_dump(),
            created_by=user_id,
            modified_by=user_id
        )
        self.session.add(db_contact)
        await self.session.commit()
        await self.session.refresh(db_contact)
        return self._to_domain(db_contact)

    async def get(self, contact_id: UUID) -> Optional[Contact]:
        """Get a contact by ID"""
        query = select(DBContact).where(DBContact.contact_id == contact_id)
        result = await self.session.execute(query)
        db_contact = result.scalar_one_or_none()
        return self._to_domain(db_contact) if db_contact else None

    async def list(
        self,
        skip: int = 0,
        limit: int = 100,
        contact_type: Optional[str] = None,
        status: Optional[str] = None
    ) -> List[Contact]:
        """List contacts with optional filtering"""
        query = select(DBContact)
        
        if contact_type:
            query = query.where(DBContact.contact_type == contact_type)
        if status:
            query = query.where(DBContact.status == status)
            
        query = query.offset(skip).limit(limit)
        result = await self.session.execute(query)
        return [self._to_domain(c) for c in result.scalars().all()]

    async def update(
        self,
        contact_id: UUID,
        data: ContactUpdate,
        user_id: UUID
    ) -> Optional[Contact]:
        """Update a contact"""
        query = select(DBContact).where(DBContact.contact_id == contact_id)
        result = await self.session.execute(query)
        db_contact = result.scalar_one_or_none()
        
        if db_contact:
            update_data = data.model_dump(exclude_unset=True)
            for key, value in update_data.items():
                setattr(db_contact, key, value)
            
            db_contact.modified_by = user_id
            db_contact.updated_at = datetime.utcnow()
            
            await self.session.commit()
            await self.session.refresh(db_contact)
            return self._to_domain(db_contact)
        
        return None

    async def delete(self, contact_id: UUID) -> bool:
        """Delete a contact"""
        query = select(DBContact).where(DBContact.contact_id == contact_id)
        result = await self.session.execute(query)
        db_contact = result.scalar_one_or_none()
        
        if db_contact:
            await self.session.delete(db_contact)
            await self.session.commit()
            return True
        return False

    async def search(self, term: str, limit: int = 10) -> List[Contact]:
        """Search contacts by name or email"""
        query = select(DBContact).where(
            (DBContact.first_name.ilike(f"%{term}%")) |
            (DBContact.last_name.ilike(f"%{term}%")) |
            (DBContact.email.ilike(f"%{term}%"))
        ).limit(limit)
        
        result = await self.session.execute(query)
        return [self._to_domain(c) for c in result.scalars().all()]

    def _to_domain(self, db_contact: DBContact) -> Contact:
        """Convert DB model to domain model"""
        return Contact(
            contact_id=db_contact.contact_id,
            first_name=db_contact.first_name,
            last_name=db_contact.last_name,
            email=db_contact.email,
            phone=db_contact.phone,
            title=db_contact.title,
            organization=db_contact.organization,
            contact_type=db_contact.contact_type,
            status=db_contact.status,
            notes=db_contact.notes,
            created_at=db_contact.created_at,
            updated_at=db_contact.updated_at,
            created_by=db_contact.created_by,
            modified_by=db_contact.modified_by
        )

    async def add_client(
        self,
        data: ContactClientCreate,
        user_id: UUID
    ) -> bool:
        """Associate a contact with a client"""
        association = ContactClient(
            contact_id=data.contact_id,
            client_id=data.client_id,
            role=data.role,
            department=data.department,
            created_by=user_id
        )
        self.session.add(association)
        await self.session.commit()
        return True

    async def remove_client(
        self,
        contact_id: UUID,
        client_id: UUID
    ) -> bool:
        """Remove a client association from a contact"""
        query = select(ContactClient).where(
            (ContactClient.contact_id == contact_id) &
            (ContactClient.client_id == client_id)
        )
        result = await self.session.execute(query)
        association = result.scalar_one_or_none()
        
        if association:
            await self.session.delete(association)
            await self.session.commit()
            return True
        return False

    async def update_client_role(
        self,
        contact_id: UUID,
        client_id: UUID,
        data: ContactClientUpdate,
        user_id: UUID
    ) -> bool:
        """Update the role of a contact for a specific client"""
        query = select(ContactClient).where(
            (ContactClient.contact_id == contact_id) &
            (ContactClient.client_id == client_id)
        )
        result = await self.session.execute(query)
        association = result.scalar_one_or_none()
        
        if association:
            update_data = data.model_dump(exclude_unset=True)
            for key, value in update_data.items():
                setattr(association, key, value)
            
            association.updated_at = datetime.utcnow()
            await self.session.commit()
            return True
        return False

    async def list_clients(
        self,
        contact_id: UUID,
        role: Optional[ContactRole] = None
    ) -> List[UUID]:
        """List all client IDs associated with a contact"""
        query = select(ContactClient.client_id).where(
            ContactClient.contact_id == contact_id
        )
        if role:
            query = query.where(ContactClient.role == role)
        
        result = await self.session.execute(query)
        return [r[0] for r in result.all()]

    async def add_project(
        self,
        data: ContactProjectCreate,
        user_id: UUID
    ) -> bool:
        """Associate a contact with a project"""
        association = ContactProject(
            contact_id=data.contact_id,
            project_id=data.project_id,
            role=data.role,
            start_date=data.start_date,
            end_date=data.end_date,
            notes=data.notes,
            created_by=user_id
        )
        self.session.add(association)
        await self.session.commit()
        return True

    async def remove_project(
        self,
        contact_id: UUID,
        project_id: UUID
    ) -> bool:
        """Remove a project association from a contact"""
        query = select(ContactProject).where(
            (ContactProject.contact_id == contact_id) &
            (ContactProject.project_id == project_id)
        )
        result = await self.session.execute(query)
        association = result.scalar_one_or_none()
        
        if association:
            await self.session.delete(association)
            await self.session.commit()
            return True
        return False

    async def update_project_role(
        self,
        contact_id: UUID,
        project_id: UUID,
        data: ContactProjectUpdate,
        user_id: UUID
    ) -> bool:
        """Update the role of a contact in a specific project"""
        query = select(ContactProject).where(
            (ContactProject.contact_id == contact_id) &
            (ContactProject.project_id == project_id)
        )
        result = await self.session.execute(query)
        association = result.scalar_one_or_none()
        
        if association:
            update_data = data.model_dump(exclude_unset=True)
            for key, value in update_data.items():
                setattr(association, key, value)
        
            association.updated_at = datetime.utcnow()
            await self.session.commit()
            return True
        return False

    async def list_projects(
        self,
        contact_id: UUID,
        role: Optional[ProjectRole] = None,
        active_only: bool = False
    ) -> List[UUID]:
        """List all project IDs associated with a contact"""
        query = select(ContactProject.project_id).where(
            ContactProject.contact_id == contact_id
        )
        if role:
            query = query.where(ContactProject.role == role)
        if active_only:
            query = query.where(
                (ContactProject.end_date.is_(None)) | 
                (ContactProject.end_date > datetime.utcnow())
            )
        
        result = await self.session.execute(query)
        return [r[0] for r in result.all()]

    async def list_contacts_by_client(
        self,
        client_id: UUID,
        role: Optional[ContactRole] = None
    ) -> List[UUID]:
        """List all contact IDs associated with a client"""
        query = select(ContactClient.contact_id).where(
            ContactClient.client_id == client_id
        )
        if role:
            query = query.where(ContactClient.role == role)
        
        result = await self.session.execute(query)
        return [r[0] for r in result.all()]

    async def list_contacts_by_project(
        self,
        project_id: UUID,
        role: Optional[ProjectRole] = None,
        active_only: bool = False
    ) -> List[UUID]:
        """List all contact IDs associated with a project"""
        query = select(ContactProject.contact_id).where(
            ContactProject.project_id == project_id
        )
        if role:
            query = query.where(ContactProject.role == role)
        if active_only:
            query = query.where(
                (ContactProject.end_date.is_(None)) | 
                (ContactProject.end_date > datetime.utcnow())
            )
        
        result = await self.session.execute(query)
        return [r[0] for r in result.all()]
