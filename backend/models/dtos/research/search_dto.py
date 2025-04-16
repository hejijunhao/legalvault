# models/dtos/research/search_dto.py

from datetime import datetime
from typing import Dict, List, Optional, Any
from uuid import UUID
from pydantic import BaseModel, Field

from models.enums.research_enums import QueryCategory, QueryType, QueryStatus
from models.dtos.base_dto import PaginatedListDTO, StatusDTO, TupleConverterMixin
from models.dtos.research.search_message_dto import SearchMessageDTO  # Added import for type hint

# Field mappings for tuple conversion
SEARCH_TUPLE_FIELDS = {
    0: "id",
    1: "title",
    2: "description",
    3: "user_id",
    4: "enterprise_id",
    5: "is_featured",
    6: "tags",
    7: "search_params",
    8: "category",
    9: "query_type",
    10: "created_at",
    11: "updated_at"
}

class SearchDTO(BaseModel, TupleConverterMixin):
    """Core DTO for search data transfer between layers"""
    id: UUID
    title: str
    description: Optional[str] = None
    user_id: UUID
    enterprise_id: Optional[UUID] = None
    is_featured: bool = False
    tags: List[str] = Field(default_factory=list)
    search_params: Dict[str, Any] = Field(default_factory=dict)
    category: Optional[QueryCategory] = None
    query_type: Optional[QueryType] = None
    created_at: datetime
    updated_at: datetime
    messages: Optional[List[SearchMessageDTO]] = Field(
        default_factory=list,
        description="List of messages associated with this search, ordered by sequence"
    )  # Added messages field
    
    class Config:
        from_attributes = True

    @classmethod
    def from_db(cls, db_search: Any) -> "SearchDTO":
        """Create DTO from database model or tuple"""
        if isinstance(db_search, tuple):
            return cls.from_tuple(db_search, SEARCH_TUPLE_FIELDS)
        return cls(
            id=db_search.id,
            title=db_search.title,
            description=db_search.description,
            user_id=db_search.user_id,
            enterprise_id=db_search.enterprise_id,
            is_featured=db_search.is_featured,
            tags=db_search.tags or [],
            search_params=db_search.search_params or {},
            category=None,  # Not persisted in DB, set to None
            query_type=None,  # Not persisted in DB, set to None
            created_at=db_search.created_at,
            updated_at=db_search.updated_at,
            messages=[SearchMessageDTO.from_db(msg) for msg in getattr(db_search, 'messages', [])]  # Populate messages
        )

class SearchListDTO(PaginatedListDTO[SearchDTO]):
    """DTO for transferring lists of searches"""
    pass

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
    """DTO for continuing an existing search with follow-up queries"""
    search_id: UUID = Field(..., description="ID of the search to continue")
    user_id: UUID = Field(..., description="ID of the user making the follow-up query")
    follow_up_query: str = Field(..., description="The follow-up question or query")
    enterprise_id: Optional[UUID] = Field(None, description="Enterprise ID for the search context")
    thread_id: Optional[str] = Field(None, description="Optional thread ID for conversation tracking")
    previous_messages: Optional[List[Dict[str, Any]]] = Field(
        default_factory=list,
        description="Previous messages for context maintenance"
    )
    search_params: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        description="Optional parameters to customize the search behavior"
    )

    def validate_query(self) -> bool:
        """Validate the follow-up query"""
        # Basic validation rules
        if not self.follow_up_query or len(self.follow_up_query.strip()) < 3:
            return False
        
        # Check for non-printable characters
        if not all(char.isprintable() for char in self.follow_up_query):
            return False
            
        # Check for reasonable length (e.g., not too long)
        if len(self.follow_up_query) > 1000:
            return False
            
        return True

    def get_context(self) -> Dict[str, Any]:
        """Get the context for the follow-up query"""
        return {
            "thread_id": self.thread_id,
            "previous_messages": self.previous_messages,
            "search_params": self.search_params
        }

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
    return SearchDTO.from_db(db_search)

def to_search_dto_without_messages(db_search: Any) -> SearchDTO:
    """Convert database model to SearchDTO without loading messages"""
    dto = SearchDTO.from_db(db_search)
    dto.messages = []  # Explicitly set messages to empty list
    return dto

def to_search_list_dto(
    db_searches: List[Any],
    total: int,
    offset: int = 0,
    limit: int = 10
) -> SearchListDTO:
    """Convert list of database models to SearchListDTO"""
    return SearchListDTO(
        items=[to_search_dto_without_messages(s) for s in db_searches],
        total=total,
        offset=offset,
        limit=limit
    )