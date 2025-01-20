# services/workflow/integrations/integration_workflow.py

from typing import Dict, Optional
from uuid import UUID
from logging import getLogger
from sqlmodel import Session

from models.domain.integrations.operations_integration import IntegrationOperations
from models.domain.integrations.operations_credentials import CredentialsOperations
from services.executors.integrations.integration_executor import IntegrationExecutor
from models.schemas.integrations.credentials import CredentialsCreate, CredentialsUpdate

logger = getLogger(__name__)

class IntegrationWorkflow:
    """Orchestrates integration operations and OAuth flows"""

    def __init__(self, session: Session):
        self.session = session
        self.int_ops = IntegrationOperations(session)
        self.cred_ops = CredentialsOperations(session)
        self.executor = IntegrationExecutor()

    async def handle_oauth_flow(
        self,
        integration_id: UUID,
        user_id: UUID,
        code: str
    ) -> Dict:
        """Orchestrate complete OAuth flow"""
        try:
            # 1. Get integration
            integration = await self.int_ops.get(integration_id)
            if not integration:
                raise ValueError("Integration not found")

            # 2. Exchange code for tokens
            token_response = await self.executor.exchange_oauth_code(
                integration=integration,
                code=code
            )

            # 3. Deactivate any existing credentials
            existing_creds = await self.cred_ops.get_for_user_integration(
                user_id=user_id,
                integration_id=integration_id
            )
            if existing_creds:
                await self.cred_ops.deactivate(existing_creds.credential_id)

            # 4. Create new credentials
            cred_data = CredentialsCreate(
                integration_id=integration_id,
                credentials=token_response.credentials,
                expires_at=token_response.expires_at,
                refresh_token=token_response.refresh_token
            )
            await self.cred_ops.create(cred_data, user_id)

            return {
                "status": "success",
                "message": f"Successfully connected to {integration.name}"
            }

        except Exception as e:
            logger.error(f"OAuth flow failed: {str(e)}")
            raise

    async def make_api_call(
        self,
        integration_id: UUID,
        user_id: UUID,
        method: str,
        endpoint: str,
        params: Optional[Dict] = None,
        data: Optional[Dict] = None
    ) -> Dict:
        """Orchestrate API call with automatic token refresh"""
        try:
            # 1. Get integration and credentials
            integration = await self.int_ops.get(integration_id)
            if not integration:
                raise ValueError("Integration not found")

            credentials = await self.cred_ops.get_for_user_integration(
                user_id=user_id,
                integration_id=integration_id
            )
            if not credentials:
                raise ValueError("No credentials found")

            # 2. Check if refresh needed
            if credentials.needs_refresh():
                token_response = await self.executor.refresh_oauth_token(
                    integration=integration,
                    refresh_token=credentials.refresh_token
                )
                
                # Update credentials
                update_data = CredentialsUpdate(
                    credentials=token_response.credentials,
                    expires_at=token_response.expires_at,
                    refresh_token=token_response.refresh_token
                )
                credentials = await self.cred_ops.update(
                    credentials.credential_id,
                    update_data
                )

            # 3. Make API call
            response = await self.executor.make_api_call(
                integration=integration,
                method=method,
                endpoint=endpoint,
                credentials=credentials.credentials,
                params=params,
                data=data
            )

            # 4. Update last used timestamp
            await self.cred_ops.update_last_used(credentials.credential_id)

            return response.dict()

        except Exception as e:
            logger.error(f"API call failed: {str(e)}")
            raise