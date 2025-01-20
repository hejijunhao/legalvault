# services/executors/integrations/integration_executor.py

import json
from typing import Dict, Optional
from datetime import datetime, timedelta
from logging import getLogger
from uuid import UUID

import httpx
from pydantic import ValidationError

from config import settings

from models.domain.integrations.integration import Integration
from .models import OAuthTokenResponse, APIResponse
from models.schemas.integrations.oauth import OAuthTokenResponse
from models.schemas.common.responses import APIResponse

logger = getLogger(__name__)

class IntegrationExecutor:
    """Executor for handling integration operations and OAuth flows"""

    def __init__(self):
        self.client = httpx.AsyncClient(timeout=30.0)

    async def get_oauth_url(self, integration: Integration) -> str:
        """Generate OAuth authorization URL"""
        try:
            if not integration.requires_oauth():
                raise ValueError("Integration does not use OAuth")

            auth_config = integration.get_auth_config()
            if not auth_config:
                raise ValueError("Missing OAuth configuration")

            params = {
                "client_id": auth_config["client_id"],
                "response_type": "code",
                "redirect_uri": f"{self._get_base_url()}/api/oauth/callback/{integration.integration_id}",
                "scope": " ".join(auth_config["scopes"]),
                "state": self._generate_state_token()
            }

            return f"{auth_config['auth_url']}?{self._build_query_string(params)}"
        except Exception as e:
            logger.error(f"Error generating OAuth URL: {str(e)}")
            raise

    async def exchange_oauth_code(
        self,
        integration: Integration,
        code: str
    ) -> OAuthTokenResponse:
        """Exchange OAuth code for access token"""
        try:
            auth_config = integration.get_auth_config()
            if not auth_config:
                raise ValueError("Missing OAuth configuration")

            data = {
                "client_id": auth_config["client_id"],
                "client_secret": auth_config["client_secret"],
                "grant_type": "authorization_code",
                "code": code,
                "redirect_uri": f"{self._get_base_url()}/api/oauth/callback/{integration.integration_id}"
            }

            async with self.client as client:
                response = await client.post(
                    auth_config["token_url"],
                    data=data
                )
                response.raise_for_status()
                token_data = response.json()

            return self._process_token_response(token_data)

        except httpx.HTTPError as e:
            logger.error(f"HTTP error during OAuth code exchange: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Error exchanging OAuth code: {str(e)}")
            raise

    async def refresh_oauth_token(
        self,
        integration: Integration,
        refresh_token: str
    ) -> OAuthTokenResponse:
        """Refresh OAuth access token"""
        try:
            auth_config = integration.get_auth_config()
            if not auth_config:
                raise ValueError("Missing OAuth configuration")

            data = {
                "client_id": auth_config["client_id"],
                "client_secret": auth_config["client_secret"],
                "grant_type": "refresh_token",
                "refresh_token": refresh_token
            }

            async with self.client as client:
                response = await client.post(
                    auth_config["token_url"],
                    data=data
                )
                response.raise_for_status()
                token_data = response.json()

            return self._process_token_response(token_data)

        except httpx.HTTPError as e:
            logger.error(f"HTTP error during token refresh: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Error refreshing OAuth token: {str(e)}")
            raise

    async def make_api_call(
        self,
        integration: Integration,
        method: str,
        endpoint: str,
        credentials: Dict,
        params: Optional[Dict] = None,
        data: Optional[Dict] = None,
        headers: Optional[Dict] = None
    ) -> APIResponse:
        """Make an API call to the integration"""
        try:
            full_url = f"{integration.config['api_base_url']}{endpoint}"
            headers = headers or {}
            headers.update({
                "Authorization": f"Bearer {credentials.get('access_token')}",
                "Content-Type": "application/json"
            })

            async with self.client as client:
                response = await client.request(
                    method=method,
                    url=full_url,
                    params=params,
                    json=data,
                    headers=headers
                )
                response.raise_for_status()
                return APIResponse(
                    success=True,
                    data=response.json()
                )

        except httpx.HTTPError as e:
            logger.error(f"HTTP error during API call: {str(e)}")
            return APIResponse(
                success=False,
                error=f"API call failed: {str(e)}"
            )
        except Exception as e:
            logger.error(f"Error making API call: {str(e)}")
            return APIResponse(
                success=False,
                error=f"Internal error: {str(e)}"
            )

    def _process_token_response(self, token_data: Dict) -> OAuthTokenResponse:
        """Process OAuth token response"""
        expires_in = token_data.get("expires_in")
        expires_at = None
        if expires_in:
            expires_at = datetime.utcnow() + timedelta(seconds=int(expires_in))

        return OAuthTokenResponse(
            credentials={
                "access_token": token_data["access_token"],
                "token_type": token_data.get("token_type", "Bearer")
            },
            expires_at=expires_at,
            refresh_token=token_data.get("refresh_token")
        )

    def _get_base_url(self) -> str:
        return settings.BASE_URL

    def _generate_state_token(self) -> str:
        """Generate state token for OAuth security"""
        # TODO: Implement secure state token generation
        return "state_token"

    def _build_query_string(self, params: Dict) -> str:
        """Build URL query string from parameters"""
        return "&".join([f"{k}={v}" for k, v in params.items()])

    async def __aenter__(self):
        """Async context manager entry"""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self.client.aclose()