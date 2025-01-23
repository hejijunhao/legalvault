# api/routes/library/masterfiledatabase.py

from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, Path
from sqlmodel import Session

from models.domain.library.operations_masterfiledatabase import MasterFileOperations
from models.schemas.library.masterfiledatabase import (
    MasterFileCreateSchema,
    MasterFileUpdateSchema,
    MasterFileResponseSchema,
    FilePermissionSchema,
    FileStatusSchema
)
from core.database import get_session
from core.auth import get_current_user

router = APIRouter(prefix="/library/files", tags=["Library"])


@router.post("/", response_model=MasterFileResponseSchema)
async def create_file(
        file_data: MasterFileCreateSchema,
        session: Session = Depends(get_session),
        current_user: UUID = Depends(get_current_user)
):
    ops = MasterFileOperations(session)
    file = await ops.create_file({**file_data.dict(), "owner_id": current_user})
    return file.db_model


@router.get("/{file_id}", response_model=MasterFileResponseSchema)
async def get_file(
        file_id: UUID = Path(...),
        session: Session = Depends(get_session),
        current_user: UUID = Depends(get_current_user)
):
    ops = MasterFileOperations(session)
    file = await ops.get_file(file_id)
    if not file or not file.is_accessible_by_user(current_user):
        raise HTTPException(status_code=404, detail="File not found")
    return file.db_model


@router.get("/", response_model=List[MasterFileResponseSchema])
async def list_files(
        client_id: Optional[UUID] = Query(None),
        session: Session = Depends(get_session),
        current_user: UUID = Depends(get_current_user)
):
    ops = MasterFileOperations(session)
    if client_id:
        files = await ops.get_files_by_client(client_id)
    else:
        files = await ops.get_files_by_owner(current_user)
    return [file.db_model for file in files if file.is_accessible_by_user(current_user)]


@router.patch("/{file_id}", response_model=MasterFileResponseSchema)
async def update_file(
        file_data: MasterFileUpdateSchema,
        file_id: UUID = Path(...),
        session: Session = Depends(get_session),
        current_user: UUID = Depends(get_current_user)
):
    ops = MasterFileOperations(session)
    file = await ops.get_file(file_id)
    if not file or not file.is_accessible_by_user(current_user):
        raise HTTPException(status_code=404, detail="File not found")

    if file_data.file_attributes:
        file = await ops.update_metadata(file_id, file_data.file_attributes.dict())
    if file_data.content_details:
        file = await ops.update_content_details(file_id, file_data.content_details.dict())
    return file.db_model


@router.post("/{file_id}/status", response_model=MasterFileResponseSchema)
async def update_file_status(
        status: FileStatusSchema,
        file_id: UUID = Path(...),
        session: Session = Depends(get_session),
        current_user: UUID = Depends(get_current_user)
):
    ops = MasterFileOperations(session)
    file = await ops.get_file(file_id)
    if not file or not file.is_accessible_by_user(current_user):
        raise HTTPException(status_code=404, detail="File not found")

    updated_file = await ops.update_file_status(file_id, status.action)
    if not updated_file:
        raise HTTPException(status_code=400, detail="Status update failed")
    return updated_file.db_model


@router.post("/{file_id}/permissions", response_model=MasterFileResponseSchema)
async def update_file_permissions(
        permission: FilePermissionSchema,
        file_id: UUID = Path(...),
        session: Session = Depends(get_session),
        current_user: UUID = Depends(get_current_user)
):
    ops = MasterFileOperations(session)
    file = await ops.get_file(file_id)
    if not file or file.db_model.owner_id != current_user:
        raise HTTPException(status_code=404, detail="File not found")

    file = await ops.update_permissions(file_id, permission.user_id, permission.add)
    return file.db_model