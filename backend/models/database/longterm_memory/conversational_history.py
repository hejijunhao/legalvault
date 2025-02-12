# models/database/longterm_memory/conversational_history.py

from datetime import datetime
from typing import Optional
from uuid import uuid4
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import Column, Text, TIMESTAMP, ForeignKey
from sqlmodel import SQLModel, Field, Index
from abc import ABC


class ConversationalHistoryBase(SQLModel, ABC):
    """
    Abstract base class representing a VP's conversational history in the LegalVault system.
    Serves as a template for tenant-specific conversational history implementations.
    Contains records of conversations and their context for long-term memory.
    """
    __abstract__ = True

    __table_args__ = (
        Index("ix_conversational_history_vp_id", "vp_id"),
        Index("ix_conversational_history_last_updated", "last_updated"),
        {'schema': 'public'}
    )

    model_config = {
        "arbitrary_types_allowed": True,
        "json_schema_extra": {
            "examples": [
                {
                    "summary": "Discussion about contract terms with Client A",
                    "context": "Contract negotiation for Project X",
                    "interaction_count": 5
                }
            ]
        }
    }

    # Core Properties
    id: UUID = Field(
        default_factory=uuid4,
        primary_key=True,
        description="Unique identifier for the conversation history record"
    )
    vp_id: UUID = Field(
        sa_column=Column(
            UUID(as_uuid=True),
            ForeignKey("vault.virtual_paralegals.id"),
            nullable=False
        ),
        description="Foreign key to the Virtual Paralegal"
    )
    
    # Conversation Details
    summary: str = Field(
        sa_column=Column(Text),
        description="Prompt containing conversation summary"
    )
    context: str = Field(
        sa_column=Column(Text),
        description="Prompt containing additional context"
    )
    interaction_count: int = Field(
        default=0,
        description="Number of interactions in this conversation"
    )

    # Metadata
    last_updated: datetime = Field(
        sa_column=Column(TIMESTAMP(timezone=True)),
        default_factory=datetime.utcnow,
        description="Timestamp of last update"
    )

    def __repr__(self) -> str:
        """String representation of the Conversational History"""
        return f"ConversationalHistory(id={self.id}, vp_id={self.vp_id}, interaction_count={self.interaction_count})"


class ConversationalHistory(ConversationalHistoryBase):
    """
    Concrete implementation of the ConversationalHistoryBase template.
    Tenant-specific implementations should inherit from ConversationalHistoryBase.
    """
    __tablename__ = "longterm_memory_conversational_history"