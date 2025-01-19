# services/executors/workspace/client_executor.py

from datetime import datetime
from typing import List, Optional, Dict, Any
from uuid import UUID

from sqlmodel import Session, select
from fastapi import HTTPException

from models.database.workspace.client import Client, ClientStatus, LegalEntityType
from models.domain.workspace.client import ClientDomain
from models.schemas.workspace.client import (
    ClientCreate,
    ClientUpdate,
    ClientProfileUpdate,
    ClientTagsUpdate
)


class ClientExecutor:
    """
    Executes client-related operations and handles database interactions.
    """

    def __init__(self, session: Session):
        self.session = session

    async def create_client(self, data: ClientCreate, user_id: UUID) -> ClientDomain:
        """Creates a new client."""
        try:
            client = Client(
                name=data.name,
                legal_entity_type=data.legal_entity_type,
                status=ClientStatus.ACTIVE,
                domicile=data.domicile,
                primary_email=data.primary_email,
                primary_phone=data.primary_phone,
                address=data.address.dict(),
                client_join_date=data.client_join_date,
                industry=data.industry,
                tax_id=data.tax_id,
                registration_number=data.registration_number,
                website=str(data.website) if data.website else None,
                preferences=data.preferences.dict() if data.preferences else None,
                tags=data.tags,
                created_by=user_id,
                modified_by=user_id
            )

            self.session.add(client)
            await self.session.commit()
            await self.session.refresh(client)

            return ClientDomain(**client.dict())
        except Exception as e:
            await self.session.rollback()
            raise HTTPException(status_code=400, detail=str(e))

    async def update_client(
            self, client_id: UUID, data: ClientUpdate, user_id: UUID
    ) -> ClientDomain:
        """Updates client details."""
        try:
            client = await self._get_client(client_id)
            domain_client = ClientDomain(**client.dict())

            # Update core details if provided
            if any([data.name, data.legal_entity_type, data.industry]):
                domain_client.update_core_details(
                    name=data.name,
                    legal_entity_type=data.legal_entity_type,
                    industry=data.industry,
                    modified_by=user_id
                )

            # Update contact info if provided
            if any([data.primary_email, data.primary_phone, data.address, data.website]):
                domain_client.update_contact_info(
                    primary_email=data.primary_email,
                    primary_phone=data.primary_phone,
                    address=data.address.dict() if data.address else None,
                    website=str(data.website) if data.website else None,
                    modified_by=user_id
                )

            # Update business info if provided
            if any([data.tax_id, data.registration_number, data.domicile]):
                domain_client.update_business_info(
                    tax_id=data.tax_id,
                    registration_number=data.registration_number,
                    domicile=data.domicile,
                    modified_by=user_id
                )

            # Update preferences if provided
            if data.preferences:
                domain_client.update_preferences(
                    data.preferences.dict(),
                    modified_by=user_id
                )

            # Update status if provided
            if data.status is not None:
                if data.status == ClientStatus.INACTIVE:
                    domain_client.deactivate(user_id)
                else:
                    domain_client.reactivate(user_id)

            # Update database model
            for field, value in data.dict(exclude_unset=True).items():
                if field == 'address' and value:
                    value = value.dict()
                elif field == 'preferences' and value:
                    value = value.dict()
                elif field == 'website' and value:
                    value = str(value)
                setattr(client, field, value)

            client.modified_by = user_id
            client.updated_at = datetime.utcnow()

            await self.session.commit()
            await self.session.refresh(client)

            return ClientDomain(**client.dict())
        except Exception as e:
            await self.session.rollback()
            raise HTTPException(status_code=400, detail=str(e))

    async def update_profile(
            self, client_id: UUID, data: ClientProfileUpdate, user_id: UUID
    ) -> ClientDomain:
        """Updates client profile."""
        try:
            client = await self._get_client(client_id)
            domain_client = ClientDomain(**client.dict())

            domain_client.update_profile(data.summary, user_id)

            client.client_profile = domain_client.client_profile
            client.modified_by = user_id
            client.updated_at = datetime.utcnow()

            await self.session.commit()
            await self.session.refresh(client)

            return ClientDomain(**client.dict())
        except Exception as e:
            await self.session.rollback()
            raise HTTPException(status_code=400, detail=str(e))

    async def update_tags(
            self, client_id: UUID, data: ClientTagsUpdate, user_id: UUID
    ) -> ClientDomain:
        """Updates client tags."""
        try:
            client = await self._get_client(client_id)
            domain_client = ClientDomain(**client.dict())

            # Replace all tags
            current_tags = set(domain_client.tags)
            new_tags = set(data.tags)

            tags_to_remove = list(current_tags - new_tags)
            tags_to_add = list(new_tags - current_tags)

            if tags_to_remove:
                domain_client.remove_tags(tags_to_remove, user_id)
            if tags_to_add:
                domain_client.add_tags(tags_to_add, user_id)

            client.tags = domain_client.tags
            client.modified_by = user_id
            client.updated_at = datetime.utcnow()

            await self.session.commit()
            await self.session.refresh(client)

            return ClientDomain(**client.dict())
        except Exception as e:
            await self.session.rollback()
            raise HTTPException(status_code=400, detail=str(e))

    async def deactivate_client(self, client_id: UUID, user_id: UUID) -> ClientDomain:
        """Deactivates a client."""
        try:
            client = await self._get_client(client_id)
            domain_client = ClientDomain(**client.dict())

            domain_client.deactivate(user_id)

            client.status = ClientStatus.INACTIVE
            client.modified_by = user_id
            client.updated_at = datetime.utcnow()

            await self.session.commit()
            await self.session.refresh(client)

            return ClientDomain(**client.dict())
        except Exception as e:
            await self.session.rollback()
            raise HTTPException(status_code=400, detail=str(e))

    async def reactivate_client(self, client_id: UUID, user_id: UUID) -> ClientDomain:
        """Reactivates a client."""
        try:
            client = await self._get_client(client_id)
            domain_client = ClientDomain(**client.dict())

            domain_client.reactivate(user_id)

            client.status = ClientStatus.ACTIVE
            client.modified_by = user_id
            client.updated_at = datetime.utcnow()

            await self.session.commit()
            await self.session.refresh(client)

            return ClientDomain(**client.dict())
        except Exception as e:
            await self.session.rollback()
            raise HTTPException(status_code=400, detail=str(e))

    async def delete_client(self, client_id: UUID) -> None:
        """Deletes a client."""
        try:
            client = await self._get_client(client_id)
            await self.session.delete(client)
            await self.session.commit()
        except Exception as e:
            await self.session.rollback()
            raise HTTPException(status_code=400, detail=str(e))

    async def get_client(self, client_id: UUID) -> ClientDomain:
        """Retrieves a client by ID."""
        client = await self._get_client(client_id)
        return ClientDomain(**client.dict())

    async def list_clients(
            self,
            status: Optional[ClientStatus] = None,
            legal_entity_type: Optional[LegalEntityType] = None,
            tags: Optional[List[str]] = None
    ) -> List[ClientDomain]:
        """Retrieves clients with optional filters."""
        try:
            query = select(Client)

            if status:
                query = query.where(Client.status == status)
            if legal_entity_type:
                query = query.where(Client.legal_entity_type == legal_entity_type)
            if tags:
                # Filter clients that have all specified tags
                for tag in tags:
                    query = query.where(Client.tags.contains([tag]))

            # Order by name and status
            query = query.order_by(Client.name, Client.status)

            result = await self.session.execute(query)
            clients = result.scalars().all()

            return [ClientDomain(**client.dict()) for client in clients]
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))

    async def search_clients(
            self,
            search_term: str,
            limit: int = 10
    ) -> List[ClientDomain]:
        """
        Searches for clients by name or other relevant fields.
        Basic implementation - can be enhanced with full-text search.
        """
        try:
            query = select(Client).where(
                Client.name.ilike(f"%{search_term}%")
            ).limit(limit)

            result = await self.session.execute(query)
            clients = result.scalars().all()

            return [ClientDomain(**client.dict()) for client in clients]
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))

    async def _get_client(self, client_id: UUID) -> Client:
        """Helper method to get client by ID."""
        client = await self.session.get(Client, client_id)
        if not client:
            raise HTTPException(status_code=404, detail="Client not found")
        return client