# models/domain/research/search_message_operations.py

from typing import List, Dict, Any, Optional, Union
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete, update, func

from models.database.research.public_search_messages import PublicSearchMessage
from models.domain.research.search_message import ResearchMessage
from models.enums.research_enums import QueryStatus

# Import DTOs instead of schema models
from models.dtos.research.search_message_dto import (
    SearchMessageDTO, SearchMessageListDTO, SearchMessageCreateDTO, SearchMessageUpdateDTO,
    to_search_message_dto, to_search_message_list_dto
)

class SearchMessageOperations:
    """Operations for managing PublicSearchMessage records in the database."""

    def __init__(self, db_session: AsyncSession):
        self.db = db_session

    async def get_next_sequence(self, search_id: UUID) -> int:
        """Get the next sequence number for a message in a search."""
        query = select(func.max(PublicSearchMessage.sequence)).where(
            PublicSearchMessage.search_id == search_id
        ).execution_options(
            no_parameters=True,
            use_server_side_cursors=False  # Disable server-side cursors which use prepared statements
        )
        result = await self.db.execute(query)
        max_sequence = result.scalar() or 0
        return max_sequence + 1

    def create_message(self, search_id: UUID, role: str, content: Dict[str, Any], sequence: int, status: QueryStatus = QueryStatus.PENDING) -> PublicSearchMessage:
        """Create a new message and add it to the session without committing."""
        message = ResearchMessage(content=content, role=role, sequence=sequence)
        db_message = PublicSearchMessage(
            search_id=search_id,
            role=message.role,
            content=message.content,
            sequence=sequence,
            status=status
        )
        self.db.add(db_message)
        return db_message

    async def get_message_by_id(self, message_id: UUID) -> Optional[SearchMessageDTO]:
        """Retrieve a message by its ID."""
        query = select(PublicSearchMessage).where(PublicSearchMessage.id == message_id).execution_options(
            no_parameters=True,
            use_server_side_cursors=False  # Disable server-side cursors which use prepared statements
        )
        result = await self.db.execute(query)
        db_message = result.scalars().first()
        if db_message:
            return to_search_message_dto(db_message)
        return None

    async def update_message(self, message_id: UUID, updates: SearchMessageUpdateDTO) -> Optional[SearchMessageDTO]:
        """Update a message's content or other attributes."""
        query = select(PublicSearchMessage).where(PublicSearchMessage.id == message_id).execution_options(
            no_parameters=True,
            use_server_side_cursors=False  # Disable server-side cursors which use prepared statements
        )
        result = await self.db.execute(query)
        db_message = result.scalars().first()
        if not db_message:
            return None
            
        # Convert DTO to dict and update fields
        updates_dict = updates.dict(exclude_unset=True)
        if not updates_dict:
            # No updates provided, return current state
            return to_search_message_dto(db_message)
            
        if "content" in updates_dict:
            temp_message = ResearchMessage(content=updates_dict["content"], role=db_message.role)
            db_message.content = temp_message.content
        
        for key, value in updates_dict.items():
            if key != "content" and hasattr(db_message, key):
                setattr(db_message, key, value)
                
        await self.db.commit()
        return to_search_message_dto(db_message)

    async def update_message_status(self, message_id: UUID, status: QueryStatus) -> Optional[SearchMessageDTO]:
        """Update a message's status."""
        query = select(PublicSearchMessage).where(PublicSearchMessage.id == message_id).execution_options(
            no_parameters=True,
            use_server_side_cursors=False  # Disable server-side cursors which use prepared statements
        )
        result = await self.db.execute(query)
        db_message = result.scalars().first()
        if not db_message:
            return None
            
        db_message.status = status
        await self.db.commit()
        return to_search_message_dto(db_message)

    async def delete_message(self, message_id: UUID) -> bool:
        """Delete a message from the database."""
        query = delete(PublicSearchMessage).where(PublicSearchMessage.id == message_id).execution_options(
            no_parameters=True,
            use_server_side_cursors=False  # Disable server-side cursors which use prepared statements
        )
        result = await self.db.execute(query)
        await self.db.commit()
        return result.rowcount > 0

    async def list_messages_by_search(self, search_id: UUID, limit: int = 100, offset: int = 0) -> SearchMessageListDTO:
        """List all messages for a given search with pagination."""
        # Query for messages
        query = select(PublicSearchMessage).where(PublicSearchMessage.search_id == search_id)\
            .order_by(PublicSearchMessage.sequence).offset(offset).limit(limit).execution_options(
                no_parameters=True,
                use_server_side_cursors=False  # Disable server-side cursors which use prepared statements
            )
        result = await self.db.execute(query)
        messages = result.scalars().all()
        
        # Count total messages
        count_query = select(func.count()).select_from(PublicSearchMessage).where(
            PublicSearchMessage.search_id == search_id
        ).execution_options(
            no_parameters=True,
            use_server_side_cursors=False  # Disable server-side cursors which use prepared statements
        )
        count_result = await self.db.execute(count_query)
        total_count = count_result.scalar() or 0
        
        # Convert to DTO
        return to_search_message_list_dto(messages, total_count, search_id)

    async def list_messages_by_status(self, status: QueryStatus, limit: int = 100, offset: int = 0) -> List[SearchMessageDTO]:
        """List messages by status with pagination."""
        query = select(PublicSearchMessage).where(PublicSearchMessage.status == status)\
            .order_by(PublicSearchMessage.created_at).offset(offset).limit(limit).execution_options(
                no_parameters=True,
                use_server_side_cursors=False  # Disable server-side cursors which use prepared statements
            )
        result = await self.db.execute(query)
        messages = result.scalars().all()
        
        return [to_search_message_dto(msg) for msg in messages]

    async def create_message_with_commit(self, message_create_dto: SearchMessageCreateDTO) -> SearchMessageDTO:
        """Create a new message and commit it to the database."""
        try:
            # Create domain model for validation
            message = ResearchMessage(
                content=message_create_dto.content,
                role=message_create_dto.role,
                sequence=message_create_dto.sequence or 1
            )
            
            # If sequence not provided, get the next sequence number
            if message_create_dto.sequence is None:
                message.sequence = await self.get_next_sequence(message_create_dto.search_id)
            
            # Create database record
            db_message = PublicSearchMessage(
                search_id=message_create_dto.search_id,
                role=message.role,
                content=message.content,
                sequence=message.sequence,
                status=message_create_dto.status if hasattr(message_create_dto, 'status') else QueryStatus.PENDING
            )
            self.db.add(db_message)
            await self.db.commit()
            
            # Refresh to get generated values
            await self.db.refresh(db_message)
            
            # Return as DTO
            return to_search_message_dto(db_message)
        except Exception as e:
            await self.db.rollback()
            raise e