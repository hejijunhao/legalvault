# backend/models/database/ability.py
from sqlmodel import SQLModel, Field, Column, JSON, Relationship
from typing import Dict, Optional, List
from datetime import datetime

class Ability(SQLModel, table=True):
    __tablename__ = "abilities"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    description: str
    structure: Dict = Field(default={}, sa_column=Column(JSON))  # Full tree structure
    requirements: Dict = Field(default={}, sa_column=Column(JSON))  # Unlock requirements
    meta_info: Dict = Field(default={}, sa_column=Column(JSON))  # Changed from metadata to meta_info
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Use string literals for both relationship types
    task_management_abilities: List["TaskManagementAbility"] = Relationship(back_populates="ability")
    receive_email_abilities: List["ReceiveEmailAbility"] = Relationship(back_populates="ability")

    class Config:
        arbitrary_types_allowed = True