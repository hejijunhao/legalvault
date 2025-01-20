# models/schemas/integrations/oauth.py

from datetime import datetime
from typing import Dict, Optional
from pydantic import BaseModel

class OAuthTokenResponse(BaseModel):
    """Response model for OAuth token operations"""
    credentials: Dict
    expires_at: Optional[datetime] = None
    refresh_token: Optional[str] = None