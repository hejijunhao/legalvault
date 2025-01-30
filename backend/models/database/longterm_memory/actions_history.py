# models/database/longterm_memory/actions_history.py

from sqlmodel import SQLModel, Field
from sqlalchemy import Column, Text, TIMESTAMP
from typing import Optional
from uuid import UUID
from datetime import datetime

class ActionsHistory(SQLModel, table=True):
    """Database model for VP actions history and memory."""
    __tablename__ = "longterm_memory_actions_history"
    __table_args__={'schema': 'public'}

    id: Optional[int] = Field(default=None, primary_key=True)
    vp_id: UUID = Field(foreign_key="vault.virtual_paralegals.id")  # FK to VP table
    summary: str = Field(sa_column=Column(Text))  # Prompt containing actions summary
    context: str = Field(sa_column=Column(Text))  # Prompt containing additional context
    last_updated: datetime = Field(
        sa_column=Column(TIMESTAMP(timezone=True)),
        default_factory=datetime.utcnow
    )
    action_count: int = Field(default=0)  # Number of actions performed