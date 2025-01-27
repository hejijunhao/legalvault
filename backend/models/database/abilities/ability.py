#backend/models/database/ability.py
from sqlmodel import SQLModel, Field, Column, JSON, Relationship
from typing import Dict, Optional, List, TYPE_CHECKING, Any
from datetime import datetime

if TYPE_CHECKING:
    from models.database import TaskManagementAbility, ReceiveEmailAbility


class Ability(SQLModel, table=True):
    __tablename__ = "abilities"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    description: str
    structure: Dict = Field(default={}, sa_column=Column(JSON))
    requirements: Dict = Field(default={}, sa_column=Column(JSON))
    meta_info: Dict = Field(default={}, sa_column=Column(JSON))
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Use full module path for the relationships
    task_management_abilities: List["TaskManagementAbility"] = Relationship(
        sa_relationship_kwargs={
            "lazy": "selectin",
            "primaryjoin": "Ability.id == TaskManagementAbility.ability_id"
        },
        back_populates="ability"
    )

    receive_email_abilities: List["ReceiveEmailAbility"] = Relationship(
        sa_relationship_kwargs={
            "lazy": "selectin",
            "primaryjoin": "Ability.id == ReceiveEmailAbility.ability_id"
        },
        back_populates="ability"
    )

    class Config:
        arbitrary_types_allowed = True