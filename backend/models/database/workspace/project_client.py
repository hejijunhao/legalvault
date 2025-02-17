# /backend/models/database/workspace/project_client.py

from datetime import datetime
from enum import Enum
from typing import Optional, List, TYPE_CHECKING
from sqlalchemy import Column, Index, String, DateTime
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlmodel import Field, SQLModel, Relationship, ForeignKey
from pydantic import validator
from abc import ABC

from .client import ClientBase
from .project import ProjectBase

class ClientProjectRole(str, Enum):
    """Role of the client in the project"""
    PRIMARY = "primary"        # Main client
    SECONDARY = "secondary"    # Secondary/related client
    OPPOSING = "opposing"      # Opposing party
    INTERESTED = "interested"  # Interested party
    OTHER = "other"           # Other role


class ProjectClientBase(SQLModel, ABC):
    """
    Abstract base class for the many-to-many relationship between Projects and Clients.
    Serves as a template for tenant-specific implementations.
    """
    __abstract__ = True

    __table_args__ = (
        Index("idx_project_client_role", "role"),
        Index("idx_project_client_created", "created_by")
    )

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
    
    # Additional metadata
    role: str = Field(
        sa_column=Column(String, nullable=False),
        default=ClientProjectRole.PRIMARY.value,
        description="Role of the client in the project"
    )

    @validator("role")
    def validate_role(cls, v):
        if isinstance(v, ClientProjectRole):
            return v.value
        if v not in [e.value for e in ClientProjectRole]:
            raise ValueError(f"Invalid role: {v}")
        return v

    billing_type: str = Field(
        sa_column=Column(String(50), nullable=True),
        description="Type of billing arrangement"
    )
    
    matter_number: Optional[str] = Field(
        sa_column=Column(String(100), nullable=True),
        description="Client's matter/reference number"
    )

    created_at: datetime = Field(
        sa_column=Column(DateTime, nullable=False),
        default_factory=datetime.utcnow,
        description="When the contact was created"
    )
    updated_at: datetime = Field(
        sa_column=Column(DateTime, nullable=False),
        default_factory=datetime.utcnow,
        description="When the contact was last updated"
    )
    created_by: UUID = Field(
        sa_column=Column(
            ForeignKey("vault.users.id", ondelete="SET NULL"),
            nullable=True
        )
    )
    modified_by: UUID = Field(
        sa_column=Column(
            ForeignKey("vault.users.id", ondelete="SET NULL"),
            nullable=True
        )
    )

    # Class Linkages
    project: Optional["ProjectBase"] = Relationship(
        back_populates="project_client",
        sa_relationship_kwargs={
            "lazy": "selectin",
            "primaryjoin": "and_(foreign(ProjectClientBase.project_id)==ProjectBase.project_id, "
                           "ProjectClientBase.__table__.schema==ProjectBase.__table__.schema)",
            "cascade": "all, delete"
        }
    )

    client: Optional["ClientBase"] = Relationship(
        back_populates="project_client",
        sa_relationship_kwargs={
            "lazy": "selectin",
            "primaryjoin": "and_(foreign(ProjectClientBase.client_id)==ClientBase.client_id, "
                           "ProjectClientBase.__table__.schema==ClientBase.__table__.schema)",
            "cascade": "all, delete"
        }
    )

    model_config = {
        "arbitrary_types_allowed": True
    }

class ProjectClientBlueprint(ProjectClientBase, table=True):
    """
    Concrete implementation of ProjectClientBase for the public schema blueprint.
    Serves as a reference for tenant-specific implementations.
    """
    __tablename__ = "project_client"
    __table_args__ = (
        *ProjectClientBase.__table_args__,
        {'schema': 'public'}
    )
