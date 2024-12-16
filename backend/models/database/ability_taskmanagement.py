# backend/models/database/ability_taskmanagement.py
from datetime import datetime
from typing import Optional, Dict, List
from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import Column
from sqlalchemy.dialects.postgresql import JSONB

class TaskManagementAbility(SQLModel, table=True):
    __tablename__ = "task_management_abilities"

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
    updated_at: datetime = Field(default_factory=datetime.utcnow, sa_column_kwargs={"onupdate": datetime.utcnow})

    # Define relationship back to Ability
    ability: Optional["Ability"] = Relationship(
        back_populates="task_management_abilities",
        sa_relationship_kwargs={"lazy": "selectin"}
    )

    class Config:
        arbitrary_types_allowed = True