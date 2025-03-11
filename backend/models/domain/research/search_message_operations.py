# models/domain/research/search_message_operations.py

from typing import List, Dict, Any, Optional
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete, update

from models.database.research.public_search_messages import PublicSearchMessage
from models.domain.research.search_message import ResearchMessage

class SearchMessageOperations:
    """Operations for managing PublicSearchMessage records in the database."""

    def __init__(self, db_session: AsyncSession):
        self.db = db_session

    def create_message(self, search_id: UUID, role: str, content: Dict[str, Any], sequence: int) -> PublicSearchMessage:
        """Create a new message and add it to the session without committing."""
        message = ResearchMessage(content=content, role=role)
        db_message = PublicSearchMessage(
            search_id=search_id,
            role=message.role,
            content=message.content,
            sequence=sequence
        )
        self.db.add(db_message)
        return db_message

    async def get_message_by_id(self, message_id: UUID) -> Optional[Dict[str, Any]]:
        """Retrieve a message by its ID."""
        query = select(PublicSearchMessage).where(PublicSearchMessage.id == message_id)
        result = await self.db.execute(query)
        db_message = result.scalars().first()
        if db_message:
            return {
                "id": db_message.id,
                "search_id": db_message.search_id,
                "role": db_message.role,
                "content": db_message.content,
                "sequence": db_message.sequence
            }
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

    async def list_messages_by_search(self, search_id: UUID, limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        """List all messages for a given search with pagination."""
        query = select(PublicSearchMessage).where(PublicSearchMessage.search_id == search_id)\
            .order_by(PublicSearchMessage.sequence).offset(offset).limit(limit)
        result = await self.db.execute(query)
        messages = result.scalars().all()
        return [
            {
                "id": m.id,
                "search_id": m.search_id,
                "role": m.role,
                "content": m.content,
                "sequence": m.sequence
            }
            for m in messages
        ]