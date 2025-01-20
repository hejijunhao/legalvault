# api/routes/workspace/contact_client.py

from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session
from models.schemas.workspace.contact_client import ContactClientCreate, ContactClientUpdate
from models.database.workspace.contact_client import ContactRole
from models.domain.workspace.operations_contact import ContactOperations
from core.database import get_session
from core.auth import get_current_user

router = APIRouter(prefix="/contact-clients", tags=["contact-clients"])

@router.post("/", response_model=bool)
async def create_contact_client(
    data: ContactClientCreate,
    session: Session = Depends(get_session),
    current_user: UUID = Depends(get_current_user)
):
    operations = ContactOperations(session)
    return await operations.add_client(data, current_user)

@router.delete("/{contact_id}/{client_id}")
async def delete_contact_client(
    contact_id: UUID,
    client_id: UUID,
    session: Session = Depends(get_session)
):
    operations = ContactOperations(session)
    if not await operations.remove_client(contact_id, client_id):
        raise HTTPException(status_code=404, detail="Contact-Client relationship not found")
    return {"status": "success"}

@router.patch("/{contact_id}/{client_id}", response_model=bool)
async def update_contact_client(
    contact_id: UUID,
    client_id: UUID,
    data: ContactClientUpdate,
    session: Session = Depends(get_session),
    current_user: UUID = Depends(get_current_user)
):
    operations = ContactOperations(session)
    if not await operations.update_client_role(contact_id, client_id, data, current_user):
        raise HTTPException(status_code=404, detail="Contact-Client relationship not found")
    return True

@router.get("/client/{client_id}", response_model=List[UUID])
async def get_client_contacts(
    client_id: UUID,
    role: ContactRole = None,
    session: Session = Depends(get_session)
):
    operations = ContactOperations(session)
    return await operations.list_contacts_by_client(client_id, role)

@router.get("/contact/{contact_id}", response_model=List[UUID])
async def get_contact_clients(
    contact_id: UUID,
    role: ContactRole = None,
    session: Session = Depends(get_session)
):
    operations = ContactOperations(session)
    return await operations.list_clients(contact_id, role)