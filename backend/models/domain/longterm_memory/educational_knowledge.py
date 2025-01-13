# models/domain/longterm_memory/educational_knowledge.py

from pydantic import BaseModel
from typing import Optional
import uuid
from models.database.longterm_memory.educational_knowledge import EducationalKnowledge, EducationType

class EducationalKnowledgeDomain(BaseModel):
    """Domain model for VP educational knowledge."""
    id: Optional[int]
    vp_id: uuid.UUID
    education_type: EducationType
    prompt: str

    @classmethod
    def from_db(cls, db_model: EducationalKnowledge) -> "EducationalKnowledgeDomain":
        return cls(
            id=db_model.id,
            vp_id=db_model.vp_id,
            education_type=db_model.education_type,
            prompt=db_model.prompt
        )

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "vp_id": self.vp_id,
            "education_type": self.education_type,
            "prompt": self.prompt
        }