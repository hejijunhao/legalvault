# models/dtos/research/search_dto.py

from datetime import datetime
from typing import Dict, List, Optional, Any, Union
from uuid import UUID
from pydantic import BaseModel, Field
from enum import Enum

# Enums for DTO layer - these mirror the domain model enums
class QueryCategoryDTO(str, Enum):
    CLEAR = "clear"
    UNCLEAR = "unclear"
    IRRELEVANT = "irrelevant"
    BORDERLINE = "borderline"

class QueryTypeDTO(str, Enum):
    COURT_CASE = "court_case"
    LEGISLATIVE = "legislative"
    COMMERCIAL = "commercial"
    GENERAL = "general"

class QueryStatusDTO(str, Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    NEEDS_CLARIFICATION = "needs_clarification"
    IRRELEVANT = "irrelevant_query"

# Base DTOs
class SearchMessageDTO(BaseModel):
    """DTO for search messages"""
    role: str
    content: Dict[str, Any]
    sequence: int

class SearchDTO(BaseModel):
    """Core DTO for search data transfer between layers"""
    id: UUID
    title: str
    description: Optional[str] = None
    user_id: UUID
    enterprise_id: Optional[UUID] = None
    is_featured: bool = False
    tags: List[str] = Field(default_factory=list)
    search_params: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime
    updated_at: datetime
    status: str
    messages: List[SearchMessageDTO] = Field(default_factory=list)
    
    class Config:
        from_attributes = True

# Specialized DTOs
class SearchListDTO(BaseModel):
    """DTO for transferring lists of searches"""
    items: List[SearchDTO]
    total: int
    offset: int
    limit: int

class SearchStatusDTO(BaseModel):
    """DTO for search status information"""
    id: str
    status: str
    created_at: datetime
    updated_at: datetime
    message_count: int

class SearchCreateDTO(BaseModel):
    """DTO for creating a new search"""
    user_id: UUID
    query: str
    enterprise_id: Optional[UUID] = None
    search_params: Optional[Dict[str, Any]] = None
    title: Optional[str] = None
    description: Optional[str] = None
    tags: List[str] = Field(default_factory=list)
    is_featured: bool = False

class SearchUpdateDTO(BaseModel):
    """DTO for updating search metadata"""
    title: Optional[str] = None
    description: Optional[str] = None
    is_featured: Optional[bool] = None
    tags: Optional[List[str]] = None
    status: Optional[str] = None

class SearchContinueDTO(BaseModel):
    """DTO for continuing an existing search"""
    search_id: UUID
    user_id: UUID
    follow_up_query: str
    enterprise_id: Optional[UUID] = None
    thread_id: Optional[str] = None
    previous_messages: Optional[List[Dict[str, Any]]] = None

class SearchResultDTO(BaseModel):
    """DTO for search execution results from workflow"""
    thread_id: Optional[str] = None
    text: str
    citations: List[Dict[str, str]] = Field(default_factory=list)
    token_usage: int = 0
    metadata: Dict[str, Any] = Field(default_factory=dict)
    error: Optional[str] = None
    
    @property
    def has_error(self) -> bool:
        return self.error is not None

# Conversion functions
def to_search_dto(db_search: Any) -> SearchDTO:
    """Convert database model to SearchDTO"""
    messages = []
    if hasattr(db_search, "messages") and db_search.messages:
        messages = [
            SearchMessageDTO(
                role=msg.role,
                content=msg.content,
                sequence=msg.sequence
            ) for msg in sorted(db_search.messages, key=lambda m: m.sequence)
        ]
    
    # Determine status based on metadata or default to COMPLETED
    status = QueryStatusDTO.COMPLETED
    if db_search.search_params and "metadata" in db_search.search_params:
        metadata = db_search.search_params.get("metadata", {})
        if "query_analysis" in metadata:
            query_analysis = metadata["query_analysis"]
            if query_analysis.get("category") == "unclear":
                status = QueryStatusDTO.NEEDS_CLARIFICATION
            elif query_analysis.get("category") == "irrelevant":
                status = QueryStatusDTO.IRRELEVANT
    
    return SearchDTO(
        id=db_search.id,
        title=db_search.title,
        description=db_search.description,
        user_id=db_search.user_id,
        enterprise_id=db_search.enterprise_id,
        is_featured=db_search.is_featured,
        tags=db_search.tags or [],
        search_params=db_search.search_params or {},
        created_at=db_search.created_at,
        updated_at=db_search.updated_at,
        status=status,
        messages=messages
    )

def to_search_dto_without_messages(db_search: Any) -> SearchDTO:
    """Convert database model to SearchDTO without loading messages (for list views)"""
    # Determine status from string or enum
    status = db_search.status
    if hasattr(status, "value"):
        status = status.value
    
    return SearchDTO(
        id=db_search.id,
        title=db_search.title,
        description=db_search.description,
        user_id=db_search.user_id,
        enterprise_id=db_search.enterprise_id,
        is_featured=db_search.is_featured if hasattr(db_search, "is_featured") else False,
        tags=db_search.tags or [],
        search_params=db_search.search_params or {},
        created_at=db_search.created_at,
        updated_at=db_search.updated_at,
        status=status,
        messages=[]  # Empty list for messages to avoid loading them
    )

def to_search_list_dto(db_searches: List[Any], total: int, offset: int, limit: int) -> SearchListDTO:
    """Convert list of database models to SearchListDTO"""
    return SearchListDTO(
        items=[to_search_dto(db_search) for db_search in db_searches],
        total=total,
        offset=offset,
        limit=limit
    )

def to_search_status_dto(search: Any) -> SearchStatusDTO:
    """Convert SearchDTO or database model to SearchStatusDTO"""
    # If it's a database model, convert to DTO first
    if not isinstance(search, SearchDTO):
        # Determine status from string or enum
        status = search.status
        if hasattr(status, "value"):
            status = status.value
            
        # Get message count
        message_count = 0
        if hasattr(search, "messages") and search.messages is not None:
            message_count = len(search.messages)
            
        return SearchStatusDTO(
            id=str(search.id),
            status=status,
            created_at=search.created_at,
            updated_at=search.updated_at,
            message_count=message_count
        )
    else:
        # It's already a SearchDTO
        return SearchStatusDTO(
            id=str(search.id),
            status=search.status,
            created_at=search.created_at,
            updated_at=search.updated_at,
            message_count=len(search.messages)
        )