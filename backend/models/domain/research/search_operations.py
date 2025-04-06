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

# Import error classes
from models.domain.research.research_errors import ValidationError, DatabaseError

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
    
    async def _execute_query(self, query, execution_options: Optional[Dict[str, Any]] = None):
        """
        Execute a query with pgBouncer compatibility settings.
        
        Args:
            query: SQLAlchemy query to execute
            execution_options: Optional execution options for pgBouncer compatibility
            
        Returns:
            Query result
            
        Raises:
            DatabaseError: If query execution fails
        """
        # Maximum number of retry attempts for pgBouncer errors
        max_retries = 2
        retry_count = 0
        last_error = None
        
        while retry_count <= max_retries:
            try:
                # Apply pgBouncer compatibility options
                _execution_options = execution_options or self.execution_options
                
                # Log the query execution attempt
                if retry_count > 0:
                    logger.info(f"Retry attempt {retry_count}/{max_retries} for query execution")
                
                result = await self.db_session.execute(
                    query.execution_options(**_execution_options)
                )
                return result
                
            except Exception as e:
                last_error = e
                error_message = str(e).lower()
                await self.db_session.rollback()
                
                # Check if this is a pgBouncer prepared statement error
                is_pgbouncer_error = any(err_type in error_message for err_type in [
                    "prepared statement", 
                    "duplicatepreparedstatementerror",
                    "invalidsqlstatementnameerror",
                    "stmtcacheerror"
                ])
                
                if is_pgbouncer_error and retry_count < max_retries:
                    logger.warning(f"pgBouncer prepared statement error encountered (attempt {retry_count+1}/{max_retries+1}): {str(e)}")
                    retry_count += 1
                    
                    # Use a fresh session for the retry
                    try:
                        from sqlalchemy.ext.asyncio import AsyncSession
                        from core.database import async_engine
                        
                        # Close the current session
                        await self.db_session.close()
                        
                        # Create a fresh session with enhanced pgBouncer compatibility
                        logger.info("Creating fresh session for retry after pgBouncer error")
                        self.db_session = AsyncSession(async_engine)
                        
                        # Add a small delay before retry to allow connection pool to stabilize
                        import asyncio
                        await asyncio.sleep(0.1 * (2 ** retry_count))  # Exponential backoff
                        
                        continue  # Try again with the new session
                    except Exception as session_error:
                        logger.error(f"Error creating fresh session: {str(session_error)}")
                        # Fall through to the general error handling
                else:
                    # Not a pgBouncer error or we've exhausted retries
                    break
        
        # If we get here, all retries failed or it wasn't a pgBouncer error
        if last_error:
            logger.error(f"Query execution failed after {retry_count} retries: {str(last_error)}")
            
            # Provide a more specific error message for pgBouncer issues
            if "prepared statement" in str(last_error).lower():
                raise DatabaseError(
                    "Database connection pool error",
                    details={
                        "error": str(last_error),
                        "suggestion": "The application is experiencing issues with the database connection pool. This is typically a transient error that resolves automatically."
                    },
                    original_error=last_error
                )
            else:
                raise DatabaseError(
                    "Query execution failed",
                    details={"error": str(last_error)},
                    original_error=last_error
                )

    async def create_search_record(
            self,
            search_id: UUID,
            user_id: UUID,
            query: str,
            enterprise_id: Optional[UUID] = None,
            search_params: Optional[Dict] = None,
            response: Optional[Dict] = None,
            execution_options: Optional[Dict[str, Any]] = None
        ) -> SearchDTO:
        """
        Create a new search record in the database.
        
        Args:
            search_id: UUID for the new search
            user_id: UUID of the user initiating the search
            query: The search query
            enterprise_id: Optional UUID of the user's enterprise
            search_params: Optional parameters for the search
            response: Optional response data from the search execution
            execution_options: Optional execution options for pgBouncer compatibility
            
        Returns:
            SearchDTO with created search data
            
        Raises:
            DatabaseError: If database operation fails
            ValidationError: If input validation fails
        """
        try:
            # Create domain model for validation
            search = ResearchSearch(
                title=query[:500],  # Use first 50 chars as title
                description=query,
                user_id=user_id,
                enterprise_id=enterprise_id
            )
            
            # Create database model
            db_search = PublicSearch(
                id=search_id,
                title=search.title,
                description=search.description,
                user_id=user_id,
                enterprise_id=enterprise_id,
                search_params=search_params or {},
                tags=[],
                is_featured=False
            )
            
            try:
                # Apply execution options if provided, otherwise use default
                _execution_options = execution_options or self.execution_options
                
                # Add and commit the search with pgBouncer compatibility settings
                self.db_session.add(db_search)
                await self.db_session.commit()
                await self.db_session.refresh(db_search)
                
                # If response provided, add initial messages
                if response:
                    try:
                        # Create message operations
                        msg_ops = SearchMessageOperations(self.db_session)
                        
                        # Add user query message
                        await msg_ops.create_message(
                            search_id=search_id,
                            content={"text": query},
                            role="user",
                            sequence=1,
                            execution_options=_execution_options
                        )
                        
                        # Add assistant response message
                        await msg_ops.create_message(
                            search_id=search_id,
                            content=response,
                            role="assistant",
                            sequence=2,
                            execution_options=_execution_options
                        )
                        
                        # Refresh search to get messages
                        await self.db_session.refresh(db_search)
                        
                    except Exception as msg_error:
                        logger.error(f"Error creating initial messages: {str(msg_error)}")
                        # Don't fail the whole operation if message creation fails
                        # Just log and continue
                        
                return to_search_dto(db_search)
                
            except Exception as e:
                await self.db_session.rollback()
                raise DatabaseError(
                    "Failed to create search record",
                    details={
                        "search_id": str(search_id),
                        "user_id": str(user_id)
                    },
                    original_error=e
                )
                
        except ValidationError:
            raise
        except DatabaseError:
            raise
        except Exception as e:
            raise DatabaseError(
                "Unexpected error creating search",
                details={
                    "search_id": str(search_id),
                    "user_id": str(user_id)
                },
                original_error=e
            )

    async def add_search_messages(self, search_id: UUID, user_query: str, response: Dict[str, Any], execution_options: Optional[Dict[str, Any]] = None) -> bool:
        """
        Add user query and assistant response messages to an existing search.
        
        Args:
            search_id: UUID of the existing search
            user_query: Follow-up query from the user
            response: Response data from the search execution
            execution_options: Optional execution options for pgBouncer compatibility
            
        Returns:
            True if messages were added successfully
            
        Raises:
            DatabaseError: If database operation fails
            ValidationError: If search not found or validation fails
        """
        try:
            # First validate the search exists
            query = select(PublicSearch).where(PublicSearch.id == search_id)
            result = await self._execute_query(query, execution_options)
            search = result.scalars().first()
            
            if not search:
                raise ValidationError(
                    "Search not found",
                    details={"search_id": str(search_id)}
                )
            
            # Validate the query
            temp_search = ResearchSearch(title=user_query)
            if not temp_search.validate_query(user_query):
                raise ValidationError(
                    "Invalid query",
                    details={
                        "reason": "Query must be at least 3 characters",
                        "query": user_query
                    }
                )
            
            try:
                # Create message operations
                msg_ops = SearchMessageOperations(self.db_session)
                
                # Add user query message
                next_sequence = await msg_ops.get_next_sequence(search_id, execution_options)
                await msg_ops.create_message(
                    search_id=search_id,
                    role="user",
                    content={"text": user_query},
                    sequence=next_sequence,
                    execution_options=execution_options
                )
                
                # Add assistant response if valid
                if "text" in response and "citations" in response:
                    assistant_seq = await msg_ops.get_next_sequence(search_id, execution_options)
                    await msg_ops.create_message(
                        search_id=search_id,
                        role="assistant",
                        content=response,
                        sequence=assistant_seq,
                        execution_options=execution_options
                    )
                else:
                    raise ValidationError(
                        "Invalid response format",
                        details={
                            "required_fields": ["text", "citations"],
                            "provided_fields": list(response.keys())
                        }
                    )
                
                await self.db_session.commit()
                return True
                
            except Exception as e:
                await self.db_session.rollback()
                raise DatabaseError(
                    "Failed to add search messages",
                    details={
                        "search_id": str(search_id),
                        "has_response": bool(response)
                    },
                    original_error=e
                )
                
        except ValidationError:
            raise
        except DatabaseError:
            raise
        except Exception as e:
            raise DatabaseError(
                "Unexpected error adding search messages",
                details={"search_id": str(search_id)},
                original_error=e
            )

    async def get_search_by_id(
            self,
            search_id: UUID,
            include_messages: bool = True,
            execution_options: Optional[Dict[str, Any]] = None
        ) -> SearchDTO:
        """
        Get a search by its ID, optionally including messages.
        
        Args:
            search_id: UUID of the search to retrieve
            include_messages: Whether to include messages in the response
            execution_options: Optional execution options for pgBouncer compatibility
            
        Returns:
            SearchDTO with search data and optionally messages
            
        Raises:
            DatabaseError: If database operation fails
            ValidationError: If search not found
        """
        try:
            # Build query based on whether messages should be included
            if include_messages:
                query = select(PublicSearch).options(
                    selectinload(PublicSearch.messages)
                ).where(PublicSearch.id == search_id)
            else:
                query = select(PublicSearch).where(PublicSearch.id == search_id)
                
            # Execute query using helper method that handles pgBouncer errors
            result = await self._execute_query(query, execution_options)
                    
            search = result.scalars().first()
            if not search:
                raise ValidationError(
                    "Search not found",
                    details={"search_id": str(search_id)}
                )
            
            # Convert to DTO based on whether messages were included
            if include_messages:
                return to_search_dto(search)
            else:
                return to_search_dto_without_messages(search)
                    
        except ValidationError:
            raise
        except DatabaseError:
            raise
        except Exception as e:
            raise DatabaseError(
                "Unexpected error retrieving search",
                details={"search_id": str(search_id)},
                original_error=e
            )

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

    async def update_search_metadata(self, search_id: UUID, updates: SearchUpdateDTO, execution_options: Optional[Dict[str, Any]] = None) -> SearchDTO:
        """
        Update search metadata like title, description, tags, etc.
        
        Args:
            search_id: UUID of the search to update
            updates: SearchUpdateDTO with fields to update
            execution_options: Optional execution options for pgBouncer compatibility
            
        Returns:
            Updated SearchDTO
            
        Raises:
            DatabaseError: If database operation fails
            ValidationError: If updates are invalid
        """
        try:
            # First get the existing search
            query = select(PublicSearch).where(PublicSearch.id == search_id)
            if execution_options:
                result = await self.db_session.execute(
                    query.execution_options(**execution_options)
                )
            else:
                result = await self._execute_query(query)
                
            db_search = result.scalars().first()
            if not db_search:
                raise ValidationError(
                    "Search not found",
                    details={"search_id": str(search_id)}
                )
            
            # Create domain model for validation
            search = ResearchSearch(
                title=db_search.title,
                description=db_search.description,
                user_id=db_search.user_id,
                enterprise_id=db_search.enterprise_id
            )
            
            # Validate updates
            search.validate_updates(updates.dict(exclude_unset=True))
            
            try:
                # Apply updates
                for field, value in updates.dict(exclude_unset=True).items():
                    setattr(db_search, field, value)
                
                await self.db_session.commit()
                await self.db_session.refresh(db_search)
                
                return to_search_dto(db_search)
                
            except Exception as e:
                await self.db_session.rollback()
                raise DatabaseError(
                    "Failed to update search metadata",
                    details={
                        "search_id": str(search_id),
                        "updates": updates.dict(exclude_unset=True)
                    },
                    original_error=e
                )
                
        except ValidationError:
            raise
        except DatabaseError:
            raise
        except Exception as e:
            raise DatabaseError(
                "Unexpected error updating search metadata",
                details={"search_id": str(search_id)},
                original_error=e
            )

    async def delete_search(self, search_id: UUID, execution_options: Optional[Dict[str, Any]] = None) -> bool:
        """
        Delete a search and all its associated messages.
        
        Args:
            search_id: UUID of the search to delete
            execution_options: Optional execution options for pgBouncer compatibility
            
        Returns:
            True if deletion was successful
            
        Raises:
            DatabaseError: If deletion fails
            ValidationError: If search not found
        """
        try:
            # First verify search exists
            query = select(PublicSearch).where(PublicSearch.id == search_id)
            if execution_options:
                result = await self.db_session.execute(
                    query.execution_options(**execution_options)
                )
            else:
                result = await self._execute_query(query)
                
            if not result.scalars().first():
                raise ValidationError(
                    "Search not found",
                    details={"search_id": str(search_id)}
                )
            
            try:
                # Delete associated messages first
                messages_query = delete(PublicSearchMessage).where(
                    PublicSearchMessage.search_id == search_id
                )
                
                if execution_options:
                    await self.db_session.execute(
                        messages_query.execution_options(**execution_options)
                    )
                else:
                    await self._execute_query(messages_query)
                
                # Then delete the search
                search_query = delete(PublicSearch).where(
                    PublicSearch.id == search_id
                )
                
                if execution_options:
                    await self.db_session.execute(
                        search_query.execution_options(**execution_options)
                    )
                else:
                    await self._execute_query(search_query)
                
                await self.db_session.commit()
                return True
                
            except Exception as e:
                await self.db_session.rollback()
                raise DatabaseError(
                    "Failed to delete search and messages",
                    details={"search_id": str(search_id)},
                    original_error=e
                )
                
        except ValidationError:
            raise
        except DatabaseError:
            raise
        except Exception as e:
            raise DatabaseError(
                "Unexpected error deleting search",
                details={"search_id": str(search_id)},
                original_error=e
            )
    
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