# /backend/models/database/workspace/project_client.py

from datetime import datetime
from enum import Enum
from typing import Optional, List, TYPE_CHECKING
from sqlalchemy import Column, Index, String, JSONB
from sqlalchemy.dialects.postgresql import UUID
from sqlmodel import Field, SQLModel, Relationship, ForeignKey
from pydantic import validator
from abc import ABC

if TYPE_CHECKING:
    from .client import ClientBase
    from .project import ProjectBase

class ClientProjectRole(str, Enum):
    """Role of the client in the project"""
    PRIMARY = "primary"        # Main client
    SECONDARY = "secondary"    # Secondary/related client
    OPPOSING = "opposing"      # Opposing party
    INTERESTED = "interested"  # Interested party
    OTHER = "other"           # Other role


class ProjectClientMetadata(SQLModel):
    """Additional metadata for project-client relationship"""
    billing_type: str = Field(default="hourly", description="Type of billing arrangement")
    matter_number: Optional[str] = Field(default=None, description="Client's matter/reference number")
    engagement_terms: dict = Field(
        default_factory=lambda: {
            "billing_rate": None,
            "retainer_amount": None,
            "payment_terms": "net-30"
        }
    )
    notes: str = Field(default="", description="Additional notes about the relationship")


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
            ForeignKey("enterprise_schema.projects.project_id", ondelete="CASCADE"),
            primary_key=True,
            nullable=False
        )
    )
    client_id: UUID = Field(
        default=None,
        sa_column=Column(
            ForeignKey("enterprise_schema.clients.client_id", ondelete="CASCADE"),
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
    
    metadata: ProjectClientMetadata = Field(
        sa_column=Column(JSONB, nullable=False),
        default_factory=ProjectClientMetadata,
        description="Additional metadata about the project-client relationship"
    )

    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        nullable=False,
        sa_column=Column(nullable=False)
    )
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        nullable=False,
        sa_column=Column(nullable=False)
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
    project: Optional["ProjectBase"] = None
    client: Optional["ClientBase"] = None

    _project = Relationship(
        back_populates="_project_client",
        sa_relationship_kwargs={
            "lazy": "selectin",
            "cascade": "all, delete",
            "primaryjoin": "and_(foreign(ProjectClientBase.project_id)==ProjectBase.project_id, ProjectClientBase.__table__.schema==ProjectBase.__table__.schema)"
        }
    )

    _client = Relationship(
        back_populates="_project_client",
        sa_relationship_kwargs={
            "lazy": "selectin",
            "cascade": "all, delete",
            "primaryjoin": "and_(foreign(ProjectClientBase.client_id)==ClientBase.client_id, ProjectClientBase.__table__.schema==ClientBase.__table__.schema)"
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
    __tablename__ = "project_client_blueprint"
    __table_args__ = (
        Index("idx_project_client_role", "role"),
        Index("idx_project_client_created", "created_by"),
        {'schema': 'public'}
    )

class ProjectClient(ProjectClientBase):
    """
    Concrete implementation of ProjectClientBase for enterprise schemas.
    """
    __tablename__ = "project_clients"