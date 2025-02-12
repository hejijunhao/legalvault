# models/database/longterm_memory/global_knowledge.py

from sqlmodel import SQLModel, Field, Index
from sqlalchemy import TIMESTAMP, Column, Text, ForeignKey, Enum as SQLEnum, UniqueConstraint
from typing import Optional
from datetime import datetime
from uuid import uuid4
from sqlalchemy.dialects.postgresql import UUID
from enum import Enum
from abc import ABC


class KnowledgeType(str, Enum):
    """Enumeration of possible knowledge types."""
    SYSTEM_STATS = "system_stats"
    USER_SPECIALIZATIONS = "user_specializations"
    ORGANIZATIONAL_POLICIES = "organizational_policies"
    PROJECT_OVERVIEW = "project_overview"
    INTEGRATION_ACCESS = "integration_access"


class GlobalKnowledgeBase(SQLModel, ABC):
    """
    Abstract base class representing a VP's global knowledge in the LegalVault system.
    Serves as a template for tenant-specific global knowledge implementations.
    Contains system-wide awareness and general domain knowledge.
    """
    __abstract__ = True

    __table_args__ = (
        UniqueConstraint('vp_id', 'knowledge_type'),
        Index("ix_global_knowledge_vp_id", "vp_id"),
        Index("ix_global_knowledge_last_updated", "last_updated"),
        {'schema': 'public'}
    )

    model_config = {
        "arbitrary_types_allowed": True,
        "json_schema_extra": {
            "examples": [
                {
                    "knowledge_type": "system_stats",
                    "prompt": "System-wide statistics and metrics..."
                }
            ]
        }
    }

    # Core Properties
    id: UUID = Field(
        default_factory=uuid4,
        primary_key=True,
        description="Unique identifier for the global knowledge record"
    )
    vp_id: UUID = Field(
        sa_column=Column(
            UUID(as_uuid=True),
            ForeignKey("vault.virtual_paralegals.id"),
            nullable=False
        ),
        description="Foreign key to the Virtual Paralegal"
    )

    # Knowledge Content
    knowledge_type: KnowledgeType = Field(
        sa_column=Column(SQLEnum(KnowledgeType)),
        description="Type of global knowledge"
    )
    prompt: str = Field(
        sa_column=Column(Text),
        description="Global knowledge prompt"
    )

    # Metadata
    last_updated: datetime = Field(
        sa_column=Column(TIMESTAMP(timezone=True)),
        default_factory=datetime.utcnow,
        description="Timestamp of last update"
    )

    def __repr__(self) -> str:
        """String representation of the Global Knowledge"""
        return f"GlobalKnowledge(id={self.id}, vp_id={self.vp_id}, type={self.knowledge_type})"


class GlobalKnowledge(GlobalKnowledgeBase, table=True):
    """
    Concrete implementation of the GlobalKnowledgeBase template.
    Tenant-specific implementations should inherit from GlobalKnowledgeBase.
    """
    __tablename__ = "longterm_memory_global_knowledge"