# models/schemas/research/search_message.py

from datetime import datetime
from typing import Dict, List, Optional, Any, Literal
from uuid import UUID
from pydantic import BaseModel, Field, validator


class SearchMessageBase(BaseModel):
    """Base schema with common message fields"""
    role: Literal["user", "assistant"] = Field(
        ...,
        description="Role of the message sender (user/assistant)"
    )
    content: Dict[str, Any] = Field(
        ...,
        description="Message content including text and metadata"
    )
    
    @validator('content')
    def validate_content(cls, v):
        if not isinstance(v, dict) or "text" not in v:
            raise ValueError("Content must be a dictionary with a 'text' key")
        return v


class SearchMessageCreate(SearchMessageBase):
    """Schema for creating a new message"""
    search_id: UUID = Field(..., description="ID of the parent search")
    sequence: int = Field(..., description="Sequence number for ordering")


class SearchMessageUpdate(BaseModel):
    """Schema for updating a message"""
    content: Optional[Dict[str, Any]] = Field(
        None,
        description="Updated message content"
    )
    
    @validator('content')
    def validate_content(cls, v):
        if v is not None and (not isinstance(v, dict) or "text" not in v):
            raise ValueError("Content must be a dictionary with a 'text' key")
        return v


class SearchMessageResponse(SearchMessageBase):
    """Schema for message responses"""
    id: UUID = Field(..., description="Unique message ID")
    search_id: UUID = Field(..., description="ID of the parent search")
    search_title: Optional[str] = Field(None, description="Title of the parent search")
    sequence: int = Field(..., description="Sequence number for ordering")
    created_at: datetime = Field(..., description="Message creation timestamp")
    updated_at: Optional[datetime] = Field(None, description="Last update timestamp")
    
    model_config = {"from_attributes": True}


class SearchMessageListResponse(BaseModel):
    """Schema for paginated message list responses"""
    items: List[SearchMessageResponse] = Field(..., description="List of messages")
    total: int = Field(..., description="Total number of messages")
    offset: int = Field(..., description="Pagination offset")
    limit: int = Field(..., description="Pagination limit")


class SearchMessageForwardRequest(BaseModel):
    """Schema for forwarding a message"""
    destination: str = Field(..., description="Destination identifier (email, user ID, etc.)")
    destination_type: Literal["email", "user", "whatsapp", "slack"] = Field(
        ...,
        description="Type of destination"
    )
