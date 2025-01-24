# models/domain/library/collections.py

from datetime import datetime
from typing import Dict, Any, Optional
from uuid import UUID

from pydantic import BaseModel, Field

from models.database.library.collections import Collection as DBCollection

class Collection(BaseModel):
    id: UUID
    name: str
    description: Optional[str] = None
    owner_id: UUID
    is_default: bool = False
    collection_type: str
    created_at: datetime
    updated_at: datetime
    collection_metadata: Dict[str, Any] = Field(default_factory=dict)

    def update(self, **kwargs: Any) -> None:
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
        self.updated_at = datetime.utcnow()

    def add_collection_metadata(self, key: str, value: Any) -> None:
        self.collection_metadata[key] = value
        self.updated_at = datetime.utcnow()

    def remove_collection_metadata(self, key: str) -> None:
        if key in self.collection_metadata:
            del self.collection_metadata[key]
            self.updated_at = datetime.utcnow()

    def is_owned_by(self, user_id: UUID) -> bool:
        return self.owner_id == user_id

    def can_be_deleted(self) -> bool:
        return not self.is_default

    @property
    def is_clausebank(self) -> bool:
        return self.collection_type.lower() == "clausebank"

    @property
    def is_custom(self) -> bool:
        return self.collection_type.lower() == "custom"

    def get_collection_metadata(self, key: str, default: Any = None) -> Any:
        return self.collection_metadata.get(key, default)

    @classmethod
    def from_orm(cls, db_collection: 'DBCollection') -> 'Collection':
        return cls(**db_collection.__dict__)

    class Config:
        arbitrary_types_allowed = True