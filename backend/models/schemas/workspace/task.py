# models/schemas/workspace/task.py

from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, Field, validator, constr

from models.database.workspace.task import TaskStatus

# Type definitions for validation
TitleType = constr(min_length=1, max_length=255)
DescriptionType = constr(min_length=1, max_length=1000)


class TaskCreate(BaseModel):
    """Schema for creating a new task"""
    project_id: UUID = Field(
        ...,
        description="ID of the project this task belongs to"
    )
    title: TitleType = Field(
        ...,
        description="Title of the task",
        example="Draft Client Agreement"
    )
    description: Optional[DescriptionType] = Field(
        None,
        description="Detailed description of the task",
        example="Prepare initial draft of service agreement for client review"
    )
    due_date: datetime = Field(
        ...,
        description="Due date for the task"
    )
    assigned_to: UUID = Field(
        ...,
        description="User ID of task assignee"
    )

    @validator('title')
    def validate_title(cls, v):
        if not v.strip():
            raise ValueError('Task title cannot be empty or whitespace')
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


class TaskUpdate(BaseModel):
    """Schema for updating an existing task"""
    title: Optional[TitleType] = None
    description: Optional[DescriptionType] = None
    status: Optional[TaskStatus] = None
    due_date: Optional[datetime] = None
    assigned_to: Optional[UUID] = None

    @validator('title')
    def validate_title(cls, v):
        if v is not None:
            if not v.strip():
                raise ValueError('Task title cannot be empty or whitespace')
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


class TaskResponse(BaseModel):
    """Schema for task API responses"""
    task_id: UUID
    project_id: UUID
    title: str
    description: Optional[str]
    status: TaskStatus
    due_date: datetime
    assigned_to: UUID
    created_at: datetime
    updated_at: datetime
    created_by: UUID
    modified_by: UUID
    completed_at: Optional[datetime]
    is_overdue: bool = Field(
        default=False,
        description="Indicates if the task is overdue"
    )

    class Config:
        orm_mode = True
        schema_extra = {
            "example": {
                "task_id": "123e4567-e89b-12d3-a456-426614174000",
                "project_id": "123e4567-e89b-12d3-a456-426614174001",
                "title": "Draft Client Agreement",
                "description": "Prepare initial draft of service agreement",
                "status": "todo",
                "due_date": "2024-02-01T15:00:00Z",
                "assigned_to": "123e4567-e89b-12d3-a456-426614174002",
                "created_at": "2024-01-15T12:00:00Z",
                "updated_at": "2024-01-15T12:00:00Z",
                "completed_at": None,
                "is_overdue": False
            }
        }


class TaskListResponse(BaseModel):
    """Schema for task list responses"""
    task_id: UUID
    project_id: UUID
    title: str
    status: TaskStatus
    due_date: datetime
    assigned_to: UUID
    is_overdue: bool
    completed_at: Optional[datetime]

    class Config:
        orm_mode = True
        schema_extra = {
            "example": {
                "task_id": "123e4567-e89b-12d3-a456-426614174000",
                "project_id": "123e4567-e89b-12d3-a456-426614174001",
                "title": "Draft Client Agreement",
                "status": "todo",
                "due_date": "2024-02-01T15:00:00Z",
                "assigned_to": "123e4567-e89b-12d3-a456-426614174002",
                "completed_at": None,
                "is_overdue": False
            }
        }