#models/schemas/ability_receive_email.py
from datetime import datetime
from typing import Dict, Optional
from pydantic import BaseModel, Field

class ReceiveEmailAbilityBase(BaseModel):
    operation_name: str = Field(..., description="Name of the operation")
    description: str = Field(..., description="Description of what this operation does")
    enabled: bool = Field(default=True)
    input_schema: Dict
    output_schema: Dict
    workflow_steps: Dict
    constraints: Dict
    permissions: Dict

class ReceiveEmailAbilityCreate(ReceiveEmailAbilityBase):
    ability_id: int = Field(..., description="Foreign key to abilities")

class ReceiveEmailAbilityUpdate(BaseModel):
    operation_name: Optional[str] = None
    description: Optional[str] = None
    enabled: Optional[bool] = None
    input_schema: Optional[Dict] = None
    output_schema: Optional[Dict] = None
    workflow_steps: Optional[Dict] = None
    constraints: Optional[Dict] = None
    permissions: Optional[Dict] = None

class ReceiveEmailAbilityInDB(ReceiveEmailAbilityBase):
    id: int
    ability_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True
