# models/domain/research/search_message_operations.py

from typing import List, Dict, Any, Optional, Union
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete, update, func

from models.database.research.public_search_messages import PublicSearchMessage
from models.domain.research.search_message import ResearchMessage
from models.schemas.research.search_message import SearchMessageResponse, SearchMessageListResponse

class SearchMessageOperations:
    """Operations for managing PublicSearchMessage records in the database."""

    def __init__(self, db_session: AsyncSession):
        self.db = db_session

    def create_message(self, search_id: UUID, role: str, content: Dict[str, Any], sequence: int) -> PublicSearchMessage:
        """Create a new message and add it to the session without committing."""
        message = ResearchMessage(content=content, role=role, sequence=sequence)
        db_message = PublicSearchMessage(
            search_id=search_id,
            role=message.role,
            content=message.content,
            sequence=sequence
        )
        self.db.add(db_message)
        return db_message

    async def get_message_by_id(self, message_id: UUID) -> Optional[SearchMessageResponse]:
        """Retrieve a message by its ID."""
        query = select(PublicSearchMessage).where(PublicSearchMessage.id == message_id)
        result = await self.db.execute(query)
        db_message = result.scalars().first()
        if db_message:
            # Get search title if possible
            search_title = None
            if hasattr(db_message, 'search') and db_message.search:
                search_title = db_message.search.title
            
            return SearchMessageResponse(
                id=db_message.id,
                search_id=db_message.search_id,
                search_title=search_title,
                role=db_message.role,
                content=db_message.content,
                sequence=db_message.sequence,
                created_at=db_message.created_at,
                updated_at=db_message.updated_at
            )
        return None

    async def update_message(self, message_id: UUID, updates: Dict[str, Any]) -> bool:
        """Update a message's content or other attributes."""
        query = select(PublicSearchMessage).where(PublicSearchMessage.id == message_id)
        result = await self.db.execute(query)
        db_message = result.scalars().first()
        if not db_message:
            return False
        if "content" in updates:
            temp_message = ResearchMessage(content=updates["content"], role=db_message.role)
            db_message.content = temp_message.content
        for key, value in updates.items():
            if key != "content":
                setattr(db_message, key, value)
        await self.db.commit()
        return True

    async def delete_message(self, message_id: UUID) -> bool:
        """Delete a message from the database."""
        query = delete(PublicSearchMessage).where(PublicSearchMessage.id == message_id)
        result = await self.db.execute(query)
        await self.db.commit()
        return result.rowcount > 0

    async def list_messages_by_search(self, search_id: UUID, limit: int = 100, offset: int = 0) -> List[SearchMessageResponse]:
        """List all messages for a given search with pagination."""
        query = select(PublicSearchMessage).where(PublicSearchMessage.search_id == search_id)\
            .order_by(PublicSearchMessage.sequence).offset(offset).limit(limit)
        result = await self.db.execute(query)
        messages = result.scalars().all()
        
        # Get search title if possible
        search_title = None
        if messages and hasattr(messages[0], 'search') and messages[0].search:
            search_title = messages[0].search.title
        
        return [
            SearchMessageResponse(
                id=m.id,
                search_id=m.search_id,
                search_title=search_title,
                role=m.role,
                content=m.content,
                sequence=m.sequence,
                created_at=m.created_at,
                updated_at=m.updated_at
            )
            for m in messages
        ]

    async def count_messages_by_search(self, search_id: UUID) -> int:
        """Count the total number of messages for a given search without retrieving all records."""
        query = select(func.count()).where(PublicSearchMessage.search_id == search_id)
        result = await self.db.execute(query)
        count = result.scalar_one()
        return count
        
    async def get_messages_list_response(self, search_id: UUID, limit: int = 100, offset: int = 0) -> SearchMessageListResponse:
        """Get a complete list response with pagination metadata."""
        messages = await self.list_messages_by_search(search_id, limit, offset)
        total = await self.count_messages_by_search(search_id)
        
        return SearchMessageListResponse(
            items=messages,
            total=total,
            offset=offset,
            limit=limit
        )