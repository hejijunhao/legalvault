from sqlmodel import SQLModel, Field, Column, JSON
from typing import Dict, Optional
from datetime import datetime


class TechTree(SQLModel, table=True):
    __tablename__ = "tech_trees"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    description: str
    structure: Dict = Field(default={}, sa_column=Column(JSON))  # Full tree structure
    requirements: Dict = Field(default={}, sa_column=Column(JSON))  # Unlock requirements
    meta_info: Dict = Field(default={}, sa_column=Column(JSON))  # Changed from metadata to meta_info
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)