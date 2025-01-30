# /backend/models/domain/behaviour.py

from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from uuid import UUID

@dataclass
class BehaviourDomain:
    id: UUID
    name: str
    description: str
    system_prompt: str
    status: str
    created_at: datetime
    updated_at: datetime

    def to_dict(self):
        return {
            "id": str(self.id),
            "name": self.name,
            "description": self.description,
            "system_prompt": self.system_prompt,
            "status": self.status,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }

    @classmethod
    def from_db(cls, behaviour_db):
        return cls(
            id=behaviour_db.id,
            name=behaviour_db.name,
            description=behaviour_db.description,
            system_prompt=behaviour_db.system_prompt,
            status=behaviour_db.status,
            created_at=behaviour_db.created_at,
            updated_at=behaviour_db.updated_at
        )
