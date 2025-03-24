# models/domain/research/search_message_operations.py

from typing import List, Dict, Any, Optional, Union
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete, update, func
import logging

from models.database.research.public_search_messages import PublicSearchMessage
from models.domain.research.search_message import ResearchMessage
from models.enums.research_enums import QueryStatus
from models.domain.research.research_errors import ValidationError, DatabaseError

# Import DTOs instead of schema models
from models.dtos.research.search_message_dto import (
    SearchMessageDTO, SearchMessageListDTO, SearchMessageCreateDTO, SearchMessageUpdateDTO,
    to_search_message_dto, to_search_message_list_dto
)

logger = logging.getLogger(__name__)

class SearchMessageOperations:
    """Operations for managing PublicSearchMessage records in the database."""

    def __init__(self, db_session: AsyncSession):
        self.db = db_session
        # Set pgBouncer compatibility options for all operations
        self.execution_options = {
            "no_parameters": True,
            "use_server_side_cursors": False
        }
    
    async def _execute_query(self, query):
        """Execute a query with pgBouncer compatibility settings."""
        try:
            # Apply pgBouncer compatibility options
            result = await self.db.execute(
                query.execution_options(**self.execution_options)
            )
            return result
        except Exception as e:
            if any(err_type in str(e) for err_type in [
                "DuplicatePreparedStatementError",
                "prepared statement",
                "InvalidSQLStatementNameError"
            ]):
                logger.warning("pgBouncer prepared statement error encountered: %s", str(e))
                logger.info("Creating fresh session to retry operation after pgBouncer error")
                # Create a fresh session and retry
                await self.db.close()
                self.db = AsyncSession(bind=self.db.bind)
                try:
                    result = await self.db.execute(
                        query.execution_options(**self.execution_options)
                    )
                    return result
                except Exception as retry_error:
                    raise DatabaseError(
                        "Failed to execute query after retry",
                        details={"query": str(query)},
                        original_error=retry_error
                    )
            raise DatabaseError(
                "Failed to execute query",
                details={"query": str(query)},
                original_error=e
            )

    def _tuple_to_message_dto(self, message_tuple: tuple) -> SearchMessageDTO:
        """Convert a database tuple to a SearchMessageDTO
        
        This method handles the conversion of raw database tuples to proper DTOs
        when pgBouncer compatibility settings cause SQLAlchemy to return tuples.
        
        The tuple structure is expected to match the columns in the PublicSearchMessage table.
        """
        try:
            # Extract values from tuple with safe fallbacks
            # Adjust indices based on the actual query column order
            id_val = message_tuple[0] if len(message_tuple) > 0 else None
            search_id = message_tuple[1] if len(message_tuple) > 1 else None
            role = message_tuple[2] if len(message_tuple) > 2 else "assistant"
            content = message_tuple[3] if len(message_tuple) > 3 else {}
            sequence = message_tuple[4] if len(message_tuple) > 4 else 0
            status = message_tuple[5] if len(message_tuple) > 5 else "completed"
            created_at = message_tuple[6] if len(message_tuple) > 6 else None
            updated_at = message_tuple[7] if len(message_tuple) > 7 else None
            
            # Convert status enum to string if needed
            if hasattr(status, "value"):
                status = status.value
                
            return SearchMessageDTO(
                role=role,
                content=content,
                sequence=sequence
            )
        except Exception as e:
            logger.error(f"Error converting tuple to SearchMessageDTO: {str(e)}")
            logger.debug(f"Tuple structure: {message_tuple}")
            # Return a minimal valid DTO rather than failing
            return SearchMessageDTO(
                role="system",
                content={"text": "Error retrieving message data"},
                sequence=0
            )

    async def get_next_sequence(self, search_id: UUID) -> int:
        """Get the next sequence number for a message in a search."""
        query = select(func.max(PublicSearchMessage.sequence)).where(
            PublicSearchMessage.search_id == search_id
        )
        result = await self._execute_query(query)
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
        query = select(PublicSearchMessage).where(PublicSearchMessage.id == message_id)
        result = await self._execute_query(query)
        db_message = result.scalars().first()
        
        if not db_message:
            return None
            
        # Check if we got a tuple instead of an ORM object
        if isinstance(db_message, tuple):
            logger.info("Received tuple instead of ORM object in get_message_by_id")
            return self._tuple_to_message_dto(db_message)
        else:
            # Convert to DTO using the conversion function for ORM objects
            return to_search_message_dto(db_message)

    async def update_message(self, message_id: UUID, updates: SearchMessageUpdateDTO) -> Optional[SearchMessageDTO]:
        """Update a message's content or other attributes."""
        query = select(PublicSearchMessage).where(PublicSearchMessage.id == message_id)
        result = await self._execute_query(query)
        db_message = result.scalars().first()
        if not db_message:
            return None
            
        # Check if we got a tuple instead of an ORM object
        if isinstance(db_message, tuple):
            logger.warning("Received tuple in update_message, cannot update tuple directly")
            # We need to re-query to get the actual ORM object for updating
            try:
                # Create a new query with different execution options
                retry_query = select(PublicSearchMessage).where(PublicSearchMessage.id == message_id)
                retry_result = await self._execute_query(retry_query)
                db_message = retry_result.scalars().first()
                if not db_message or isinstance(db_message, tuple):
                    logger.error("Failed to get ORM object for update operation")
                    return None
            except Exception as e:
                logger.error(f"Error re-querying for ORM object: {str(e)}")
                raise DatabaseError(
                    "Failed to update message",
                    details={"message_id": str(message_id)},
                    original_error=e
                )
        
        # Update the message attributes
        if hasattr(updates, 'content') and updates.content is not None:
            db_message.content = updates.content
        if hasattr(updates, 'role') and updates.role is not None:
            db_message.role = updates.role
        if hasattr(updates, 'status') and updates.status is not None:
            db_message.status = updates.status
        
        # Commit the changes
        try:
            await self.db.commit()
            await self.db.refresh(db_message)
            return to_search_message_dto(db_message)
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error updating message: {str(e)}")
            raise DatabaseError(
                "Failed to update message",
                details={"message_id": str(message_id)},
                original_error=e
            )

    async def update_message_status(self, message_id: UUID, status: QueryStatus) -> Optional[SearchMessageDTO]:
        """Update a message's status."""
        query = select(PublicSearchMessage).where(PublicSearchMessage.id == message_id)
        result = await self._execute_query(query)
        db_message = result.scalars().first()
        if not db_message:
            return None
            
        # Check if we got a tuple instead of an ORM object
        if isinstance(db_message, tuple):
            logger.warning("Received tuple in update_message_status, cannot update tuple directly")
            # We need to re-query to get the actual ORM object for updating
            try:
                # Create a new query with different execution options
                retry_query = select(PublicSearchMessage).where(PublicSearchMessage.id == message_id)
                retry_result = await self._execute_query(retry_query)
                db_message = retry_result.scalars().first()
                if not db_message or isinstance(db_message, tuple):
                    logger.error("Failed to get ORM object for update operation")
                    return None
            except Exception as e:
                logger.error(f"Error re-querying for ORM object: {str(e)}")
                raise DatabaseError(
                    "Failed to update message status",
                    details={"message_id": str(message_id)},
                    original_error=e
                )
        
        # Update the status
        db_message.status = status
        
        # Commit the changes
        try:
            await self.db.commit()
            await self.db.refresh(db_message)
            return to_search_message_dto(db_message)
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error updating message status: {str(e)}")
            raise DatabaseError(
                "Failed to update message status",
                details={"message_id": str(message_id)},
                original_error=e
            )

    async def delete_message(self, message_id: UUID) -> bool:
        """Delete a message from the database."""
        query = delete(PublicSearchMessage).where(PublicSearchMessage.id == message_id)
        result = await self._execute_query(query)
        await self.db.commit()
        return result.rowcount > 0

    async def list_messages_by_search(self, search_id: UUID, limit: int = 100, offset: int = 0, execution_options: Optional[Dict[str, Any]] = None) -> SearchMessageListDTO:
        """List all messages for a given search with pagination."""
        # Query for messages
        query = select(PublicSearchMessage).where(PublicSearchMessage.search_id == search_id)\
            .order_by(PublicSearchMessage.sequence).offset(offset).limit(limit)
        
        # Use provided execution_options if given, otherwise use default
        if execution_options:
            result = await self.db.execute(
                query.execution_options(**execution_options)
            )
        else:
            result = await self._execute_query(query)
            
        messages = result.scalars().all()
        
        # Convert messages to DTOs, handling both tuple and ORM cases
        message_dtos = []
        if messages:
            for message in messages:
                if isinstance(message, tuple):
                    logger.info("Received tuple instead of ORM object in list_messages_by_search")
                    message_dtos.append(self._tuple_to_message_dto(message))
                else:
                    message_dtos.append(to_search_message_dto(message))
        
        # Count total messages
        count_query = select(func.count()).select_from(PublicSearchMessage).where(
            PublicSearchMessage.search_id == search_id
        )
        
        # Use provided execution_options for count query as well
        if execution_options:
            count_result = await self.db.execute(
                count_query.execution_options(**execution_options)
            )
        else:
            count_result = await self._execute_query(count_query)
            
        total_count = count_result.scalar() or 0
        
        # Return custom DTO with our processed items
        return SearchMessageListDTO(
            items=message_dtos,
            total=total_count,
            search_id=search_id
        )

    async def list_messages_by_status(self, status: QueryStatus, limit: int = 100, offset: int = 0) -> List[SearchMessageDTO]:
        """List messages by status with pagination."""
        query = select(PublicSearchMessage).where(PublicSearchMessage.status == status)\
            .order_by(PublicSearchMessage.created_at).offset(offset).limit(limit)
        result = await self._execute_query(query)
        messages = result.scalars().all()
        
        # Check if we got tuples instead of ORM objects
        message_dtos = []
        if messages and len(messages) > 0:
            if isinstance(messages[0], tuple):
                logger.info("Received tuples instead of ORM objects in list_messages_by_status")
                message_dtos = [self._tuple_to_message_dto(message) for message in messages]
            else:
                # Normal ORM object conversion
                message_dtos = [to_search_message_dto(message) for message in messages]
        
        return message_dtos

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
            error_message = str(e).lower()
            await self.db.rollback()
            
            # Handle pgBouncer prepared statement errors
            if ("prepared statement" in error_message or 
                "duplicatepreparedstatementerror" in error_message or 
                "invalidsqlstatementnameerror" in error_message):
                logger.warning(f"pgBouncer prepared statement error encountered: {str(e)}")
                try:
                    # Try to create a fresh session and retry
                    from sqlalchemy.ext.asyncio import AsyncSession
                    from core.database import async_engine
                    
                    logger.info("Creating fresh session to retry operation after pgBouncer error")
                    async with AsyncSession(async_engine) as fresh_session:
                        # Create a new instance with the fresh session
                        fresh_ops = SearchMessageOperations(fresh_session)
                        # Retry the operation
                        return await fresh_ops.create_message_with_commit(message_create_dto)
                except Exception as retry_error:
                    logger.error(f"Error in retry attempt after pgBouncer error: {str(retry_error)}")
                    raise DatabaseError(
                        "Failed to create message after retry",
                        details={"message_create_dto": str(message_create_dto)},
                        original_error=retry_error
                    )
            
            raise DatabaseError(
                "Failed to create message",
                details={"message_create_dto": str(message_create_dto)},
                original_error=e
            )

    async def get_messages_list_response(self, search_id: UUID, limit: int = 100, offset: int = 0, execution_options: Optional[Dict[str, Any]] = None) -> SearchMessageListDTO:
        """
        Get a paginated list of messages for a search with proper response formatting.
        
        This is a wrapper around list_messages_by_search that ensures proper formatting
        for API responses and handles pgBouncer compatibility options.
        """
        # Call the underlying list_messages_by_search method with execution options
        messages_list = await self.list_messages_by_search(
            search_id=search_id,
            limit=limit,
            offset=offset,
            execution_options=execution_options or self.execution_options
        )
        
        # Ensure the response has the correct format for the API
        if not hasattr(messages_list, 'offset'):
            messages_list.offset = offset
        if not hasattr(messages_list, 'limit'):
            messages_list.limit = limit
            
        return messages_list
