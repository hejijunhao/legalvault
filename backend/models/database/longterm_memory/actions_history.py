# models/database/longterm_memory/actions_history.py

from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4
from sqlalchemy.dialects.postgresql import UUID as SQLAlchemyUUID
from sqlalchemy import Column, Text, TIMESTAMP
from sqlmodel import SQLModel, Field, Index, ForeignKey
from abc import ABC


class ActionsHistoryBase(SQLModel, ABC):
    """
    Abstract base class representing a VP's actions history in the LegalVault system.
    Serves as a template for tenant-specific actions history implementations.
    Contains records of actions taken and their context for long-term memory.
    """
    __abstract__ = True

    __table_args__ = (
        Index("ix_actions_history_vp_id", "vp_id"),
        Index("ix_actions_history_last_updated", "last_updated")
    )

    model_config = {
        "arbitrary_types_allowed": True,
        "json_schema_extra": {
            "examples": [
                {
                    "summary": "Reviewed client contract and extracted key dates",
                    "context": "Contract review for Project X",
                    "action_count": 2
                }
            ]
        }
    }

    # Core Properties
    id: UUID = Field(
        default_factory=uuid4,
        primary_key=True,
        sa_type=SQLAlchemyUUID,
        description="Unique identifier for the actions history record"
    )
    vp_id: UUID = Field(
        sa_column=Column(
            SQLAlchemyUUID,
            ForeignKey("vault.virtual_paralegals.id"),
            nullable=False
        )
    )
    
    # Action Details
    summary: str = Field(
        sa_column=Column(Text),
        description="Prompt containing actions summary"
    )
    context: str = Field(
        sa_column=Column(Text),
        description="Prompt containing additional context"
    )
    action_count: int = Field(
        default=0,
        description="Number of actions performed"
    )

    # Metadata
    last_updated: datetime = Field(
        sa_column=Column(TIMESTAMP(timezone=True)),
        default_factory=datetime.utcnow,
        description="Timestamp of last update"
    )

    def __repr__(self) -> str:
        """String representation of the Actions History"""
        return f"ActionsHistory(id={self.id}, vp_id={self.vp_id}, action_count={self.action_count})"


class ActionsHistoryBlueprint(ActionsHistoryBase, table=True):
    """
    Concrete implementation of ActionsHistoryBase for the public schema blueprint.
    Serves as a reference for tenant-specific implementations.
    """
    __tablename__ = "longterm_memory_actions_history_blueprint"
    __table_args__ = (
        Index("ix_actions_history_vp_id", "vp_id"),
        Index("ix_actions_history_last_updated", "last_updated"),
        {'schema': 'public'}
    )


class ActionsHistory(ActionsHistoryBase):
    """
    Concrete implementation of ActionsHistoryBase for enterprise schemas.
    """
    __tablename__ = "longterm_memory_actions_history"