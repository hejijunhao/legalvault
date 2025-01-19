# api/routes/project_client.py
from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session
from models.schemas.project_client import ProjectClientCreate, ProjectClientRead, ProjectClientUpdate
from models.domain.workspace.operations_project_client import ProjectClientOperations
from core.database import get_session
from core.auth import get_current_user

router = APIRouter(prefix="/project-clients", tags=["project-clients"])

@router.post("/", response_model=ProjectClientRead)
async def create_project_client(
    data: ProjectClientCreate,
    session: Session = Depends(get_session),
    current_user: UUID = Depends(get_current_user)
):
    operations = ProjectClientOperations(session)
    return await operations.create(data, current_user)

@router.get("/project/{project_id}", response_model=List[ProjectClientRead])
async def get_project_clients(
    project_id: UUID,
    session: Session = Depends(get_session)
):
    operations = ProjectClientOperations(session)
    return await operations.get_by_project(project_id)

@router.get("/client/{client_id}", response_model=List[ProjectClientRead])
async def get_client_projects(
    client_id: UUID,
    session: Session = Depends(get_session)
):
    operations = ProjectClientOperations(session)
    return await operations.get_by_client(client_id)

@router.patch("/{project_id}/{client_id}", response_model=ProjectClientRead)
async def update_project_client(
    project_id: UUID,
    client_id: UUID,
    data: ProjectClientUpdate,
    session: Session = Depends(get_session)
):
    operations = ProjectClientOperations(session)
    updated = await operations.update(project_id, client_id, data)
    if not updated:
        raise HTTPException(status_code=404, detail="Project-Client relationship not found")
    return updated

@router.delete("/{project_id}/{client_id}")
async def delete_project_client(
    project_id: UUID,
    client_id: UUID,
    session: Session = Depends(get_session)
):
    operations = ProjectClientOperations(session)
    if not await operations.delete(project_id, client_id):
        raise HTTPException(status_code=404, detail="Project-Client relationship not found")
    return {"status": "success"}