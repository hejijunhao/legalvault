# models/schemas/library/collections.py

from datetime import datetime
from typing import Dict, Any, Optional
from uuid import UUID

from pydantic import BaseModel, Field, ConfigDict

def default_dict() -> Dict[str, Any]:
    return {}

class CollectionBase(BaseModel):
    name: str = Field(..., description="The name of the collection")
    description: Optional[str] = Field(None, description="A brief description of the collection")
    collection_type: str = Field(..., description="The type of the collection")
    collection_metadata: Dict[str, Any] = Field(default_factory=default_dict, description="Additional metadata for the collection")

class CollectionCreate(CollectionBase):
    owner_id: UUID
    is_default: bool = False

class CollectionUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    collection_type: Optional[str] = None
    is_default: Optional[bool] = None
    collection_metadata: Optional[Dict[str, Any]] = None

class CollectionInDB(CollectionBase):
    id: UUID
    owner_id: UUID
    is_default: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class CollectionResponse(CollectionInDB):
    pass

class CollectionList(BaseModel):
    collections: list[CollectionResponse]
    total: int
    page: int
    page_size: int
    total_pages: int

class CollectionDelete(BaseModel):
    id: UUID
    success: bool
    message: str
