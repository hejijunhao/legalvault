# /backend/models/database/workspace/project_client.py

from datetime import datetime
from typing import Optional
from sqlmodel import Field, SQLModel
from sqlalchemy import Column, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import text


class ProjectClient(SQLModel, table=True):
    """
    Association table for the many-to-many relationship between Projects and Clients.
    """
    __tablename__ = "project_clients"

    project_id: UUID = Field(
        default=None,
        sa_column=Column(
            ForeignKey("projects.project_id", ondelete="CASCADE"),
            primary_key=True,
            nullable=False
        )
    )
    client_id: UUID = Field(
        default=None,
        sa_column=Column(
            ForeignKey("clients.client_id", ondelete="CASCADE"),
            primary_key=True,
            nullable=False
        )
    )
    
    # Additional metadata fields
    role: str = Field(default="primary", description="Role of the client in the project (e.g., primary, secondary)")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    created_by: UUID = Field(
        default=None,
        sa_column=Column(
            ForeignKey("users.id", ondelete="SET NULL"),
            nullable=True
        )
    )

    class Config:
        arbitrary_types_allowed = True