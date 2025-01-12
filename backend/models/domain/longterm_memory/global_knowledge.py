# models/domain/longterm_memory/global_knowledge.py

from pydantic import BaseModel
from typing import Optional
import uuid
from models.database.longterm_memory.global_knowledge import GlobalKnowledge, KnowledgeType

class GlobalKnowledgeDomain(BaseModel):
    """Domain model for VP global knowledge."""
    id: Optional[int]
    vp_id: uuid.UUID
    knowledge_type: KnowledgeType
    prompt: str

    @classmethod
    def from_db(cls, db_model: GlobalKnowledge) -> "GlobalKnowledgeDomain":
        return cls(
            id=db_model.id,
            vp_id=db_model.vp_id,
            knowledge_type=db_model.knowledge_type,
            prompt=db_model.prompt
        )

    def to_dict(self) -> dict:
        """Convert domain model to dictionary."""
        return {
            "id": self.id,
            "vp_id": self.vp_id,
            "knowledge_type": self.knowledge_type,
            "prompt": self.prompt
        }