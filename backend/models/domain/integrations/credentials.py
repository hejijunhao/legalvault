# models/domain/integrations/credentials.py

from datetime import datetime, timedelta
from typing import Dict, Optional
from uuid import UUID
from models.database.integrations.credentials import Credentials as DBCredentials
from models.database.integrations.integration import Integration as DBIntegration

class Credentials:
    """Domain model for Credentials, containing business logic for credential management."""

    def __init__(self, db_credentials: DBCredentials):
        self.db_credentials = db_credentials

    @property
    def credential_id(self) -> UUID:
        return self.db_credentials.credential_id

    @property
    def user_id(self) -> UUID:
        return self.db_credentials.user_id

    @property
    def integration_id(self) -> UUID:
        return self.db_credentials.integration_id

    @property
    def is_active(self) -> bool:
        return self.db_credentials.is_active

    @property
    def credentials(self) -> Dict:
        return self.db_credentials.credentials

    def is_expired(self) -> bool:
        """Check if credentials have expired."""
        if not self.db_credentials.expires_at:
            return False
        return datetime.utcnow() > self.db_credentials.expires_at

    def needs_refresh(self, refresh_threshold_minutes: int = 5) -> bool:
        """Check if credentials need refreshing soon."""
        if not self.db_credentials.expires_at:
            return False
        threshold = datetime.utcnow() + timedelta(minutes=refresh_threshold_minutes)
        return threshold > self.db_credentials.expires_at

    def has_refresh_token(self) -> bool:
        """Check if refresh token is available."""
        return bool(self.db_credentials.refresh_token)

    def get_access_token(self) -> Optional[str]:
        """Get the access token from credentials."""
        return self.credentials.get("access_token")

    def get_token_type(self) -> str:
        """Get the token type (e.g., 'Bearer')."""
        return self.credentials.get("token_type", "Bearer")

    def get_authorization_header(self) -> Optional[Dict[str, str]]:
        """Get formatted authorization header."""
        access_token = self.get_access_token()
        if not access_token:
            return None
        return {"Authorization": f"{self.get_token_type()} {access_token}"}

    def update_last_used(self) -> None:
        """Update the last used timestamp."""
        self.db_credentials.last_used_at = datetime.utcnow()

    def deactivate(self) -> None:
        """Deactivate these credentials."""
        self.db_credentials.is_active = False
        self.db_credentials.modified_at = datetime.utcnow()

    def update_credentials(self, new_credentials: Dict) -> None:
        """Update stored credentials."""
        self.db_credentials.credentials = new_credentials
        self.db_credentials.modified_at = datetime.utcnow()

    def update_refresh_token(self, refresh_token: str) -> None:
        """Update refresh token."""
        self.db_credentials.refresh_token = refresh_token
        self.db_credentials.modified_at = datetime.utcnow()

    def set_expiry(self, expires_at: datetime) -> None:
        """Set credential expiry time."""
        self.db_credentials.expires_at = expires_at
        self.db_credentials.modified_at = datetime.utcnow()