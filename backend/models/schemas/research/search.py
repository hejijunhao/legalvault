# models/schemas/research/search.py

from datetime import datetime
from typing import Dict, List, Optional, Any, Literal
from uuid import UUID
from pydantic import BaseModel, Field, validator

from models.enums.research_enums import QueryCategory, QueryType


class SearchBase(BaseModel):
    """Base schema with common search fields"""
    title: Optional[str] = Field(None, description="Title for the search")
    description: Optional[str] = Field(None, description="Description of the search")
    tags: Optional[List[str]] = Field(default_factory=list, description="Tags for categorization")
    is_featured: bool = Field(default=False, description="Whether this is a featured search")
    search_params: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        description="Optional parameters to customize search behavior"
    )

    @validator("search_params")
    def validate_search_params(cls, v):
        allowed_keys = {"temperature", "max_tokens", "top_p", "top_k", "jurisdiction"}
        if v and not all(k in allowed_keys for k in v.keys()):
            raise ValueError(f"Invalid search parameters. Allowed keys: {allowed_keys}")
        try:
            import json
            json.dumps(v)
        except TypeError:
            raise ValueError("Search parameters must be JSON-serializable")
        return v


class SearchCreate(SearchBase):
    """Schema for creating a new search"""
    query: str = Field(..., description="Initial search query", min_length=3)


class SearchUpdate(BaseModel):
    """Schema for updating a search"""
    title: Optional[str] = Field(None, description="Updated title")
    description: Optional[str] = Field(None, description="Updated description")
    is_featured: Optional[bool] = Field(None, description="Updated featured status")
    tags: Optional[List[str]] = Field(None, description="Updated tags")


class SearchContinue(BaseModel):
    """Schema for continuing an existing search"""
    follow_up_query: str = Field(
        ..., 
        min_length=3,
        description="Follow-up query for an existing search"
    )
    thread_id: Optional[str] = Field(
        None,
        description="Optional thread ID for conversation tracking"
    )
    previous_messages: Optional[List[Dict[str, Any]]] = Field(
        default_factory=list,
        description="Previous messages for context maintenance"
    )
    search_params: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        description="Optional parameters to customize search behavior"
    )
    
    @validator("search_params")
    def validate_search_params(cls, v):
        allowed_keys = {"temperature", "max_tokens", "top_p", "top_k", "jurisdiction"}
        if v and not all(k in allowed_keys for k in v.keys()):
            raise ValueError(f"Invalid search parameters. Allowed keys: {allowed_keys}")
        try:
            import json
            json.dumps(v)
        except TypeError:
            raise ValueError("Search parameters must be JSON-serializable")
        return v


class CitationModel(BaseModel):
    """Schema for citations in search responses"""
    text: str
    url: str


class SearchMessageResponse(BaseModel):
    """Schema for search message responses"""
    role: str
    content: Dict[str, Any]
    sequence: int

    model_config = {"from_attributes": True}


class SearchResponse(SearchBase):
    """Schema for search responses"""
    id: UUID = Field(..., description="Unique search ID")
    query: str = Field(..., description="Search query")
    user_id: UUID = Field(..., description="ID of the search owner")
    enterprise_id: Optional[UUID] = Field(None, description="Enterprise ID if applicable")
    created_at: datetime = Field(..., description="Search creation timestamp")
    updated_at: Optional[datetime] = Field(None, description="Last update timestamp")
    category: Optional[QueryCategory] = Field(None, description="Query category")
    query_type: Optional[QueryType] = Field(None, description="Query type")
    messages: List[SearchMessageResponse] = Field(
        default_factory=list,
        description="Associated messages"
    )

    model_config = {"from_attributes": True}


class SearchListResponse(BaseModel):
    """Schema for paginated search list responses"""
    items: List[SearchResponse] = Field(..., description="List of searches")
    total: int = Field(..., description="Total number of items")
    offset: int = Field(..., description="Pagination offset", ge=0)
    limit: int = Field(..., description="Pagination limit", gt=0)