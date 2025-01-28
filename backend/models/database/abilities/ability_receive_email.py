#models/database/ability_receive_email.py

from datetime import datetime
from typing import Optional, Dict
from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import Column, Index
from sqlalchemy.dialects.postgresql import JSONB

class ReceiveEmailAbility(SQLModel, table=True):
    __tablename__ = "ability_receive_email"
    __table_args__ = (
        {'schema': 'vault'},
        Index("ix_ability_receive_email_operation_name", "operation_name")
    )

    id: int = Field(default=None, primary_key=True)
    ability_id: int = Field(foreign_key="vault.abilities.id", index=True)
    operation_name: str = Field(max_length=255)
    description: str
    enabled: bool = Field(default=True)
    input_schema: Dict = Field(sa_column=Column(JSONB))
    output_schema: Dict = Field(sa_column=Column(JSONB))
    workflow_steps: Dict = Field(sa_column=Column(JSONB))
    constraints: Dict = Field(sa_column=Column(JSONB))
    permissions: Dict = Field(sa_column=Column(JSONB))
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column_kwargs={"onupdate": datetime.utcnow}
    )

    # Define relationship back to Ability
    ability: Optional["Ability"] = Relationship(
        back_populates="receive_email_abilities",
        sa_relationship_kwargs={"lazy": "selectin"}
    )

    class Config:
        arbitrary_types_allowed = True