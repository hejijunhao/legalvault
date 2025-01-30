# models/database/longterm_memory/conversational_history.py

from sqlmodel import SQLModel, Field
from sqlalchemy import Column, Text, TIMESTAMP
from typing import Optional
from uuid import UUID
from datetime import datetime

class ConversationalHistory(SQLModel, table=True):
    """Database model for VP conversational history and memory."""
    __tablename__ = "longterm_memory_conversational_history"
    __table_args__={'schema': 'public'}

    id: Optional[int] = Field(default=None, primary_key=True)
    vp_id: UUID = Field(foreign_key="vault.virtual_paralegals.id")  # FK to VP table
    summary: str = Field(sa_column=Column(Text))  # Prompt containing conversation summary
    context: str = Field(sa_column=Column(Text))  # Prompt containing additional context
    last_updated: datetime = Field(
        sa_column=Column(TIMESTAMP(timezone=True)),
        default_factory=datetime.utcnow
    )
    interaction_count: int = Field(default=0)  # Number of interactions in this conversation