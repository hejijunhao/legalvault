# models/domain/longterm_memory/self_identity.py

from pydantic import BaseModel
from typing import Optional
from models.database.longterm_memory.self_identity import SelfIdentity


class SelfIdentityDomain(BaseModel):
    """Domain model for VP self-identity."""
    id: Optional[int]
    vp_id: int
    prompt: str

    @classmethod
    def from_db(cls, db_model: SelfIdentity) -> "SelfIdentityDomain":
        return cls(
            id=db_model.id,
            vp_id=db_model.vp_id,
            prompt=db_model.prompt
        )

    def to_dict(self) -> dict:
        """Convert domain model to dictionary."""
        return {
            "id": self.id,
            "vp_id": self.vp_id,
            "prompt": self.prompt
        }