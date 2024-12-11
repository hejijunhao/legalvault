# backend/models/schemas/ability_taskmanagement.py
from datetime import datetime
from typing import Dict, Optional
from pydantic import BaseModel, Field

class TaskManagementAbilityBase(BaseModel):
    operation_name: str = Field(..., description="Name of operation (e.g., 'find_task')")
    description: str = Field(..., description="Human-readable description of what operation does")
    enabled: bool = Field(default=True, description="Whether operation is currently available")
    input_schema: Dict = Field(..., description="Expected input format and requirements")
    output_schema: Dict = Field(..., description="Expected output format and structure")
    workflow_steps: Dict = Field(..., description="Ordered list of steps the operation follows")
    constraints: Dict = Field(..., description="Operation limitations and requirements")
    permissions: Dict = Field(..., description="Required permissions/conditions")

class TaskManagementAbilityCreate(TaskManagementAbilityBase):
    techtree_id: int = Field(..., description="Foreign key to tech_trees")

class TaskManagementAbilityUpdate(TaskManagementAbilityBase):
    operation_name: Optional[str] = None
    description: Optional[str] = None
    enabled: Optional[bool] = None
    input_schema: Optional[Dict] = None
    output_schema: Optional[Dict] = None
    workflow_steps: Optional[Dict] = None
    constraints: Optional[Dict] = None
    permissions: Optional[Dict] = None

class TaskManagementAbilityInDB(TaskManagementAbilityBase):
    id: int
    techtree_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True