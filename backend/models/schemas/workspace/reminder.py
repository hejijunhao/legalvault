# models/schemas/workspace/reminder.py

from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, Field, validator, constr

from models.database.workspace.reminder import ReminderStatus

# Type definitions for validation
TitleType = constr(min_length=1, max_length=255)
DescriptionType = constr(min_length=1, max_length=1000)


class ReminderCreate(BaseModel):
    """Schema for creating a new reminder"""
    project_id: UUID = Field(
        ...,
        description="ID of the project this reminder belongs to"
    )
    title: TitleType = Field(
        ...,
        description="Title of the reminder",
        example="Review Contract Draft"
    )
    description: Optional[DescriptionType] = Field(
        None,
        description="Detailed description of the reminder",
        example="Review latest version of merger agreement before client meeting"
    )
    due_date: datetime = Field(
        ...,
        description="Due date for the reminder"
    )

    @validator('title')
    def validate_title(cls, v):
        if not v.strip():
            raise ValueError('Reminder title cannot be empty or whitespace')
        return v.strip()

    @validator('description')
    def validate_description(cls, v):
        if v is not None:
            v = v.strip()
            if not v:
                return None
        return v

    @validator('due_date')
    def validate_due_date(cls, v):
        if v < datetime.utcnow():
            raise ValueError('Due date cannot be in the past')
        return v


class ReminderUpdate(BaseModel):
    """Schema for updating an existing reminder"""
    title: Optional[TitleType] = None
    description: Optional[DescriptionType] = None
    status: Optional[ReminderStatus] = None
    due_date: Optional[datetime] = None

    @validator('title')
    def validate_title(cls, v):
        if v is not None:
            if not v.strip():
                raise ValueError('Reminder title cannot be empty or whitespace')
            return v.strip()
        return v

    @validator('description')
    def validate_description(cls, v):
        if v is not None:
            v = v.strip()
            if not v:
                return None
        return v

    @validator('due_date')
    def validate_due_date(cls, v):
        if v is not None and v < datetime.utcnow():
            raise ValueError('Due date cannot be in the past')
        return v


class ReminderResponse(BaseModel):
    """Schema for reminder API responses"""
    reminder_id: UUID
    project_id: UUID
    title: str
    description: Optional[str]
    status: ReminderStatus
    due_date: datetime
    created_at: datetime
    updated_at: datetime
    created_by: UUID
    modified_by: UUID
    is_overdue: bool = Field(
        default=False,
        description="Indicates if the reminder is overdue"
    )

    class Config:
        orm_mode = True
        schema_extra = {
            "example": {
                "reminder_id": "123e4567-e89b-12d3-a456-426614174000",
                "project_id": "123e4567-e89b-12d3-a456-426614174001",
                "title": "Review Contract Draft",
                "description": "Review latest version of merger agreement",
                "status": "pending",
                "due_date": "2024-02-01T15:00:00Z",
                "created_at": "2024-01-15T12:00:00Z",
                "updated_at": "2024-01-15T12:00:00Z",
                "is_overdue": False
            }
        }


class ReminderListResponse(BaseModel):
    """Schema for reminder list responses"""
    reminder_id: UUID
    project_id: UUID
    title: str
    status: ReminderStatus
    due_date: datetime
    is_overdue: bool

    class Config:
        orm_mode = True
        schema_extra = {
            "example": {
                "reminder_id": "123e4567-e89b-12d3-a456-426614174000",
                "project_id": "123e4567-e89b-12d3-a456-426614174001",
                "title": "Review Contract Draft",
                "status": "pending",
                "due_date": "2024-02-01T15:00:00Z",
                "is_overdue": False
            }
        }