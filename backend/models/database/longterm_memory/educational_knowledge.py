# models/database/longterm_memory/educational_knowledge.py

import sqlmodel
from sqlmodel import SQLModel, Field
from sqlalchemy import Column, Text, Enum as SQLEnum
from typing import Optional
import uuid
from enum import Enum

class EducationType(str, Enum):
    """Enumeration of possible education types."""
    LEGAL_HANDBOOK = "legal_handbook"
    PROFESSIONAL_GUIDELINES = "professional_guidelines"
    BEST_PRACTICES = "best_practices"
    PROCEDURES = "procedures"
    DOMAIN_PRINCIPLES = "domain_principles"
    SPECIFIC_DETAILS = "specific_details"

class EducationalKnowledge(SQLModel, table=True):
    """Database model for VP educational knowledge system prompts."""
    __tablename__ = "longterm_memory_educational_knowledge"

    id: Optional[int] = Field(default=None, primary_key=True)
    vp_id: uuid.UUID = Field(foreign_key="virtual_paralegals.id")
    education_type: EducationType = Field(sa_column=Column(SQLEnum(EducationType)))
    prompt: str = Field(sa_column=Column(Text))

    class Config:
        arbitrary_types_allowed = True

    __table_args__ = (
        sqlmodel.UniqueConstraint('vp_id', 'education_type'),
    )