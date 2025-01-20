# api/routes/workspace/contacts.py

from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session
from models.schemas.workspace.contact import ContactCreate, ContactRead, ContactUpdate
from models.domain.workspace.operations_contact import ContactOperations
from core.database import get_session
from core.auth import get_current_user

router = APIRouter(prefix="/contacts", tags=["contacts"])

@router.post("/", response_model=ContactRead)
async def create_contact(
    data: ContactCreate,
    session: Session = Depends(get_session),
    current_user: UUID = Depends(get_current_user)
):
    operations = ContactOperations(session)
    return await operations.create(data, current_user)

@router.get("/{contact_id}", response_model=ContactRead)
async def get_contact(
    contact_id: UUID,
    session: Session = Depends(get_session)
):
    operations = ContactOperations(session)
    contact = await operations.get(contact_id)
    if not contact:
        raise HTTPException(status_code=404, detail="Contact not found")
    return contact

@router.patch("/{contact_id}", response_model=ContactRead)
async def update_contact(
    contact_id: UUID,
    data: ContactUpdate,
    session: Session = Depends(get_session),
    current_user: UUID = Depends(get_current_user)
):
    operations = ContactOperations(session)
    updated = await operations.update(contact_id, data, current_user)
    if not updated:
        raise HTTPException(status_code=404, detail="Contact not found")
    return updated

@router.delete("/{contact_id}")
async def delete_contact(
    contact_id: UUID,
    session: Session = Depends(get_session)
):
    operations = ContactOperations(session)
    if not await operations.delete(contact_id):
        raise HTTPException(status_code=404, detail="Contact not found")
    return {"status": "success"}