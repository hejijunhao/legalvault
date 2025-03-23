# models/dtos/research/search_dto.py

from datetime import datetime
from typing import Dict, List, Optional, Any, Union
from uuid import UUID
from pydantic import BaseModel, Field

# Import enums from centralized location and rename with DTO suffix
from models.enums.research_enums import QueryCategory as QueryCategoryDTO
from models.enums.research_enums import QueryType as QueryTypeDTO

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
    
    class Config:
        from_attributes = True

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
    """
    Convert database model to SearchDTO.
    
    Args:
        db_search: Database model instance or tuple
        
    Returns:
        SearchDTO with data from model
    """
    if isinstance(db_search, tuple):
        return _tuple_to_search_dto(db_search)
    
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
        messages=[SearchMessageDTO(**msg.to_dict()) for msg in db_search.messages] if hasattr(db_search, 'messages') else []
    )

def to_search_dto_without_messages(db_search: Any) -> SearchDTO:
    """
    Convert database model to SearchDTO without loading messages (for list views).
    
    Args:
        db_search: Database model instance or tuple
        
    Returns:
        SearchDTO with data from model, but without messages
    """
    if isinstance(db_search, tuple):
        return _tuple_to_search_dto(db_search)
    
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
        messages=[]
    )

def to_search_list_dto(db_searches: List[Any], total: int, offset: int = 0, limit: int = 10) -> SearchListDTO:
    """
    Convert list of database models to SearchListDTO.
    
    Args:
        db_searches: List of database model instances or tuples
        total: Total number of items in database
        offset: Starting offset for pagination
        limit: Number of items per page
        
    Returns:
        SearchListDTO with converted items and pagination info
    """
    return SearchListDTO(
        items=[to_search_dto_without_messages(s) for s in db_searches],
        total=total,
        offset=offset,
        limit=limit
    )