# models/domain/longterm_memory/conversational_history.py

from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from uuid import UUID
from models.database.longterm_memory.conversational_history import ConversationalHistory


class ConversationalHistoryDomain(BaseModel):
    """Domain model for VP conversational history."""
    id: Optional[int]
    vp_id: UUID
    summary: str
    context: str
    last_updated: datetime
    interaction_count: int

    @classmethod
    def from_db(cls, db_model: ConversationalHistory) -> "ConversationalHistoryDomain":
        return cls(
            id=db_model.id,
            vp_id=db_model.vp_id,
            summary=db_model.summary,
            context=db_model.context,
            last_updated=db_model.last_updated,
            interaction_count=db_model.interaction_count
        )

    def to_dict(self) -> dict:
        """Convert domain model to dictionary."""
        return {
            "id": self.id,
            "vp_id": self.vp_id,
            "summary": self.summary,
            "context": self.context,
            "last_updated": self.last_updated.isoformat(),
            "interaction_count": self.interaction_count
        }