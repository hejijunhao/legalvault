# api/routes/library/collections.py

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from uuid import UUID
from typing import List

from core.database import get_session
from core.auth import get_current_user
from models.domain.library.operations_collections import CollectionOperations
from models.schemas.library.collections import (
    CollectionCreate,
    CollectionUpdate,
    CollectionResponse,
    CollectionList,
    CollectionDelete
)
from models.schemas.user import UserResponse

router = APIRouter()

@router.post("/collections", response_model=CollectionResponse)
def create_collection(
    collection: CollectionCreate,
    session: Session = Depends(get_session),
    current_user: UserResponse = Depends(get_current_user)
):
    collection.owner_id = current_user.id
    collection_ops = CollectionOperations(session)
    try:
        return collection_ops.create_collection(collection)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/collections/{collection_id}", response_model=CollectionResponse)
def get_collection(
    collection_id: UUID,
    session: Session = Depends(get_session),
    current_user: UserResponse = Depends(get_current_user)
):
    collection_ops = CollectionOperations(session)
    collection = collection_ops.get_collection(collection_id)
    if not collection:
        raise HTTPException(status_code=404, detail="Collection not found")
    if collection.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to access this collection")
    return collection

@router.get("/collections", response_model=CollectionList)
def list_collections(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    session: Session = Depends(get_session),
    current_user: UserResponse = Depends(get_current_user)
):
    collection_ops = CollectionOperations(session)
    collections = collection_ops.get_collections_by_owner(current_user.id)
    return CollectionList(
        collections=collections[skip : skip + limit],
        total=len(collections)
    )

@router.put("/collections/{collection_id}", response_model=CollectionResponse)
def update_collection(
    collection_id: UUID,
    collection_update: CollectionUpdate,
    session: Session = Depends(get_session),
    current_user: UserResponse = Depends(get_current_user)
):
    collection_ops = CollectionOperations(session)
    existing_collection = collection_ops.get_collection(collection_id)
    if not existing_collection:
        raise HTTPException(status_code=404, detail="Collection not found")
    if existing_collection.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to update this collection")
    updated_collection = collection_ops.update_collection(collection_id, collection_update.dict(exclude_unset=True))
    return updated_collection

@router.delete("/collections/{collection_id}", response_model=CollectionDelete)
def delete_collection(
    collection_id: UUID,
    session: Session = Depends(get_session),
    current_user: UserResponse = Depends(get_current_user)
):
    collection_ops = CollectionOperations(session)
    existing_collection = collection_ops.get_collection(collection_id)
    if not existing_collection:
        raise HTTPException(status_code=404, detail="Collection not found")
    if existing_collection.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to delete this collection")
    if existing_collection.is_default:
        raise HTTPException(status_code=400, detail="Cannot delete default collection")
    success = collection_ops.delete_collection(collection_id)
    return CollectionDelete(id=collection_id, success=success, message="Collection deleted successfully" if success else "Failed to delete collection")

@router.get("/collections/type/{collection_type}", response_model=List[CollectionResponse])
def get_collections_by_type(
    collection_type: str,
    session: Session = Depends(get_session),
    current_user: UserResponse = Depends(get_current_user)
):
    collection_ops = CollectionOperations(session)
    collections = collection_ops.get_collections_by_type(collection_type)
    return [collection for collection in collections if collection.owner_id == current_user.id]

@router.get("/collections/default", response_model=CollectionResponse)
def get_default_collection(
    session: Session = Depends(get_session),
    current_user: UserResponse = Depends(get_current_user)
):
    collection_ops = CollectionOperations(session)
    default_collection = collection_ops.get_default_collection(current_user.id)
    if not default_collection:
        raise HTTPException(status_code=404, detail="Default collection not found")
    return default_collection