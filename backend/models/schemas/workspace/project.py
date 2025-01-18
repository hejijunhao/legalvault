# models/schemas/workspace/project.py

from datetime import datetime
from typing import List, Optional, Annotated, Dict, Any
from uuid import UUID
from pydantic import BaseModel, Field, validator, constr
from models.database.workspace.project import ProjectStatus, ConfidentialityLevel, ProjectKnowledge
from models.schemas.workspace.reminder import ReminderListResponse
from models.schemas.workspace.task import TaskListResponse

# Type definitions for validation
TagType = constr(min_length=1, max_length=50)
ContentType = constr(min_length=1, max_length=50000)
NameType = constr(min_length=1, max_length=255)
PracticeAreaType = constr(min_length=1, max_length=100)
SummaryType = constr(min_length=1, max_length=2000)


class ProjectKnowledgeSchema(BaseModel):
    """Schema for validating project knowledge data"""
    content: ContentType = Field(
        ...,
        description="Rich text content of project knowledge",
        example="Project involves handling multiple jurisdictions..."
    )
    last_updated: datetime = Field(
        default_factory=datetime.utcnow,
        description="Timestamp of last knowledge update"
    )


class NotebookStatusSchema(BaseModel):
    """Schema for notebook status information"""
    notebook_id: UUID
    is_archived: bool = False
    last_modified: datetime
    has_content: bool = False

class ProjectCreate(BaseModel):
    """Schema for creating a new project"""
    name: NameType = Field(
        ...,
        description="Project name",
        example="Smith v. Johnson Litigation"
    )
    practice_area: Optional[PracticeAreaType] = Field(
        None,
        description="Area of legal practice",
        example="Corporate Law"
    )
    confidentiality: ConfidentialityLevel = Field(
        default=ConfidentialityLevel.CONFIDENTIAL,
        description="Project confidentiality level"
    )
    start_date: Optional[datetime] = Field(
        None,
        description="Project start date"
    )
    tags: Annotated[List[TagType], Field(
        default=[],
        description="Project tags",
        example=["litigation", "corporate", "urgent"]
    )]
    create_notebook: bool = Field(
        default=True,
        description="Flag to automatically create an associated notebook"
    )

    @validator('name')
    def validate_name(cls, v):
        if not v.strip():
            raise ValueError('Project name cannot be empty or whitespace')
        return v.strip()

    @validator('tags')
    def validate_tags(cls, v):
        seen = set()
        unique_tags = []
        for tag in v:
            tag_stripped = tag.strip()
            if tag_stripped and tag_stripped not in seen:
                seen.add(tag_stripped)
                unique_tags.append(tag_stripped)
        return unique_tags

    @validator('start_date')
    def validate_start_date(cls, v):
        if v and v > datetime.utcnow():
            raise ValueError('Start date cannot be in the future')
        return v


class ProjectUpdate(BaseModel):
    """Schema for updating an existing project"""
    name: Optional[NameType] = None
    status: Optional[ProjectStatus] = None
    practice_area: Optional[PracticeAreaType] = None
    confidentiality: Optional[ConfidentialityLevel] = None
    start_date: Optional[datetime] = None
    tags: Optional[List[TagType]] = None

    @validator('name')
    def validate_name(cls, v):
        if v is not None and not v.strip():
            raise ValueError('Project name cannot be empty or whitespace')
        return v.strip() if v else v

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

    @validator('start_date')
    def validate_start_date(cls, v):
        if v and v > datetime.utcnow():
            raise ValueError('Start date cannot be in the future')
        return v


class ProjectKnowledgeUpdate(BaseModel):
    """Schema for updating project knowledge"""
    content: ContentType = Field(
        ...,
        description="Rich text content of project knowledge",
        example="Updated project scope includes..."
    )


class ProjectSummaryUpdate(BaseModel):
    """Schema for updating project summary"""
    summary: SummaryType = Field(
        ...,
        description="Condensed project summary",
        example="High-priority corporate litigation case involving..."
    )


class ProjectResponse(BaseModel):
    """Schema for project API responses"""
    project_id: UUID
    name: str
    status: ProjectStatus
    created_at: datetime
    updated_at: datetime
    created_by: UUID
    modified_by: UUID
    practice_area: Optional[str]
    confidentiality: ConfidentialityLevel
    start_date: Optional[datetime]
    tags: List[str]
    knowledge: Optional[ProjectKnowledge]
    summary: Optional[str]
    summary_updated_at: Optional[datetime]
    notebook_id: Optional[UUID]
    notebook_status: Optional[NotebookStatusSchema]
    tasks: Optional[List[TaskListResponse]] = None
    pending_tasks: Optional[List[TaskListResponse]] = None
    overdue_tasks: Optional[List[TaskListResponse]] = None

    class Config:
        orm_mode = True
        schema_extra = {
            "example": {
                "project_id": "123e4567-e89b-12d3-a456-426614174000",
                "name": "Smith v. Johnson Litigation",
                "status": "active",
                "practice_area": "Corporate Law",
                "tags": ["litigation", "corporate", "urgent"],
                "notebook_id": "123e4567-e89b-12d3-a456-426614174001",
                "notebook_status": {
                    "is_archived": False,
                    "last_modified": "2024-01-15T12:00:00Z",
                    "has_content": True
                }
            }
        }

    pending_reminders: Optional[List[ReminderListResponse]] = None
    overdue_reminders: Optional[List[ReminderListResponse]] = None

class ProjectListResponse(BaseModel):
    """Schema for project list responses"""
    project_id: UUID
    name: str
    status: ProjectStatus
    practice_area: Optional[str]
    updated_at: datetime
    summary: Optional[str]
    notebook_id: Optional[UUID]
    has_notebook: bool

    class Config:
        orm_mode = True
        schema_extra = {
            "example": {
                "project_id": "123e4567-e89b-12d3-a456-426614174000",
                "name": "Smith v. Johnson Litigation",
                "status": "active",
                "practice_area": "Corporate Law",
                "updated_at": "2024-01-15T12:00:00Z",
                "summary": "High-priority corporate litigation case...",
                "notebook_id": "123e4567-e89b-12d3-a456-426614174001",
                "has_notebook": True
            }
        }