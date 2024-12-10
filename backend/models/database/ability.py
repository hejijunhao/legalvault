from sqlmodel import SQLModel, Field
from typing import List, Optional
from uuid import UUID, uuid4
from datetime import datetime


class Ability(SQLModel, table=True):
    __tablename__ = "abilities"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    name: str = Field(index=True)
    description: str
    category: str = Field(index=True)
    prerequisites: List[UUID] = Field(default=[])  # Stored as JSON array
    tier: int = Field(index=True)
    cost: int
    icon_name: Optional[str] = None
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class ParalegalAbility(SQLModel, table=True):
    """Junction table for tracking which VP has which abilities"""
    __tablename__ = "paralegal_abilities"

    paralegal_id: UUID = Field(foreign_key="virtual_paralegals.id", primary_key=True)
    ability_id: UUID = Field(foreign_key="abilities.id", primary_key=True)
    unlocked_at: datetime = Field(default_factory=datetime.utcnow)