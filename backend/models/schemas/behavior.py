from pydantic import BaseModel
from typing import Optional, Any, Dict, List
from uuid import UUID
from datetime import datetime

class BehaviorCreate(BaseModel):
    paralegal_id: UUID
    category: str  # e.g., "communication", "task_management"
    setting_key: str  # e.g., "formality_level", "summary_style"
    value: Any
    is_customizable: bool = True

class BehaviorUpdate(BaseModel):
    category: Optional[str] = None
    setting_key: Optional[str] = None
    value: Optional[Any] = None
    is_customizable: Optional[bool] = None

class BehaviorResponse(BaseModel):
    id: UUID
    paralegal_id: UUID
    category: str
    setting_key: str
    value: Any
    is_customizable: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True