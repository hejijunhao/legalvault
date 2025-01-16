# backend/models/schemas/workspace/notebook.py

from datetime import datetime
from typing import List, Optional, Annotated
from uuid import UUID
from pydantic import BaseModel, Field, validator, constr

# Type definitions for validation
TitleType = constr(min_length=1, max_length=255)
TagType = constr(min_length=1, max_length=50)
ContentType = constr(min_length=0, max_length=50000)  # Allow empty content


class NotebookCreate(BaseModel):
    """Schema for creating a new notebook"""
    title: Optional[TitleType] = Field(
        None,
        description="Optional notebook title",
        example="Project Research Notes"
    )
    content: ContentType = Field(
        default="",
        description="Initial notebook content",
        example="<rich-text>Initial project notes...</rich-text>"
    )
    tags: Annotated[List[TagType], Field(
        default=[],
        description="Initial notebook tags",
        example=["research", "notes", "draft"]
    )]

    @validator('title')
    def validate_title(cls, v):
        if v is not None:
            v = v.strip()
            if not v:
                return None
        return v

    @validator('tags')
    def validate_tags(cls, v):
        # Remove duplicates while preserving order
        seen = set()
        unique_tags = []
        for tag in v:
            tag_stripped = tag.strip()
            if tag_stripped and tag_stripped not in seen:
                seen.add(tag_stripped)
                unique_tags.append(tag_stripped)
        return unique_tags


class NotebookUpdate(BaseModel):
    """Schema for updating notebook properties"""
    title: Optional[TitleType] = Field(
        None,
        description="Updated notebook title"
    )
    tags: Optional[List[TagType]] = Field(
        None,
        description="Updated tag list"
    )

    @validator('title')
    def validate_title(cls, v):
        if v is not None:
            v = v.strip()
            if not v:
                return None
        return v

    @validator('tags')
    def validate_tags(cls, v):
        if v is None:
            return v
        seen = set()
        unique_tags = []
        for tag in v:
            tag_stripped = tag.strip()
            if tag_stripped and tag_stripped not in seen:
                seen.add(tag_stripped)
                unique_tags.append(tag_stripped)
        return unique_tags


class NotebookContentUpdate(BaseModel):
    """Schema for updating notebook content"""
    content: ContentType = Field(
        ...,  # Required field
        description="Updated notebook content",
        example="<rich-text>Updated content with new information...</rich-text>"
    )


class NotebookResponse(BaseModel):
    """Schema for notebook API responses"""
    notebook_id: UUID
    project_id: UUID
    title: Optional[str]
    content: str
    tags: List[str]
    is_archived: bool
    created_by: UUID
    modified_by: UUID
    created_at: datetime
    updated_at: datetime
    last_modified_content: datetime

    class Config:
        orm_mode = True
        schema_extra = {
            "example": {
                "notebook_id": "123e4567-e89b-12d3-a456-426614174000",
                "project_id": "123e4567-e89b-12d3-a456-426614174001",
                "title": "Project Research Notes",
                "content": "<rich-text>Project research and findings...</rich-text>",
                "tags": ["research", "notes", "draft"],
                "is_archived": False,
                "created_by": "123e4567-e89b-12d3-a456-426614174002",
                "modified_by": "123e4567-e89b-12d3-a456-426614174002",
                "created_at": "2024-01-15T12:00:00Z",
                "updated_at": "2024-01-15T12:00:00Z",
                "last_modified_content": "2024-01-15T12:00:00Z"
            }
        }


class NotebookListResponse(BaseModel):
    """Schema for notebook list responses"""
    notebook_id: UUID
    project_id: UUID
    title: Optional[str]
    is_archived: bool
    updated_at: datetime
    last_modified_content: datetime

    class Config:
        orm_mode = True
        schema_extra = {
            "example": {
                "notebook_id": "123e4567-e89b-12d3-a456-426614174000",
                "project_id": "123e4567-e89b-12d3-a456-426614174001",
                "title": "Project Research Notes",
                "is_archived": False,
                "updated_at": "2024-01-15T12:00:00Z",
                "last_modified_content": "2024-01-15T12:00:00Z"
            }
        }