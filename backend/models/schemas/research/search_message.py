# models/schemas/research/search_message.py

from datetime import datetime
from typing import Dict, List, Optional, Any, Literal
from uuid import UUID
from pydantic import BaseModel, Field, validator


class CitationResponse(BaseModel):
    """Schema for citation responses"""
    text: str = Field(..., description="Citation text", min_length=1)
    url: str = Field(..., description="Source URL", pattern=r'^https?://')
    title: Optional[str] = Field(None, description="Source title")
    source: Optional[str] = Field(None, description="Source name")
    timestamp: Optional[datetime] = Field(None, description="Citation timestamp")

    @validator('url')
    def validate_url(cls, v):
        if not v.startswith(('http://', 'https://')):
            raise ValueError('URL must start with http:// or https://')
        return v

    model_config = {"from_attributes": True}


class MessageContent(BaseModel):
    """Schema for structured message content"""
    text: str = Field(..., description="Message text", min_length=1)
    citations: List[CitationResponse] = Field(
        default_factory=list,
        description="List of citations"
    )
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Additional metadata"
    )

    @validator('metadata')
    def validate_metadata(cls, v):
        for key, value in v.items():
            if not isinstance(key, str):
                raise ValueError("Metadata keys must be strings")
            try:
                import json
                json.dumps(value)
            except TypeError:
                raise ValueError(f"Metadata value for key '{key}' must be JSON-serializable")
        return v


class SearchMessageBase(BaseModel):
    """Base schema with common message fields"""
    role: Literal["user", "assistant"] = Field(
        ...,
        description="Role of the message sender (user/assistant)"
    )
    content: MessageContent = Field(
        ...,
        description="Message content including text and metadata"
    )


class SearchMessageCreate(SearchMessageBase):
    """Schema for creating a new message"""
    search_id: UUID = Field(..., description="ID of the parent search")
    sequence: int = Field(..., description="Sequence number for ordering", ge=0)
    status: Optional[str] = Field(
        None,
        description="Initial message status",
        pattern=r'^(pending|processing|completed|failed)$'
    )


class SearchMessageUpdate(BaseModel):
    """Schema for updating a message"""
    content: Optional[MessageContent] = Field(
        None,
        description="Updated message content"
    )
    sequence: Optional[int] = Field(
        None,
        description="Updated sequence number",
        ge=0
    )
    status: Optional[str] = Field(
        None,
        description="Updated message status",
        pattern=r'^(pending|processing|completed|failed)$'
    )


class SearchMessageResponse(SearchMessageBase):
    """Schema for message responses"""
    id: UUID = Field(..., description="Unique message ID")
    search_id: UUID = Field(..., description="ID of the parent search")
    search_title: Optional[str] = Field(None, description="Title of the parent search")
    sequence: int = Field(..., description="Sequence number for ordering", ge=0)
    status: str = Field(
        ...,
        description="Message status",
        pattern=r'^(pending|processing|completed|failed)$'
    )
    created_at: datetime = Field(..., description="Message creation timestamp")
    updated_at: Optional[datetime] = Field(None, description="Last update timestamp")

    model_config = {"from_attributes": True}


class SearchMessageListResponse(BaseModel):
    """Schema for paginated message list responses"""
    items: List[SearchMessageResponse] = Field(..., description="List of messages")
    total: int = Field(..., description="Total number of messages")
    offset: int = Field(..., description="Pagination offset")
    limit: int = Field(..., description="Pagination limit")
