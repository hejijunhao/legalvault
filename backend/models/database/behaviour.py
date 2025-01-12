# /backend/models/database/behaviour.py

from datetime import datetime
from typing import Optional
from sqlmodel import Field, SQLModel
from uuid import UUID, uuid4
from enum import Enum
from sqlalchemy import Column, ForeignKey


class BehaviourStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    DEPRECATED = "deprecated"


class Behaviour(SQLModel, table=True):
    __tablename__ = "behaviours"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    name: str = Field(unique=True, index=True)
    description: str
    system_prompt: str
    status: BehaviourStatus = Field(default=BehaviourStatus.ACTIVE)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class AbilityBehaviour(SQLModel, table=True):
    __tablename__ = "ability_behaviours"

    ability_id: UUID = Field(default=None, sa_column=Column(
        ForeignKey("abilities.id", ondelete="CASCADE"),
        primary_key=True,
        nullable=False
    ))
    behaviour_id: UUID = Field(default=None, sa_column=Column(
        ForeignKey("behaviours.id", ondelete="CASCADE"),
        primary_key=True,
        nullable=False
    ))
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class BehaviourVP(SQLModel, table=True):
    __tablename__ = "behaviour_vps"

    vp_id: UUID = Field(default=None, sa_column=Column(
        ForeignKey("virtual_paralegals.id", ondelete="CASCADE"),
        primary_key=True,
        nullable=False
    ))
    behaviour_id: UUID = Field(default=None, sa_column=Column(
        ForeignKey("behaviours.id", ondelete="CASCADE"),
        primary_key=True,
        nullable=False
    ))
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
