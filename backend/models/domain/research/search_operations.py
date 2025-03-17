# models/domain/research/search_operations.py

from typing import Dict, List, Optional, Any, Union
from uuid import UUID
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete, func, update, desc, asc
from sqlalchemy.orm import selectinload

from models.database.research.public_searches import PublicSearch
from models.domain.research.search import ResearchSearch, QueryStatus
from models.database.research.public_search_messages import PublicSearchMessage
from models.domain.research.search_message_operations import SearchMessageOperations

# Import DTOs
from models.dtos.research.search_dto import (
    SearchDTO, SearchListDTO, SearchStatusDTO, SearchCreateDTO, SearchUpdateDTO,
    to_search_dto, to_search_list_dto, to_search_status_dto, to_search_dto_without_messages
)
from models.dtos.research.search_message_dto import SearchMessageDTO

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
            await self.db_session.rollback()
            print(f"Error creating search record: {str(e)}")
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
            search_dto = await self.get_search_by_id(search_id)
            if not search_dto:
                return {"error": f"Search with ID {search_id} not found"}
                
            # Validate the query using domain logic
            temp_search = ResearchSearch(title=user_query)
            if not temp_search.validate_query(user_query):
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
            await self.db_session.rollback()
            print(f"Error adding search messages: {str(e)}")
            return {"error": str(e)}
    
    async def get_search_by_id(self, search_id: UUID) -> Union[SearchDTO, Dict[str, Any]]:
        """
        Retrieve a search and its messages by ID.
        
        Args:
            search_id: UUID of the search
            
        Returns:
            SearchDTO with search data and messages, or error dict if not found
        """
        try:
            query = select(PublicSearch).options(
                selectinload(PublicSearch.messages)
            ).where(PublicSearch.id == search_id)
            result = await self.db_session.execute(query)
            db_search = result.scalars().first()
            
            if not db_search:
                return {"error": f"Search with ID {search_id} not found"}
            
            # Convert to DTO using the conversion function
            return to_search_dto(db_search)
        except Exception as e:
            print(f"Error retrieving search: {str(e)}")
            return {"error": str(e)}

    async def list_searches(
        self,
        user_id: Optional[UUID] = None,
        enterprise_id: Optional[UUID] = None,
        offset: int = 0,
        limit: int = 20,
        sort_by: str = "created_at",
        sort_order: str = "desc",
        status: Optional[str] = None
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
            status: Optional filter by status value
            
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
            
            if status:
                query = query.where(PublicSearch.status == status)
                count_query = count_query.where(PublicSearch.status == status)
            
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
            result = await self.db_session.execute(query)
            count_result = await self.db_session.execute(count_query)
            
            searches = result.scalars().all()
            total_count = count_result.scalar()
            
            # Convert to DTOs
            search_dtos = [to_search_dto_without_messages(search) for search in searches]
            
            return SearchListDTO(
                items=search_dtos,
                total=total_count,
                offset=offset,
                limit=limit
            )
        except Exception as e:
            print(f"Error listing searches: {str(e)}")
            return {"error": str(e)}

    async def update_search_metadata(self, search_id: UUID, updates: SearchUpdateDTO) -> Union[SearchDTO, Dict[str, Any]]:
        """
        Update search metadata like title, description, tags, etc.
        
        Args:
            search_id: UUID of the search to update
            updates: SearchUpdateDTO with fields to update
            
        Returns:
            Updated SearchDTO if successful, error dict otherwise
        """
        try:
            query = select(PublicSearch).where(PublicSearch.id == search_id)
            result = await self.db_session.execute(query)
            db_search = result.scalars().first()
            
            if not db_search:
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
            await self.db_session.rollback()
            print(f"Error updating search metadata: {str(e)}")
            return {"error": str(e)}

    async def delete_search(self, search_id: UUID) -> Union[bool, Dict[str, Any]]:
        """
        Delete a search and all its messages.
        
        Args:
            search_id: UUID of the search to delete
            
        Returns:
            True if successful, error dict otherwise
        """
        try:
            # First check if the search exists
            check_query = select(PublicSearch).where(PublicSearch.id == search_id)
            check_result = await self.db_session.execute(check_query)
            if not check_result.scalars().first():
                return {"error": f"Search with ID {search_id} not found"}
            
            # Delete messages first (cascade would handle this, but being explicit)
            msg_delete = delete(PublicSearchMessage).where(PublicSearchMessage.search_id == search_id)
            await self.db_session.execute(msg_delete)
            
            # Delete the search
            search_delete = delete(PublicSearch).where(PublicSearch.id == search_id)
            result = await self.db_session.execute(search_delete)
            
            await self.db_session.commit()
            return True
        except Exception as e:
            await self.db_session.rollback()
            print(f"Error deleting search: {str(e)}")
            return {"error": str(e)}
    
    async def get_search_status(self, search_id: UUID) -> Union[SearchStatusDTO, Dict[str, Any]]:
        """
        Get the current status of a search.
        
        Args:
            search_id: UUID of the search
            
        Returns:
            SearchStatusDTO with status information, or error dict if not found
        """
        try:
            query = select(PublicSearch).where(PublicSearch.id == search_id)
            result = await self.db_session.execute(query)
            db_search = result.scalars().first()
            
            if not db_search:
                return {"error": f"Search with ID {search_id} not found"}
            
            # Convert to DTO using the conversion function
            return to_search_status_dto(db_search)
        except Exception as e:
            print(f"Error retrieving search status: {str(e)}")
            return {"error": str(e)}

    async def update_search_status(self, search_id: UUID, status: QueryStatus) -> Union[SearchStatusDTO, Dict[str, Any]]:
        """
        Update the status of a search.
        
        Args:
            search_id: UUID of the search
            status: New status value from QueryStatus enum
            
        Returns:
            SearchStatusDTO with updated status, or error dict if not found
        """
        try:
            # First get the search to check if it exists
            query = select(PublicSearch).where(PublicSearch.id == search_id)
            result = await self.db_session.execute(query)
            db_search = result.scalars().first()
            
            if not db_search:
                return {"error": f"Search with ID {search_id} not found"}
            
            # Create domain model and update status
            search = ResearchSearch(
                title=db_search.title,
                description=db_search.description,
                user_id=db_search.user_id,
                enterprise_id=db_search.enterprise_id
            )
            search.update_status(status)
            
            # Update database record
            db_search.status = status.value
            db_search.updated_at = datetime.utcnow()
            
            await self.db_session.commit()
            await self.db_session.refresh(db_search)
            
            # Return updated status
            return to_search_status_dto(db_search)
        except Exception as e:
            await self.db_session.rollback()
            print(f"Error updating search status: {str(e)}")
            return {"error": str(e)}