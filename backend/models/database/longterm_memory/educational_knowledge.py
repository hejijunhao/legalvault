# models/database/longterm_memory/educational_knowledge.py

from sqlmodel import SQLModel, Field, Index
from datetime import datetime
from sqlalchemy import TIMESTAMP, Column, Text, ForeignKey, Enum as SQLEnum, UniqueConstraint, String
from typing import Optional
from uuid import UUID, uuid4
from sqlalchemy.dialects.postgresql import UUID as SQLAlchemyUUID
from enum import Enum
from pydantic import validator
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
        UniqueConstraint('vp_id', 'education_type'),
        Index("ix_educational_knowledge_vp_id", "vp_id"),
        Index("ix_educational_knowledge_last_updated", "last_updated")
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
        sa_type=SQLAlchemyUUID,
        description="Unique identifier for the educational knowledge record"
    )
    vp_id: UUID = Field(
        sa_column=Column(
            SQLAlchemyUUID,
            ForeignKey("vault.virtual_paralegals.id"),
            nullable=False
        )
    )

    # Knowledge Content
    education_type: str = Field(
        sa_column=Column(String, nullable=False),
        description="Type of educational content"
    )

    @validator("education_type")
    def validate_education_type(cls, v):
        if isinstance(v, EducationType):
            return v.value
        if v not in [e.value for e in EducationType]:
            raise ValueError(f"Invalid education type: {v}")
        return v

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


class EducationalKnowledgeBlueprint(EducationalKnowledgeBase, table=True):
    """
    Concrete implementation of EducationalKnowledgeBase for the public schema blueprint.
    Serves as a reference for tenant-specific implementations.
    """
    __tablename__ = "longterm_memory_educational_knowledge_blueprint"
    __table_args__ = (
        UniqueConstraint('vp_id', 'education_type'),
        Index("ix_educational_knowledge_vp_id", "vp_id"),
        Index("ix_educational_knowledge_last_updated", "last_updated"),
        {'schema': 'public'}
    )


class EducationalKnowledge(EducationalKnowledgeBase):
    """
    Concrete implementation of EducationalKnowledgeBase for enterprise schemas.
    """
    __tablename__ = "longterm_memory_educational_knowledge"