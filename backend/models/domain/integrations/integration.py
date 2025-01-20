# models/domain/integrations/integration.py

from typing import Dict, List, Optional
from uuid import UUID
from models.database.integrations.integration import Integration as DBIntegration, AuthType
from models.database.integrations.credentials import Credentials as DBCredentials
from models.database.integrations.integration_ability import IntegrationAbility as DBIntegrationAbility

class Integration:
    """Domain model for Integration, containing business logic for integration management."""
    
    def __init__(self, db_integration: DBIntegration):
        self.db_integration = db_integration
        self._credentials: List[DBCredentials] = []
        self._abilities: List[DBIntegrationAbility] = []

    @property
    def integration_id(self) -> UUID:
        return self.db_integration.integration_id

    @property
    def name(self) -> str:
        return self.db_integration.name

    @property
    def description(self) -> str:
        return self.db_integration.description

    @property
    def auth_type(self) -> AuthType:
        return self.db_integration.auth_type

    @property
    def config(self) -> Dict:
        return self.db_integration.config

    @property
    def is_active(self) -> bool:
        return self.db_integration.is_active

    @property
    def api_version(self) -> str:
        return self.db_integration.api_version

    @property
    def required_scopes(self) -> List[str]:
        return self.db_integration.required_scopes

    def requires_oauth(self) -> bool:
        """Check if integration requires OAuth authentication."""
        return self.auth_type == AuthType.OAUTH2

    def requires_api_key(self) -> bool:
        """Check if integration requires API key authentication."""
        return self.auth_type == AuthType.API_KEY

    def get_auth_config(self) -> Dict:
        """Get authentication-specific configuration."""
        if self.requires_oauth():
            return {
                "client_id": self.config.get("client_id"),
                "auth_url": self.config.get("auth_url"),
                "token_url": self.config.get("token_url"),
                "scopes": self.config.get("scopes", [])
            }
        return {}

    def validate_scopes(self, provided_scopes: List[str]) -> bool:
        """Validate that all required scopes are provided."""
        return all(scope in provided_scopes for scope in self.required_scopes)

    def get_rate_limit(self) -> Optional[int]:
        """Get rate limit if configured."""
        return self.db_integration.rate_limit

    def has_webhook(self) -> bool:
        """Check if integration supports webhooks."""
        return bool(self.db_integration.webhook_url)

    def get_webhook_url(self) -> Optional[str]:
        """Get webhook URL if configured."""
        return self.db_integration.webhook_url

    def set_credentials(self, credentials: List[DBCredentials]) -> None:
        """Set associated credentials."""
        self._credentials = credentials

    def set_abilities(self, abilities: List[DBIntegrationAbility]) -> None:
        """Set associated abilities."""
        self._abilities = abilities

    def get_active_credentials(self) -> List[DBCredentials]:
        """Get list of active credentials for this integration."""
        return [cred for cred in self._credentials if cred.is_active]

    def get_required_abilities(self) -> List[DBIntegrationAbility]:
        """Get list of abilities that require this integration."""
        return [ability for ability in self._abilities if ability.is_required]