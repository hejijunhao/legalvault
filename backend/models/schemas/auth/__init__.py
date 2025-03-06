# models/schemas/auth/__init__.py

from pydantic import BaseModel
from typing import Optional
from uuid import UUID
from datetime import datetime

class TokenData(BaseModel):
    user_id: UUID
    exp: Optional[datetime] = None

class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    user_id: UUID
    expires_in: int  # seconds
