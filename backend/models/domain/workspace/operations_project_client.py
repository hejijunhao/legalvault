# models/domain/workspace/operations_project_client.py
from uuid import UUID
from datetime import datetime
from typing import List, Optional
from sqlmodel import select, Session
from models.database.workspace.project_client import ProjectClient as DBProjectClient
from models.schemas.project_client import ProjectClientCreate, ProjectClientUpdate

class ProjectClientOperations:
    def __init__(self, session: Session):
        self.session = session

    async def create(self, data: ProjectClientCreate, user_id: UUID) -> DBProjectClient:
        db_project_client = DBProjectClient(
            **data.model_dump(),
            created_by=user_id
        )
        self.session.add(db_project_client)
        await self.session.commit()
        await self.session.refresh(db_project_client)
        return db_project_client

    async def get_by_project(self, project_id: UUID) -> List[DBProjectClient]:
        query = select(DBProjectClient).where(DBProjectClient.project_id == project_id)
        result = await self.session.execute(query)
        return result.scalars().all()

    async def get_by_client(self, client_id: UUID) -> List[DBProjectClient]:
        query = select(DBProjectClient).where(DBProjectClient.client_id == client_id)
        result = await self.session.execute(query)
        return result.scalars().all()

    async def update(
        self,
        project_id: UUID,
        client_id: UUID,
        data: ProjectClientUpdate
    ) -> Optional[DBProjectClient]:
        query = select(DBProjectClient).where(
            DBProjectClient.project_id == project_id,
            DBProjectClient.client_id == client_id
        )
        result = await self.session.execute(query)
        db_project_client = result.scalar_one_or_none()
        
        if db_project_client:
            for key, value in data.model_dump(exclude_unset=True).items():
                setattr(db_project_client, key, value)
            db_project_client.updated_at = datetime.utcnow()
            await self.session.commit()
            await self.session.refresh(db_project_client)
        
        return db_project_client

    async def delete(self, project_id: UUID, client_id: UUID) -> bool:
        query = select(DBProjectClient).where(
            DBProjectClient.project_id == project_id,
            DBProjectClient.client_id == client_id
        )
        result = await self.session.execute(query)
        db_project_client = result.scalar_one_or_none()
        
        if db_project_client:
            await self.session.delete(db_project_client)
            await self.session.commit()
            return True
        return False