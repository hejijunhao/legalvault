# models/database/longterm_memory/educational_knowledge.py

from sqlmodel import SQLModel, Field, Index
from datetime import datetime
from sqlalchemy import TIMESTAMP, Column, Text, ForeignKey, Enum as SQLEnum, UniqueConstraint
from typing import Optional
from uuid import uuid4
from sqlalchemy.dialects.postgresql import UUID
from enum import Enum
from abc import ABC


class EducationType(str, Enum):
    """Enumeration of possible education types."""
    LEGAL_HANDBOOK = "legal_handbook"
    PROFESSIONAL_GUIDELINES = "professional_guidelines"
    BEST_PRACTICES = "best_practices"
    PROCEDURES = "procedures"
    DOMAIN_PRINCIPLES = "domain_principles"
    SPECIFIC_DETAILS = "specific_details"


class EducationalKnowledgeBase(SQLModel, ABC):
    """
    Abstract base class representing a VP's educational knowledge in the LegalVault system.
    Serves as a template for tenant-specific educational knowledge implementations.
    Contains structured educational content and professional knowledge.
    """
    __abstract__ = True

    __table_args__ = (
        UniqueConstraint('vp_id', 'knowledge_type'),
        Index("ix_educational_knowledge_vp_id", "vp_id"),
        Index("ix_educational_knowledge_last_updated", "last_updated"),
        {'schema': 'public'}
    )

    model_config = {
        "arbitrary_types_allowed": True,
        "json_schema_extra": {
            "examples": [
                {
                    "education_type": "legal_handbook",
                    "prompt": "Legal handbook content for contract law..."
                }
            ]
        }
    }

    # Core Properties
    id: UUID = Field(
        default_factory=uuid4,
        primary_key=True,
        description="Unique identifier for the educational knowledge record"
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
    education_type: EducationType = Field(
        sa_column=Column(SQLEnum(EducationType)),
        description="Type of educational content"
    )
    prompt: str = Field(
        sa_column=Column(Text),
        description="Educational content prompt"
    )

    # Metadata
    last_updated: datetime = Field(
        sa_column=Column(TIMESTAMP(timezone=True)),
        default_factory=datetime.utcnow,
        description="Timestamp of last update"
    )

    def __repr__(self) -> str:
        """String representation of the Educational Knowledge"""
        return f"EducationalKnowledge(id={self.id}, vp_id={self.vp_id}, type={self.education_type})"


class EducationalKnowledge(EducationalKnowledgeBase):
    """
    Concrete implementation of the EducationalKnowledgeBase template.
    Tenant-specific implementations should inherit from EducationalKnowledgeBase.
    """
    __tablename__ = "longterm_memory_educational_knowledge"