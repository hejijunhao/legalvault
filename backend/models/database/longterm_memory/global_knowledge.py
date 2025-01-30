# models/database/longterm_memory/global_knowledge.py

import sqlmodel
from sqlmodel import SQLModel, Field
from sqlalchemy import Column, Text, Enum as SQLEnum
from typing import Optional
import uuid
from enum import Enum

class KnowledgeType(str, Enum):
    """Enumeration of possible knowledge types."""
    SYSTEM_STATS = "system_stats"
    USER_SPECIALIZATIONS = "user_specializations"
    ORGANIZATIONAL_POLICIES = "organizational_policies"
    PROJECT_OVERVIEW = "project_overview"
    INTEGRATION_ACCESS = "integration_access"

class GlobalKnowledge(SQLModel, table=True):
    """Database model for VP global knowledge system prompts."""
    __tablename__ = "longterm_memory_global_knowledge"

    id: Optional[int] = Field(default=None, primary_key=True)
    vp_id: uuid.UUID = Field(foreign_key="vault.virtual_paralegals.id")
    knowledge_type: KnowledgeType = Field(sa_column=Column(SQLEnum(KnowledgeType)))
    prompt: str = Field(sa_column=Column(Text))

    class Config:
        arbitrary_types_allowed = True

    __table_args__ = (
        # Ensure each VP has only one prompt per knowledge type
        sqlmodel.UniqueConstraint('vp_id', 'knowledge_type'),
        {'schema': 'public'}
    )