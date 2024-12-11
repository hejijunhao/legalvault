from sqlmodel import SQLModel, Field
from typing import Optional, Dict, List
from uuid import UUID, uuid4
from datetime import datetime
from sqlalchemy import JSON, Column

class VirtualParalegal(SQLModel, table=True):
    __tablename__ = "virtual_paralegals"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    name: str = Field(index=True)
    email: str = Field(unique=True)
    phone: Optional[str] = None
    whatsapp: Optional[str] = None
    owner_id: UUID = Field(foreign_key="users.id")
    # Change these two lines:
    abilities: List = Field(sa_column=Column(JSON), default=[])
    behaviors: Dict = Field(sa_column=Column(JSON), default={})
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    tech_tree_progress: Dict = Field(
        default={
            "unlocked_nodes": {},  # node_id -> unlock_timestamp
            "progress": {},  # node_id -> completion_percentage
            "metadata": {}  # Additional tracking data
        },
        sa_column=Column(JSON)
    )