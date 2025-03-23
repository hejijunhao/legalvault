# models/domain/research/search_operations.py

from uuid import UUID
from typing import Dict, List, Optional, Any, Union
from datetime import datetime
import logging

from sqlalchemy import select, desc, asc, func, delete, text
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

# Import domain models
from models.domain.research.search import ResearchSearch
from models.database.research.public_searches import PublicSearch
from models.database.research.public_search_messages import PublicSearchMessage
from models.domain.research.search_message_operations import SearchMessageOperations

# Import DTOs and conversion functions
from models.dtos.research.search_dto import (
    SearchDTO, SearchListDTO, SearchCreateDTO, SearchUpdateDTO,
    to_search_dto, to_search_list_dto, to_search_dto_without_messages
)
from models.dtos.research.search_message_dto import (
    SearchMessageDTO, to_search_message_dto
)

logger = logging.getLogger(__name__)

class ResearchOperations:
    """
    Operations for managing research searches in the database.
    Handles persistence and retrieval for ResearchSearch domain model outputs.
    """
    
    def __init__(self, db_session: AsyncSession):
        """
        Initialize with a database session.
        
        Args:
            db_session: SQLAlchemy async session for database operations
        """
        self.db_session = db_session
        # Set pgBouncer compatibility options for all operations
        self.execution_options = {
            "no_parameters": True,
            "use_server_side_cursors": False
        }
    
    async def _execute_query(self, query):
        """Execute a query with pgBouncer compatibility settings."""
        try:
            # Apply pgBouncer compatibility options
            result = await self.db_session.execute(
                query.execution_options(**self.execution_options)
            )
            return result
        except Exception as e:
            logger.error(f"Error executing query: {str(e)}")
            raise
    
    async def create_search_record(self, search_id: UUID, user_id: UUID, query: str, 
                           enterprise_id: Optional[UUID] = None,
                           search_params: Optional[Dict] = None,
                           response: Optional[Dict] = None) -> Union[SearchDTO, Dict[str, Any]]:
        """
        Create a new search record in the database.
        
        Args:
            search_id: UUID for the new search
            user_id: UUID of the user initiating the search
            query: The search query
            enterprise_id: Optional UUID of the user's enterprise
            search_params: Optional parameters for the search
            response: Optional response data from the search execution
            
        Returns:
            SearchDTO if successful, error dict otherwise
        """
        try:
            # Create domain model for validation
            search = ResearchSearch(
                title=query,
                description=None,
                user_id=user_id,
                enterprise_id=enterprise_id
            )
            
            # Validate the query using domain logic
            if not search.validate_query(query):
                logger.error("Invalid query. Query must be at least 3 characters.")
                return {"error": "Invalid query. Query must be at least 3 characters."}
            
            # Create database record
            db_search = PublicSearch(
                id=search_id,
                title=search.title,
                description=search.description,
                user_id=user_id,
                enterprise_id=enterprise_id,
                search_params=search_params
            )
            
            # Add with pgBouncer compatibility options
            await self._execute_query(text("SELECT 1"))
            self.db_session.add(db_search)
            
            # If we have a response, create message records
            if response:
                # Add user query as first message
                msg_ops = SearchMessageOperations(self.db_session)
                
                # Get next sequence numbers using the centralized method
                user_msg_seq = await msg_ops.get_next_sequence(search_id)
                
                msg_ops.create_message(
                    search_id=search_id,
                    role="user",
                    content={"text": query},
                    sequence=user_msg_seq
                )
                
                # Add assistant response as second message
                if "text" in response and "citations" in response:
                    assistant_msg_seq = await msg_ops.get_next_sequence(search_id)
                    msg_ops.create_message(
                        search_id=search_id,
                        role="assistant",
                        content=response,
                        sequence=assistant_msg_seq
                    )
            
            await self.db_session.commit()
            
            # Return the created search with all data
            return await self.get_search_by_id(search_id)
        except Exception as e:
            error_message = str(e).lower()
            await self.db_session.rollback()
            
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
                        fresh_ops = ResearchOperations(fresh_session)
                        # Retry the operation
                        return await fresh_ops.create_search_record(
                            search_id, user_id, query, enterprise_id, search_params, response
                        )
                except Exception as retry_error:
                    logger.error(f"Error in retry attempt after pgBouncer error: {str(retry_error)}")
                    return {"error": f"Database error: {str(retry_error)}"}
            
            logger.error(f"Error creating search record: {str(e)}")
            return {"error": str(e)}

    async def add_search_messages(self, search_id: UUID, user_query: str, response: Dict[str, Any]) -> Union[bool, Dict[str, Any]]:
        """
        Add user query and assistant response messages to an existing search.
        
        Args:
            search_id: UUID of the existing search
            user_query: Follow-up query from the user
            response: Response data from the search execution
            
        Returns:
            True if successful, error dict otherwise
        """
        try:
            # First validate the search exists
            query = select(PublicSearch).where(PublicSearch.id == search_id)
            result = await self._execute_query(query)
            db_search = result.scalars().first()
            
            if not db_search:
                logger.error(f"Search with ID {search_id} not found")
                return {"error": f"Search with ID {search_id} not found"}
                
            # Validate the query using domain logic
            temp_search = ResearchSearch(title=user_query)
            if not temp_search.validate_query(user_query):
                logger.error("Invalid query. Query must be at least 3 characters.")
                return {"error": "Invalid query. Query must be at least 3 characters."}
            
            # Create message operations
            msg_ops = SearchMessageOperations(self.db_session)
            
            # Get next sequence number using the centralized method
            next_sequence = await msg_ops.get_next_sequence(search_id)
            
            # Add user query message
            msg_ops.create_message(
                search_id=search_id,
                role="user",
                content={"text": user_query},
                sequence=next_sequence
            )
            
            # Add assistant response message
            if "text" in response and "citations" in response:
                assistant_seq = await msg_ops.get_next_sequence(search_id)
                msg_ops.create_message(
                    search_id=search_id,
                    role="assistant",
                    content=response,
                    sequence=assistant_seq
                )
            
            await self.db_session.commit()
            return True
        except Exception as e:
            error_message = str(e).lower()
            await self.db_session.rollback()
            
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
                        fresh_ops = ResearchOperations(fresh_session)
                        # Retry the operation
                        return await fresh_ops.add_search_messages(search_id, user_query, response)
                except Exception as retry_error:
                    logger.error(f"Error in retry attempt after pgBouncer error: {str(retry_error)}")
                    return {"error": f"Database error: {str(retry_error)}"}
            
            logger.error(f"Error adding search messages: {str(e)}")
            return {"error": str(e)}
    
    async def get_search_by_id(self, search_id: UUID, execution_options: Optional[Dict[str, Any]] = None) -> Union[SearchDTO, Dict[str, Any]]:
        """
        Retrieve a search and its messages by ID.
        
        Args:
            search_id: UUID of the search
            execution_options: Optional execution options for pgBouncer compatibility
            
        Returns:
            SearchDTO with search data and messages, or error dict if not found
        """
        try:
            # Add pgBouncer compatibility options
            query = select(PublicSearch).options(
                selectinload(PublicSearch.messages)
            ).where(PublicSearch.id == search_id)
            
            # Use provided execution_options if given, otherwise use default
            if execution_options:
                result = await self.db_session.execute(
                    query.execution_options(**execution_options)
                )
            else:
                result = await self._execute_query(query)
                
            db_search = result.scalars().first()
            
            if not db_search:
                logger.error(f"Search with ID {search_id} not found")
                return {"error": f"Search with ID {search_id} not found", "user_id": None}
            
            # Check if we got a tuple instead of an ORM object
            if isinstance(db_search, tuple):
                logger.info("Received tuple instead of ORM object in get_search_by_id")
                search_dto = self._tuple_to_search_dto(db_search)
                
                # Load messages separately for tuple case
                msg_query = select(PublicSearchMessage).where(
                    PublicSearchMessage.search_id == search_id
                ).order_by(PublicSearchMessage.sequence)
                msg_result = await self._execute_query(msg_query)
                messages = msg_result.scalars().all()
                
                # Convert messages to DTOs, handling both tuple and ORM cases
                if messages:
                    message_dtos = []
                    for msg in messages:
                        if isinstance(msg, tuple):
                            msg_ops = SearchMessageOperations(self.db_session)
                            message_dtos.append(msg_ops._tuple_to_message_dto(msg))
                        else:
                            message_dtos.append(to_search_message_dto(msg))
                    search_dto.messages = message_dtos
                
                return search_dto
            else:
                # Convert search and its messages to DTOs
                search_dto = to_search_dto(db_search)
                if db_search.messages:
                    search_dto.messages = [to_search_message_dto(msg) for msg in db_search.messages]
                return search_dto

        except Exception as e:
            error_message = str(e).lower()
            await self.db_session.rollback()
            
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
                        fresh_ops = ResearchOperations(fresh_session)
                        # Retry the operation
                        return await fresh_ops.get_search_by_id(search_id, execution_options)
                except Exception as retry_error:
                    logger.error(f"Error in retry attempt after pgBouncer error: {str(retry_error)}")
                    return {"error": f"Database error: {str(retry_error)}", "user_id": None}
            
            logger.error(f"Error retrieving search: {str(e)}")
            return {"error": str(e), "user_id": None}

    async def list_searches(
        self,
        user_id: Optional[UUID] = None,
        enterprise_id: Optional[UUID] = None,
        offset: int = 0,
        limit: int = 20,
        sort_by: str = "created_at",
        sort_order: str = "desc",
        execution_options: Optional[Dict[str, Any]] = None
    ) -> Union[SearchListDTO, Dict[str, Any]]:
        """
        List searches with pagination and filtering.
        
        Args:
            user_id: Optional filter by user ID
            enterprise_id: Optional filter by enterprise ID
            offset: Pagination offset
            limit: Maximum items to return
            sort_by: Field to sort by
            sort_order: Sort direction ('asc' or 'desc')
            execution_options: Optional execution options for pgBouncer compatibility
            
        Returns:
            SearchListDTO with paginated results, or error dict on failure
        """
        try:
            # Build base query
            query = select(PublicSearch)
            count_query = select(func.count(PublicSearch.id))
            
            # Apply filters
            if user_id:
                query = query.where(PublicSearch.user_id == user_id)
                count_query = count_query.where(PublicSearch.user_id == user_id)
                
            if enterprise_id:
                query = query.where(PublicSearch.enterprise_id == enterprise_id)
                count_query = count_query.where(PublicSearch.enterprise_id == enterprise_id)
            
            # Apply sorting
            if sort_by not in ["created_at", "updated_at", "title"]:
                sort_by = "created_at"  # Default to created_at if invalid field
                
            if sort_order.lower() not in ["asc", "desc"]:
                sort_order = "desc"  # Default to descending if invalid order
                
            sort_column = getattr(PublicSearch, sort_by)
            if sort_order.lower() == "desc":
                query = query.order_by(desc(sort_column))
            else:
                query = query.order_by(asc(sort_column))
            
            # Apply pagination
            query = query.offset(offset).limit(limit)
            
            # Execute queries
            if execution_options:
                result = await self.db_session.execute(
                    query.execution_options(**execution_options)
                )
                count_result = await self.db_session.execute(
                    count_query.execution_options(**execution_options)
                )
            else:
                result = await self._execute_query(query)
                count_result = await self._execute_query(count_query)
            
            searches = result.scalars().all()
            total_count = count_result.scalar()
            
            # Convert to DTOs
            search_dtos = []
            if searches:
                for search in searches:
                    if isinstance(search, tuple):
                        logger.info("Received tuple instead of ORM object in list_searches")
                        search_dtos.append(self._tuple_to_search_dto(search))
                    else:
                        search_dtos.append(to_search_dto_without_messages(search))
            
            return SearchListDTO(
                items=search_dtos,
                total=total_count,
                offset=offset,
                limit=limit
            )
        except Exception as e:
            error_message = str(e).lower()
            await self.db_session.rollback()
            
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
                        fresh_ops = ResearchOperations(fresh_session)
                        # Retry the operation
                        return await fresh_ops.list_searches(
                            user_id, enterprise_id, offset, limit, sort_by, sort_order, execution_options
                        )
                except Exception as retry_error:
                    logger.error(f"Error in retry attempt after pgBouncer error: {str(retry_error)}")
                    return {"error": f"Database error: {str(retry_error)}"}
            
            logger.error(f"Error listing searches: {str(e)}")
            return {"error": str(e)}

    async def update_search_metadata(self, search_id: UUID, updates: SearchUpdateDTO, execution_options: Optional[Dict[str, Any]] = None) -> Union[SearchDTO, Dict[str, Any]]:
        """
        Update search metadata like title, description, tags, etc.
        
        Args:
            search_id: UUID of the search to update
            updates: SearchUpdateDTO with fields to update
            execution_options: Optional execution options for pgBouncer compatibility
            
        Returns:
            Updated SearchDTO if successful, error dict otherwise
        """
        try:
            query = select(PublicSearch).where(PublicSearch.id == search_id)
            
            # Use provided execution_options if given, otherwise use default
            if execution_options:
                result = await self.db_session.execute(
                    query.execution_options(**execution_options)
                )
            else:
                result = await self._execute_query(query)
                
            db_search = result.scalars().first()
            
            if not db_search:
                logger.error(f"Search with ID {search_id} not found")
                return {"error": f"Search with ID {search_id} not found"}
            
            # Convert DTO to dict and check if there are any updates
            updates_dict = updates.dict(exclude_unset=True)
            if not updates_dict:
                # No updates provided, return current state without database operation
                return to_search_dto(db_search)
                
            # Validate title if it's being updated
            if "title" in updates_dict:
                temp_search = ResearchSearch(title=updates_dict["title"])
                # Validation happens in the constructor
                
            # Update fields
            for key, value in updates_dict.items():
                if hasattr(db_search, key):
                    setattr(db_search, key, value)
            
            # Update the updated_at timestamp
            db_search.updated_at = datetime.utcnow()
            
            await self.db_session.commit()
            await self.db_session.refresh(db_search)
            
            # Return updated search as DTO
            return to_search_dto(db_search)
        except Exception as e:
            error_message = str(e).lower()
            await self.db_session.rollback()
            
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
                        fresh_ops = ResearchOperations(fresh_session)
                        # Retry the operation
                        return await fresh_ops.update_search_metadata(search_id, updates, execution_options)
                except Exception as retry_error:
                    logger.error(f"Error in retry attempt after pgBouncer error: {str(retry_error)}")
                    return {"error": f"Database error: {str(retry_error)}"}
            
            logger.error(f"Error updating search metadata: {str(e)}")
            return {"error": str(e)}

    async def delete_search(self, search_id: UUID, execution_options: Optional[Dict[str, Any]] = None) -> Union[bool, Dict[str, Any]]:
        """
        Delete a search and all its messages.
        
        Args:
            search_id: UUID of the search to delete
            execution_options: Optional execution options for pgBouncer compatibility
            
        Returns:
            True if successful, error dict otherwise
        """
        try:
            # First check if the search exists
            check_query = select(PublicSearch).where(PublicSearch.id == search_id)
            
            # Use provided execution_options if given, otherwise use default
            if execution_options:
                check_result = await self.db_session.execute(
                    check_query.execution_options(**execution_options)
                )
            else:
                check_result = await self._execute_query(check_query)
                
            if not check_result.scalars().first():
                logger.error(f"Search with ID {search_id} not found")
                return {"error": f"Search with ID {search_id} not found"}
            
            # Delete messages first (cascade would handle this, but being explicit)
            msg_delete = delete(PublicSearchMessage).where(PublicSearchMessage.search_id == search_id)
            
            # Use provided execution_options if given, otherwise use default
            if execution_options:
                await self.db_session.execute(
                    msg_delete.execution_options(**execution_options)
                )
            else:
                await self._execute_query(msg_delete)
            
            # Delete the search
            search_delete = delete(PublicSearch).where(PublicSearch.id == search_id)
            
            # Use provided execution_options if given, otherwise use default
            if execution_options:
                result = await self.db_session.execute(
                    search_delete.execution_options(**execution_options)
                )
            else:
                result = await self._execute_query(search_delete)
            
            await self.db_session.commit()
            return True
        except Exception as e:
            error_message = str(e).lower()
            await self.db_session.rollback()
            
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
                        fresh_ops = ResearchOperations(fresh_session)
                        # Retry the operation
                        return await fresh_ops.delete_search(search_id, execution_options)
                except Exception as retry_error:
                    logger.error(f"Error in retry attempt after pgBouncer error: {str(retry_error)}")
                    return {"error": f"Database error: {str(retry_error)}"}
            
            logger.error(f"Error deleting search: {str(e)}")
            return {"error": str(e)}
    
    def _tuple_to_search_dto(self, search_tuple: tuple) -> SearchDTO:
        """
        Convert a database tuple to a SearchDTO.
        
        Args:
            search_tuple: Tuple from database query
            
        Returns:
            SearchDTO with data from tuple
        """
        try:
            # Extract fields from tuple
            id = search_tuple[0] if len(search_tuple) > 0 else None
            title = search_tuple[1] if len(search_tuple) > 1 else ""
            description = search_tuple[2] if len(search_tuple) > 2 else None
            user_id = search_tuple[3] if len(search_tuple) > 3 else None
            enterprise_id = search_tuple[4] if len(search_tuple) > 4 else None
            created_at = search_tuple[6] if len(search_tuple) > 6 else datetime.now()
            updated_at = search_tuple[7] if len(search_tuple) > 7 else datetime.now()
            search_params = search_tuple[8] if len(search_tuple) > 8 else {}
            tags = search_tuple[9] if len(search_tuple) > 9 else []
            is_featured = search_tuple[10] if len(search_tuple) > 10 else False
            
            return SearchDTO(
                id=id,
                title=title,
                description=description,
                user_id=user_id,
                enterprise_id=enterprise_id,
                created_at=created_at,
                updated_at=updated_at,
                search_params=search_params or {},
                tags=tags or [],
                is_featured=is_featured or False,
                messages=[]
            )
        except Exception as e:
            logger.error(f"Error converting tuple to SearchDTO: {str(e)}")
            return {
                "error": f"Failed to convert search tuple: {str(e)}",
                "status": "error",
                "data": None
            }