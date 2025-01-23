# models/domain/operations/library/operations_masterfiledatabase.py

from typing import Optional, List, Dict, Any
from uuid import UUID
from sqlmodel import Session, select
from models.database.library.masterfiledatabase import MasterFileDatabase
from models.domain.library.masterfiledatabase import MasterFile

class MasterFileOperations:
    def __init__(self, session: Session):
        self.session = session

    async def get_file(self, file_id: UUID) -> Optional[MasterFile]:
        """Retrieve a single file by ID."""
        db_file = await self.session.get(MasterFileDatabase, file_id)
        return MasterFile(db_file) if db_file else None

    async def create_file(self, file_data: Dict[str, Any]) -> MasterFile:
        """Create a new file record."""
        db_file = MasterFileDatabase(**file_data)
        self.session.add(db_file)
        await self.session.commit()
        return MasterFile(db_file)

    async def get_files_by_owner(self, owner_id: UUID, include_hidden: bool = False) -> List[MasterFile]:
        """Retrieve all files for an owner."""
        query = select(MasterFileDatabase).where(MasterFileDatabase.owner_id == owner_id)
        if not include_hidden:
            query = query.where(MasterFileDatabase.file_attributes['status'].astext != 'hidden')
        db_files = await self.session.execute(query)
        return [MasterFile(db_file) for db_file in db_files.scalars().all()]

    async def get_files_by_client(self, client_id: UUID) -> List[MasterFile]:
        """Retrieve all files associated with a client."""
        query = select(MasterFileDatabase).where(MasterFileDatabase.client_id == client_id)
        db_files = await self.session.execute(query)
        return [MasterFile(db_file) for db_file in db_files.scalars().all()]

    async def update_file_status(self, file_id: UUID, action: str) -> Optional[MasterFile]:
        """Update file status based on action."""
        domain_file = await self.get_file(file_id)
        if not domain_file:
            return None

        actions = {
            'hide': domain_file.hide_file,
            'unhide': domain_file.unhide_file,
            'delete': domain_file.delete_file,
            'start_processing': domain_file.start_processing,
            'finish_processing': domain_file.finish_processing
        }

        if action in actions:
            actions[action]()
            await self.session.commit()
        return domain_file

    async def update_metadata(self, file_id: UUID, metadata: Dict[str, Any]) -> Optional[MasterFile]:
        """Update file metadata."""
        domain_file = await self.get_file(file_id)
        if domain_file:
            domain_file.update_metadata(metadata)
            await self.session.commit()
        return domain_file

    async def update_content_details(self, file_id: UUID, details: Dict[str, Any]) -> Optional[MasterFile]:
        """Update file content details."""
        domain_file = await self.get_file(file_id)
        if domain_file:
            domain_file.update_content_details(details)
            await self.session.commit()
        return domain_file

    async def update_permissions(self, file_id: UUID, user_id: UUID, add: bool = True) -> Optional[MasterFile]:
        """Update file permissions."""
        domain_file = await self.get_file(file_id)
        if domain_file:
            domain_file.update_permissions(user_id, add)
            await self.session.commit()
        return domain_file

    async def change_owner(self, file_id: UUID, new_owner_id: UUID) -> Optional[MasterFile]:
        """Change file ownership."""
        domain_file = await self.get_file(file_id)
        if domain_file:
            domain_file.change_owner(new_owner_id)
            await self.session.commit()
        return domain_file