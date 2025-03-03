# models/schemas/research/search.py

from datetime import datetime
from typing import Dict, List, Optional, Any
from uuid import UUID
from pydantic import BaseModel, Field

class SearchBase(BaseModel):
    """Base schema with common search fields"""
    query: str = Field(..., min_length=1, description="Search query text")

class SearchCreate(SearchBase):
    """Schema for creating a new search"""
    search_params: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        description="Optional parameters to customize search behavior"
    )

class SearchContinue(BaseModel):
    """Schema for continuing an existing search"""
    follow_up_query: str = Field(
        ..., 
        min_length=1,
        description="Follow-up query for an existing search"
    )

class SearchMessageResponse(BaseModel):
    """Schema for search message responses"""
    role: str
    content: Dict[str, Any]
    sequence: int

    model_config = {"from_attributes": True}

class SearchResponse(SearchBase):
    """Schema for search API responses"""
    id: UUID
    title: str
    description: Optional[str] = None
    user_id: UUID
    enterprise_id: UUID
    is_featured: bool = False
    tags: Optional[List[str]] = None
    search_params: Dict[str, Any]
    created_at: datetime
    updated_at: datetime
    messages: List[SearchMessageResponse]

    model_config = {"from_attributes": True}

class SearchListResponse(BaseModel):
    """Schema for search list responses"""
    id: UUID
    title: str
    description: Optional[str] = None
    is_featured: bool
    tags: Optional[List[str]] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}

class SearchUpdate(BaseModel):
    """Schema for updating search metadata"""
    title: Optional[str] = None
    description: Optional[str] = None
    is_featured: Optional[bool] = None
    tags: Optional[List[str]] = None
    
    model_config = {"from_attributes": True}