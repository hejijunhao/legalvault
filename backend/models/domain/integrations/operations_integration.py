# models/domain/integrations/operations_integration.py

from typing import List, Optional, Tuple
from uuid import UUID
from sqlmodel import select, Session, and_
from models.database.integrations.integration import Integration as DBIntegration
from models.database.integrations.integration_ability import IntegrationAbility
from models.database.integrations.credentials import Credentials as DBCredentials
from models.domain.integrations.integration import Integration
from models.schemas.integrations.integration import IntegrationCreate, IntegrationUpdate

class IntegrationOperations:
    def __init__(self, session: Session):
        self.session = session

    async def create(self, data: IntegrationCreate) -> Integration:
        """Create a new integration"""
        db_integration = DBIntegration(**data.model_dump())
        self.session.add(db_integration)
        await self.session.commit()
        await self.session.refresh(db_integration)
        return self._to_domain(db_integration)

    async def get(self, integration_id: UUID) -> Optional[Integration]:
        """Get integration by ID with related credentials and abilities"""
        query = select(DBIntegration).where(DBIntegration.integration_id == integration_id)
        result = await self.session.execute(query)
        db_integration = result.scalar_one_or_none()
        
        if not db_integration:
            return None

        # Load relationships
        credentials = await self._get_credentials(integration_id)
        abilities = await self._get_abilities(integration_id)
        
        integration = self._to_domain(db_integration)
        integration.set_credentials(credentials)
        integration.set_abilities(abilities)
        return integration

    async def get_by_name(self, name: str) -> Optional[Integration]:
        """Get integration by name"""
        query = select(DBIntegration).where(DBIntegration.name == name)
        result = await self.session.execute(query)
        db_integration = result.scalar_one_or_none()
        return self._to_domain(db_integration) if db_integration else None

    async def list(
        self,
        skip: int = 0,
        limit: int = 100,
        active_only: bool = True,
        auth_type: Optional[str] = None
    ) -> List[Integration]:
        """List integrations with optional filtering"""
        query = select(DBIntegration)
        
        if active_only:
            query = query.where(DBIntegration.is_active == True)
        if auth_type:
            query = query.where(DBIntegration.auth_type == auth_type)
            
        query = query.offset(skip).limit(limit)
        result = await self.session.execute(query)
        return [self._to_domain(i) for i in result.scalars().all()]

    async def list_for_ability(
        self,
        ability_id: UUID,
        required_only: bool = False
    ) -> List[Tuple[Integration, bool]]:
        """List integrations for a specific ability with their required status"""
        query = select(DBIntegration, IntegrationAbility).join(
            IntegrationAbility,
            DBIntegration.integration_id == IntegrationAbility.integration_id
        ).where(
            and_(
                IntegrationAbility.ability_id == ability_id,
                DBIntegration.is_active == True
            )
        )
        
        if required_only:
            query = query.where(IntegrationAbility.is_required == True)
            
        result = await self.session.execute(query)
        return [(self._to_domain(i), ia.is_required) for i, ia in result.all()]

    async def update(
        self,
        integration_id: UUID,
        data: IntegrationUpdate
    ) -> Optional[Integration]:
        """Update existing integration"""
        query = select(DBIntegration).where(DBIntegration.integration_id == integration_id)
        result = await self.session.execute(query)
        db_integration = result.scalar_one_or_none()
        
        if not db_integration:
            return None

        for key, value in data.model_dump(exclude_unset=True).items():
            setattr(db_integration, key, value)
        
        await self.session.commit()
        await self.session.refresh(db_integration)
        return self._to_domain(db_integration)

    async def deactivate(self, integration_id: UUID) -> bool:
        """Deactivate integration and all associated credentials"""
        query = select(DBIntegration).where(DBIntegration.integration_id == integration_id)
        result = await self.session.execute(query)
        db_integration = result.scalar_one_or_none()
        
        if not db_integration:
            return False

        # Deactivate integration
        db_integration.is_active = False
        
        # Deactivate all associated credentials
        creds_query = select(DBCredentials).where(
            DBCredentials.integration_id == integration_id,
            DBCredentials.is_active == True
        )
        creds_result = await self.session.execute(creds_query)
        for cred in creds_result.scalars().all():
            cred.is_active = False
        
        await self.session.commit()
        return True

    async def _get_credentials(self, integration_id: UUID) -> List[DBCredentials]:
        """Get all credentials for an integration"""
        query = select(DBCredentials).where(
            DBCredentials.integration_id == integration_id
        )
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def _get_abilities(self, integration_id: UUID) -> List[IntegrationAbility]:
        """Get all ability mappings for an integration"""
        query = select(IntegrationAbility).where(
            IntegrationAbility.integration_id == integration_id
        )
        result = await self.session.execute(query)
        return list(result.scalars().all())

    def _to_domain(self, db_integration: Optional[DBIntegration]) -> Optional[Integration]:
        """Convert database model to domain model"""
        if not db_integration:
            return None
        return Integration(db_integration)