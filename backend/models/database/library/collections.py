# models/database/library/collections.py

from datetime import datetime
from typing import Dict, Any, Optional
from uuid import UUID, uuid4

from sqlmodel import Field, SQLModel
from sqlalchemy import Column
from sqlalchemy.dialects.postgresql import JSONB

class Collection(SQLModel, table=True):
    __tablename__ = "collections"
    __table_args__={'schema': 'public'}

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    name: str = Field(index=True)
    description: Optional[str] = Field(default=None)
    owner_id: UUID = Field(foreign_key="vault.users.id", index=True)
    is_default: bool = Field(default=False)
    collection_type: str = Field(index=True)  # e.g., "Clausebank", "Custom", etc.
    collection_metadata: Dict[str, Any] = Field(sa_column=Column(JSONB))
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        nullable=False,
        sa_column_kwargs={"server_default": "now()"}
    )
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        nullable=False,
        sa_column_kwargs={"server_default": "now()", "onupdate": "now()"}
    )

    class Config:
        arbitrary_types_allowed = True
        json_schema_extra = {
            "example": {
                "name": "Sample Collection",
                "description": "A sample collection for demonstration",
                "collection_type": "Custom",
                "collection_metadata": {"key": "value"}
            }
        }