# models/dtos/research/search_message_dto.py

from datetime import datetime
from typing import Dict, List, Optional, Any, Union
from uuid import UUID
from pydantic import BaseModel, Field

class CitationDTO(BaseModel):
    """DTO for citations in search responses"""
    text: str
    url: str

class SearchMessageDTO(BaseModel):
    """Core DTO for search message data transfer between layers"""
    id: UUID
    search_id: UUID
    role: str
    content: Dict[str, Any]
    sequence: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class SearchMessageCreateDTO(BaseModel):
    """DTO for creating a new search message"""
    search_id: UUID
    role: str
    content: Dict[str, Any]
    sequence: Optional[int] = None

class SearchMessageUpdateDTO(BaseModel):
    """DTO for updating a search message"""
    content: Optional[Dict[str, Any]] = None
    sequence: Optional[int] = None

class SearchMessageListDTO(BaseModel):
    """DTO for transferring lists of search messages"""
    items: List[SearchMessageDTO]
    total: int
    search_id: UUID

# Conversion functions
def to_search_message_dto(db_message: Any) -> SearchMessageDTO:
    """Convert database model to SearchMessageDTO"""
    return SearchMessageDTO(
        id=db_message.id,
        search_id=db_message.search_id,
        role=db_message.role,
        content=db_message.content,
        sequence=db_message.sequence,
        created_at=db_message.created_at,
        updated_at=db_message.updated_at
    )

def to_search_message_list_dto(db_messages: List[Any], total: int, search_id: UUID) -> SearchMessageListDTO:
    """Convert list of database models to SearchMessageListDTO"""
    return SearchMessageListDTO(
        items=[to_search_message_dto(db_message) for db_message in db_messages],
        total=total,
        search_id=search_id
    )

# Helper functions for workflow integration
def format_message_for_workflow(message_dto: SearchMessageDTO) -> Dict[str, Any]:
    """Format a message DTO for use in workflow layer"""
    return {
        "role": message_dto.role,
        "content": message_dto.content,
        "sequence": message_dto.sequence,
        "id": str(message_dto.id),
        "search_id": str(message_dto.search_id),
        "created_at": message_dto.created_at.isoformat()
    }

def format_messages_for_workflow(message_dtos: List[SearchMessageDTO]) -> List[Dict[str, Any]]:
    """Format a list of message DTOs for use in workflow layer"""
    return [format_message_for_workflow(dto) for dto in message_dtos]