# models/dtos/research/search_message_dto.py

from datetime import datetime
from typing import Dict, List, Optional, Any
from uuid import UUID
from pydantic import BaseModel, Field

from models.enums.research_enums import QueryStatus
from models.dtos.base_dto import PaginatedListDTO, StatusDTO, TupleConverterMixin

# Field mappings for tuple conversion
MESSAGE_TUPLE_FIELDS = {
    0: "id",
    1: "search_id",
    2: "role",
    3: "content",
    4: "sequence",
    5: "status",
    6: "created_at",
    7: "updated_at"
}

class CitationDTO(BaseModel):
    """Value object for citations in search responses"""
    text: str
    url: str
    title: Optional[str] = None
    source: Optional[str] = None
    timestamp: Optional[datetime] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert citation to dictionary format"""
        return {
            "text": self.text,
            "url": self.url,
            "title": self.title,
            "source": self.source,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "CitationDTO":
        if "timestamp" in data and isinstance(data["timestamp"], str):
            data["timestamp"] = datetime.fromisoformat(data["timestamp"])
        return cls(**data)


class MessageContentDTO(BaseModel):
    """Value object for structured message content"""
    text: str
    citations: List[CitationDTO] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert message content to dictionary format"""
        return {
            "text": self.text,
            "citations": [c.to_dict() for c in self.citations],
            "metadata": self.metadata
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "MessageContentDTO":
        if isinstance(data, dict):
            if "citations" in data:
                data["citations"] = [
                    CitationDTO.from_dict(c) if isinstance(c, dict) else c 
                    for c in data["citations"]
                ]
            return cls(**data)
        return cls(text=str(data), citations=[], metadata={})


class SearchMessageDTO(TupleConverterMixin, BaseModel):
    """DTO for search messages with tuple conversion support"""
    id: UUID
    search_id: UUID
    role: str
    content: Dict[str, Any]
    sequence: int
    status: str = QueryStatus.PENDING.value
    created_at: datetime
    updated_at: Optional[datetime] = None
    search_title: Optional[str] = None

    def get_structured_content(self) -> MessageContentDTO:
        """Get content as structured MessageContentDTO"""
        return MessageContentDTO.from_dict(self.content)

    @classmethod
    def from_db(cls, db_message: Any) -> "SearchMessageDTO":
        """Create DTO from database model or tuple"""
        if isinstance(db_message, tuple):
            return cls.from_tuple(db_message, MESSAGE_TUPLE_FIELDS)
        return cls(
            id=db_message.id,
            search_id=db_message.search_id,
            role=db_message.role,
            content=db_message.content,
            sequence=db_message.sequence,
            status=db_message.status,
            created_at=db_message.created_at,
            updated_at=db_message.updated_at,
            search_title=getattr(db_message, "search_title", None)
        )


class SearchMessageCreateDTO(BaseModel):
    """DTO for creating a new search message"""
    search_id: UUID
    role: str
    content: Dict[str, Any]
    sequence: Optional[int] = None
    status: str = QueryStatus.PENDING.value


class SearchMessageUpdateDTO(BaseModel):
    """DTO for updating a search message"""
    content: Optional[Dict[str, Any]] = None
    sequence: Optional[int] = None
    status: Optional[str] = None


class SearchMessageListDTO(PaginatedListDTO[SearchMessageDTO]):
    """DTO for transferring lists of search messages"""
    search_id: UUID


class WebSocketCommandDTO(BaseModel):
    """DTO for WebSocket commands"""
    command: str
    search_id: UUID
    data: Optional[Dict[str, Any]] = None


class WebSocketResponseDTO(BaseModel):
    """DTO for WebSocket responses"""
    event: str
    data: Dict[str, Any]
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "event": self.event,
            "data": self.data,
            "timestamp": self.timestamp.isoformat()
        }


class WebSocketErrorDTO(BaseModel):
    """DTO for WebSocket errors"""
    error: str
    code: str
    details: Optional[Dict[str, Any]] = None


# Conversion functions
def to_search_message_dto(db_message: Any) -> SearchMessageDTO:
    """Convert database model to SearchMessageDTO"""
    return SearchMessageDTO.from_db(db_message)


def to_search_message_list_dto(
    db_messages: List[Any],
    total: int,
    search_id: UUID,
    offset: int = 0,
    limit: int = 100
) -> SearchMessageListDTO:
    """Convert list of database models to SearchMessageListDTO"""
    return SearchMessageListDTO(
        items=[to_search_message_dto(msg) for msg in db_messages],
        total=total,
        search_id=search_id,
        offset=offset,
        limit=limit
    )


def format_message_for_workflow(message: SearchMessageDTO) -> Dict[str, Any]:
    """Format a message DTO for use in workflow layer"""
    content = message.get_structured_content()
    return {
        "role": message.role,
        "content": content.to_dict(),
        "sequence": message.sequence,
        "id": str(message.id),
        "search_id": str(message.search_id),
        "status": message.status,
        "created_at": message.created_at.isoformat()
    }


def format_messages_for_workflow(messages: List[SearchMessageDTO]) -> List[Dict[str, Any]]:
    """Format a list of message DTOs for use in workflow layer"""
    return [format_message_for_workflow(msg) for msg in messages]

