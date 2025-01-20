# models/schemas/common/responses.py

from typing import Dict, Optional
from pydantic import BaseModel

class APIResponse(BaseModel):
    """Generic API response model"""
    success: bool
    data: Optional[Dict] = None
    error: Optional[str] = None