# backend/models/database/ability_taskmanagement.py
from datetime import datetime
from typing import Optional
from sqlmodel import SQLModel, Field
from sqlalchemy.dialects.postgresql import JSONB

class TaskManagementAbility(SQLModel, table=True):
    __tablename__ = "task_management_abilities"

    id: int = Field(default=None, primary_key=True)
    techtree_id: int = Field(foreign_key="tech_trees.id", index=True)
    operation_name: str = Field(max_length=255)
    description: str
    enabled: bool = Field(default=True)
    input_schema: dict = Field(sa_column=JSONB)
    output_schema: dict = Field(sa_column=JSONB)
    workflow_steps: dict = Field(sa_column=JSONB)
    constraints: dict = Field(sa_column=JSONB)
    permissions: dict = Field(sa_column=JSONB)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow, sa_column_kwargs={"onupdate": datetime.utcnow})

    class Config:
        arbitrary_types_allowed = True
