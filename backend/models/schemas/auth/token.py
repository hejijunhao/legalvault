# models/schemas/auth/token.py

from pydantic import BaseModel
from typing import Optional
from uuid import UUID
from datetime import datetime

class TokenData(BaseModel):
    user_id: UUID
    email: Optional[str] = None
    exp: Optional[datetime] = None

class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    user_id: UUID
    expires_in: int  # seconds