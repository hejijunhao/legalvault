# models/domain/research/search_message_operations.py

from typing import List, Dict, Any, Optional
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from datetime import datetime
import logging

from models.database.research.public_search_messages import PublicSearchMessage
from models.enums.research_enums import QueryStatus
from models.domain.research.research_errors import DatabaseError
from models.dtos.research.search_message_dto import (
    SearchMessageDTO, SearchMessageListDTO, SearchMessageCreateDTO,
    to_search_message_dto, to_search_message_list_dto
)

logger = logging.getLogger(__name__)

class SearchMessageOperations:
    """Operations for managing PublicSearchMessage records in the database."""

    def __init__(self, db_session: AsyncSession):
        self.db = db_session
        self.execution_options = {
            "no_parameters": True,
            "use_server_side_cursors": False
        }

    async def _execute_query(self, query, execution_options: Optional[Dict[str, Any]] = None) -> Any:
        """Execute a query with pgBouncer compatibility settings."""
        try:
            opts = execution_options or self.execution_options
            result = await self.db.execute(query.execution_options(**opts))
            return result
        except Exception as e:
            error_message = str(e).lower()
            if any(err in error_message for err in ["duplicatepreparedstatementerror", "prepared statement", "invalidsqlstatementnameerror"]):
                logger.warning(f"pgBouncer prepared statement error: {e}")
                raise DatabaseError("Prepared statement error", details={"query": str(query)}, original_error=e)
            raise DatabaseError("Failed to execute query", details={"query": str(query)}, original_error=e)

    def _tuple_to_message_dto(self, message_tuple: tuple) -> SearchMessageDTO:
        """Convert a database tuple to a SearchMessageDTO."""
        try:
            id_val, search_id, role, content, sequence, status, created_at, updated_at = message_tuple
            status_value = status.value if hasattr(status, "value") else status
            return SearchMessageDTO(role=role, content=content, sequence=sequence)
        except (ValueError, IndexError) as e:
            logger.error(f"Tuple structure mismatch: {e}")
            return SearchMessageDTO(role="system", content={"text": "Error retrieving message data"}, sequence=0)

    async def get_next_sequence(self, search_id: UUID, execution_options: Optional[Dict[str, Any]] = None) -> int:
        """Get the next sequence number for a message in a search."""
        query = select(func.max(PublicSearchMessage.sequence)).where(PublicSearchMessage.search_id == search_id)
        result = await self._execute_query(query, execution_options)
        return (result.scalar() or 0) + 1

    async def get_message_by_id(self, message_id: UUID, execution_options: Optional[Dict[str, Any]] = None) -> Optional[SearchMessageDTO]:
        """Retrieve a message by its ID."""
        query = select(PublicSearchMessage).where(PublicSearchMessage.id == message_id)
        result = await self._execute_query(query, execution_options)
        db_message = result.scalars().first()
        return to_search_message_dto(db_message) if db_message else None

    async def list_messages_by_search(self, search_id: UUID, limit: int = 100, offset: int = 0,
                                      execution_options: Optional[Dict[str, Any]] = None) -> SearchMessageListDTO:
        """List all messages for a search with pagination."""
        query = select(PublicSearchMessage).where(PublicSearchMessage.search_id == search_id)\
            .order_by(PublicSearchMessage.sequence).offset(offset).limit(limit)
        result = await self._execute_query(query, execution_options)
        messages = result.scalars().all()
        message_dtos = [to_search_message_dto(m) if not isinstance(m, tuple) else self._tuple_to_message_dto(m) for m in messages]
        count_query = select(func.count()).where(PublicSearchMessage.search_id == search_id)
        total_count = (await self._execute_query(count_query, execution_options)).scalar() or 0
        return SearchMessageListDTO(items=message_dtos, total=total_count, search_id=search_id)

    async def create_message_with_commit(self, message_create_dto: SearchMessageCreateDTO,
                                         execution_options: Optional[Dict[str, Any]] = None) -> SearchMessageDTO:
        """Create a new message and commit it."""
        try:
            sequence = message_create_dto.sequence or await self.get_next_sequence(message_create_dto.search_id, execution_options)
            db_message = PublicSearchMessage(
                search_id=message_create_dto.search_id,
                role=message_create_dto.role,
                content=message_create_dto.content,
                sequence=sequence,
                status=message_create_dto.status or QueryStatus.PENDING
            )
            self.db.add(db_message)
            await self.db.commit()
            await self.db.refresh(db_message)
            return to_search_message_dto(db_message)
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error creating message: {e}")
            raise DatabaseError("Failed to create message", details={"dto": str(message_create_dto)}, original_error=e)

    async def get_messages_list_response(self, search_id: UUID, limit: int = 100, offset: int = 0,
                                         execution_options: Optional[Dict[str, Any]] = None) -> SearchMessageListDTO:
        """Get a paginated list of messages for a search."""
        messages_list = await self.list_messages_by_search(search_id, limit, offset, execution_options or self.execution_options)
        messages_list.offset = offset
        messages_list.limit = limit
        return messages_list

    async def get_messages_for_search(self, search_id: UUID, user_id: UUID, user_permissions: List[str],
                                      after_time: Optional[datetime] = None,
                                      execution_options: Optional[Dict[str, Any]] = None) -> List[SearchMessageDTO]:
        """Get completed messages for a search, designed for SSE delivery."""
        # TODO: Implement permission checks using user_id and user_permissions
        try:
            query = select(PublicSearchMessage).where(
                PublicSearchMessage.search_id == search_id,
                PublicSearchMessage.status == QueryStatus.COMPLETED
            )
            if after_time:
                query = query.where(PublicSearchMessage.updated_at > after_time)
            query = query.order_by(PublicSearchMessage.sequence)
            result = await self._execute_query(query, execution_options)
            messages = result.scalars().all()
            return [to_search_message_dto(m) if not isinstance(m, tuple) else self._tuple_to_message_dto(m) for m in messages]
        except Exception as e:
            logger.error(f"Error fetching messages for SSE: {e}")
            return []