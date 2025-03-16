# models/schemas/research/search.py

from datetime import datetime
from typing import Dict, List, Optional, Any
from uuid import UUID
from pydantic import BaseModel, Field, validator
from enum import Enum

# Mirror domain model enums for API layer
class QueryCategory(str, Enum):
    CLEAR = "clear"
    UNCLEAR = "unclear"
    IRRELEVANT = "irrelevant"
    BORDERLINE = "borderline"  # For queries that might need review

class QueryType(str, Enum):
    COURT_CASE = "court_case"
    LEGISLATIVE = "legislative"
    COMMERCIAL = "commercial"
    GENERAL = "general"

class QueryStatus(str, Enum):
    COMPLETED = "completed"
    FAILED = "failed"
    NEEDS_CLARIFICATION = "needs_clarification"
    IRRELEVANT = "irrelevant_query"

class SearchBase(BaseModel):
    """Base schema with common search fields"""
    query: str = Field(..., min_length=3, description="Search query text")

class SearchCreate(SearchBase):
    """Schema for creating a new search"""
    search_params: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        description="Optional parameters to customize search behavior"
    )
    
    @validator("search_params")
    def validate_search_params(cls, v):
        allowed_keys = {"temperature", "max_tokens", "top_p", "top_k", "jurisdiction"}
        if v and not all(k in allowed_keys for k in v.keys()):
            raise ValueError(f"Invalid search parameters. Allowed keys: {allowed_keys}")
        return v

class SearchContinue(BaseModel):
    """Schema for continuing an existing search"""
    follow_up_query: str = Field(
        ..., 
        min_length=3,
        description="Follow-up query for an existing search"
    )

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
    """Schema for search API responses"""
    id: UUID
    title: str
    description: Optional[str] = None
    user_id: UUID
    enterprise_id: Optional[UUID] = None
    is_featured: bool = False
    tags: Optional[List[str]] = None
    search_params: Dict[str, Any]
    created_at: datetime
    updated_at: datetime
    messages: List[SearchMessageResponse]
    status: QueryStatus
    category: Optional[QueryCategory] = None
    query_type: Optional[QueryType] = None

    model_config = {"from_attributes": True}

class SearchListResponse(BaseModel):
    items: List[SearchResponse]
    total: int
    offset: int
    limit: int

class SearchUpdate(BaseModel):
    """Schema for updating search metadata"""
    title: Optional[str] = None
    description: Optional[str] = None
    is_featured: Optional[bool] = None
    tags: Optional[List[str]] = None
    category: Optional[QueryCategory] = None
    query_type: Optional[QueryType] = None
    status: Optional[QueryStatus] = None
    
    model_config = {"from_attributes": True}