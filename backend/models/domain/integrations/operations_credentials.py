# models/domain/integrations/operations_credentials.py

from datetime import datetime
from typing import List, Optional
from uuid import UUID
from sqlmodel import select, Session
from models.database.integrations.credentials import Credentials as DBCredentials
from models.database.integrations.integration import Integration as DBIntegration
from models.domain.integrations.credentials import Credentials
from models.schemas.integrations.credentials import CredentialsCreate, CredentialsUpdate

class CredentialsOperations:
    def __init__(self, session: Session):
        self.session = session

    async def create(self, data: CredentialsCreate, user_id: UUID) -> Credentials:
        """Create new integration credentials for a user"""
        db_credentials = DBCredentials(
            user_id=user_id,
            **data.model_dump()
        )
        self.session.add(db_credentials)
        await self.session.commit()
        await self.session.refresh(db_credentials)
        return self._to_domain(db_credentials)

    async def get(self, credential_id: UUID) -> Optional[Credentials]:
        """Get credentials by ID"""
        query = select(DBCredentials).where(DBCredentials.credential_id == credential_id)
        result = await self.session.execute(query)
        db_credentials = result.scalar_one_or_none()
        return self._to_domain(db_credentials) if db_credentials else None

    async def get_for_user_integration(
        self, 
        user_id: UUID, 
        integration_id: UUID
    ) -> Optional[Credentials]:
        """Get active credentials for a specific user and integration"""
        query = select(DBCredentials).where(
            DBCredentials.user_id == user_id,
            DBCredentials.integration_id == integration_id,
            DBCredentials.is_active == True
        )
        result = await self.session.execute(query)
        db_credentials = result.scalar_one_or_none()
        return self._to_domain(db_credentials) if db_credentials else None

    async def list_for_user(
        self,
        user_id: UUID,
        skip: int = 0,
        limit: int = 100,
        active_only: bool = True
    ) -> List[Credentials]:
        """List all credentials for a user"""
        query = select(DBCredentials).where(DBCredentials.user_id == user_id)
        if active_only:
            query = query.where(DBCredentials.is_active == True)
        query = query.offset(skip).limit(limit)
        result = await self.session.execute(query)
        return [self._to_domain(c) for c in result.scalars().all()]

    async def update(
        self,
        credential_id: UUID,
        data: CredentialsUpdate
    ) -> Optional[Credentials]:
        """Update existing credentials"""
        query = select(DBCredentials).where(DBCredentials.credential_id == credential_id)
        result = await self.session.execute(query)
        db_credentials = result.scalar_one_or_none()
        
        if not db_credentials:
            return None

        for key, value in data.model_dump(exclude_unset=True).items():
            setattr(db_credentials, key, value)
        
        db_credentials.modified_at = datetime.utcnow()
        await self.session.commit()
        await self.session.refresh(db_credentials)
        return self._to_domain(db_credentials)

    async def deactivate(self, credential_id: UUID) -> bool:
        """Deactivate credentials"""
        query = select(DBCredentials).where(DBCredentials.credential_id == credential_id)
        result = await self.session.execute(query)
        db_credentials = result.scalar_one_or_none()
        
        if not db_credentials:
            return False

        db_credentials.is_active = False
        db_credentials.modified_at = datetime.utcnow()
        await self.session.commit()
        return True

    async def update_last_used(self, credential_id: UUID) -> bool:
        """Update last used timestamp"""
        query = select(DBCredentials).where(DBCredentials.credential_id == credential_id)
        result = await self.session.execute(query)
        db_credentials = result.scalar_one_or_none()
        
        if not db_credentials:
            return False

        db_credentials.last_used_at = datetime.utcnow()
        await self.session.commit()
        return True

    def _to_domain(self, db_credentials: Optional[DBCredentials]) -> Optional[Credentials]:
        """Convert database model to domain model"""
        if not db_credentials:
            return None
        return Credentials(db_credentials)