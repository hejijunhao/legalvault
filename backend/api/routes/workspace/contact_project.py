# api/routes/workspace/contact_project.py
from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session
from models.schemas.workspace.contact_project import ContactProjectCreate, ContactProjectUpdate
from models.database.workspace.contact_project import ProjectRole
from models.domain.workspace.operations_contact import ContactOperations
from core.database import get_session
from core.auth import get_current_user

router = APIRouter(prefix="/contact-projects", tags=["contact-projects"])

@router.post("/", response_model=bool)
async def create_contact_project(
    data: ContactProjectCreate,
    session: Session = Depends(get_session),
    current_user: UUID = Depends(get_current_user)
):
    operations = ContactOperations(session)
    return await operations.add_project(data, current_user)

@router.delete("/{contact_id}/{project_id}")
async def delete_contact_project(
    contact_id: UUID,
    project_id: UUID,
    session: Session = Depends(get_session)
):
    operations = ContactOperations(session)
    if not await operations.remove_project(contact_id, project_id):
        raise HTTPException(status_code=404, detail="Contact-Project relationship not found")
    return {"status": "success"}

@router.patch("/{contact_id}/{project_id}", response_model=bool)
async def update_contact_project(
    contact_id: UUID,
    project_id: UUID,
    data: ContactProjectUpdate,
    session: Session = Depends(get_session),
    current_user: UUID = Depends(get_current_user)
):
    operations = ContactOperations(session)
    if not await operations.update_project_role(contact_id, project_id, data, current_user):
        raise HTTPException(status_code=404, detail="Contact-Project relationship not found")
    return True

@router.get("/project/{project_id}", response_model=List[UUID])
async def get_project_contacts(
    project_id: UUID,
    role: ProjectRole = None,
    active_only: bool = False,
    session: Session = Depends(get_session)
):
    operations = ContactOperations(session)
    return await operations.list_contacts_by_project(project_id, role, active_only)

@router.get("/contact/{contact_id}", response_model=List[UUID])
async def get_contact_projects(
    contact_id: UUID,
    role: ProjectRole = None,
    active_only: bool = False,
    session: Session = Depends(get_session)
):
    operations = ContactOperations(session)
    return await operations.list_projects(contact_id, role, active_only)