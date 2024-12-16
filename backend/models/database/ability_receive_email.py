from datetime import datetime
from typing import Optional, Dict
from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import Column, Index
from sqlalchemy.dialects.postgresql import JSONB

class ReceiveEmailAbility(SQLModel, table=True):
    __tablename__ = "receive_email_abilities"
    __table_args__ = (Index("ix_receive_email_abilities_operation_name", "operation_name"),)

    id: int = Field(default=None, primary_key=True)
    ability_id: int = Field(foreign_key="abilities.id", index=True)
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

    # Add relationship to parent Ability
    ability: Optional["Ability"] = Relationship(back_populates="receive_email_abilities")

    class Config:
        arbitrary_types_allowed = True