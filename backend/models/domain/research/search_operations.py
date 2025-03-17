# models/domain/research/search_operations.py

from typing import Dict, List, Optional, Any, Tuple
from uuid import UUID, uuid4
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete, func, update
from sqlalchemy.orm import selectinload

from models.database.research.public_searches import PublicSearch
from models.domain.research.search import ResearchSearch
from models.domain.research.search_message_operations import SearchMessageOperations
from models.database.research.public_search_messages import PublicSearchMessage

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
                           response: Optional[Dict] = None) -> Tuple[UUID, Dict[str, Any]]:
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
            Tuple of (search_id, search_data)
        """
        try:
            # Create domain model for validation
            search = ResearchSearch(title=query, description=None)
            
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
                msg_ops.create_message(
                    search_id=search_id,
                    role="user",
                    content={"text": query},
                    sequence=1
                )
                
                # Add assistant response as second message
                if "text" in response and "citations" in response:
                    msg_ops.create_message(
                        search_id=search_id,
                        role="assistant",
                        content=response,
                        sequence=2
                    )
            
            await self.db_session.commit()
            
            # Return the search data
            search_data = await self.get_search_by_id(search_id)
            return search_id, search_data
        except Exception as e:
            await self.db_session.rollback()
            return search_id, {"error": f"Database error: {str(e)}"}
    
    async def add_search_messages(self, search_id: UUID, user_query: str, response: Dict[str, Any]) -> bool:
        """
        Add user query and assistant response messages to an existing search.
        
        Args:
            search_id: UUID of the existing search
            user_query: Follow-up query from the user
            response: Response data from the search execution
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Get current highest sequence number
            query = select(func.max(PublicSearchMessage.sequence)).where(
                PublicSearchMessage.search_id == search_id
            )
            result = await self.db_session.execute(query)
            max_sequence = result.scalar() or 0
            
            # Add user query message
            msg_ops = SearchMessageOperations(self.db_session)
            msg_ops.create_message(
                search_id=search_id,
                role="user",
                content={"text": user_query},
                sequence=max_sequence + 1
            )
            
            # Add assistant response message
            if "text" in response and "citations" in response:
                msg_ops.create_message(
                    search_id=search_id,
                    role="assistant",
                    content=response,
                    sequence=max_sequence + 2
                )
            
            await self.db_session.commit()
            return True
        except Exception as e:
            await self.db_session.rollback()
            print(f"Error adding search messages: {str(e)}")
            return False
    
    async def get_search_by_id(self, search_id: UUID) -> Optional[Dict[str, Any]]:
        """
        Retrieve a search and its messages by ID.
        
        Args:
            search_id: UUID of the search
            
        Returns:
            Dictionary with search data and messages, or None if not found
        """
        try:
            query = select(PublicSearch).options(
                selectinload(PublicSearch.messages)
            ).where(PublicSearch.id == search_id)
            result = await self.db_session.execute(query)
            db_search = result.scalars().first()
            
            if not db_search:
                return None
            
            # Determine search status based on metadata or default to COMPLETED
            status = "completed"
            if db_search.search_params and "metadata" in db_search.search_params:
                metadata = db_search.search_params.get("metadata", {})
                if "query_analysis" in metadata:
                    query_analysis = metadata["query_analysis"]
                    if query_analysis.get("category") == "unclear":
                        status = "needs_clarification"
                    elif query_analysis.get("category") == "irrelevant":
                        status = "irrelevant_query"
            
            search_data = {
                "id": str(db_search.id),
                "title": db_search.title,
                "description": db_search.description,
                "user_id": str(db_search.user_id),
                "enterprise_id": str(db_search.enterprise_id) if db_search.enterprise_id else None,
                "is_featured": db_search.is_featured,
                "tags": db_search.tags,
                "search_params": db_search.search_params,
                "created_at": db_search.created_at,
                "updated_at": db_search.updated_at,
                "status": status,
                "messages": [
                    {
                        "role": msg.role,
                        "content": msg.content,
                        "sequence": msg.sequence
                    } for msg in sorted(db_search.messages, key=lambda m: m.sequence)
                ]
            }
            return search_data
        except Exception as e:
            print(f"Error retrieving search: {str(e)}")
            return None
    
    async def list_searches(
        self,
        user_id: Optional[UUID] = None,
        enterprise_id: Optional[UUID] = None,
        limit: int = 20,
        offset: int = 0,
        featured_only: bool = False
    ) -> Dict[str, Any]:
        """
        List searches with optional filtering.
        
        Args:
            user_id: Optional filter by user
            enterprise_id: Optional filter by enterprise
            limit: Maximum results to return
            offset: Pagination offset
            featured_only: Whether to only return featured searches
            
        Returns:
            Dictionary with items list and pagination metadata
        """
        try:
            # Build base query for data
            query = select(PublicSearch)
            
            # Build count query with same filters
            count_query = select(func.count()).select_from(PublicSearch)
            
            # Apply filters to both queries
            if user_id:
                query = query.where(PublicSearch.user_id == user_id)
                count_query = count_query.where(PublicSearch.user_id == user_id)
            if enterprise_id:
                query = query.where(PublicSearch.enterprise_id == enterprise_id)
                count_query = count_query.where(PublicSearch.enterprise_id == enterprise_id)
            if featured_only:
                query = query.where(PublicSearch.is_featured == True)
                count_query = count_query.where(PublicSearch.is_featured == True)
            
            # Apply pagination to data query only
            query = query.order_by(PublicSearch.updated_at.desc()).limit(limit).offset(offset)
            
            # Execute both queries
            result = await self.db_session.execute(query)
            count_result = await self.db_session.execute(count_query)
            
            db_searches = result.scalars().all()
            total_count = count_result.scalar() or 0
            
            # Format results
            items = [
                {
                    "id": str(db_search.id),
                    "title": db_search.title,
                    "description": db_search.description,
                    "user_id": str(db_search.user_id),
                    "enterprise_id": str(db_search.enterprise_id) if db_search.enterprise_id else None,
                    "is_featured": db_search.is_featured,
                    "tags": db_search.tags,
                    "created_at": db_search.created_at,
                    "updated_at": db_search.updated_at
                }
                for db_search in db_searches
            ]
            
            return {
                "items": items,
                "total": total_count,
                "offset": offset,
                "limit": limit
            }
        except Exception as e:
            print(f"Error listing searches: {str(e)}")
            return {
                "items": [],
                "total": 0,
                "offset": offset,
                "limit": limit
            }
    
    async def update_search_metadata(
        self, 
        search_id: UUID, 
        title: Optional[str] = None,
        description: Optional[str] = None,
        tags: Optional[List[str]] = None,
        is_featured: Optional[bool] = None
    ) -> bool:
        """
        Update search metadata fields.
        
        Args:
            search_id: UUID of the search to update
            title: Optional new title
            description: Optional new description
            tags: Optional new tags list
            is_featured: Optional featured status
            
        Returns:
            True if updated, False if not found
        """
        try:
            update_values = {}
            if title is not None:
                update_values["title"] = title
            if description is not None:
                update_values["description"] = description
            if tags is not None:
                update_values["tags"] = tags
            if is_featured is not None:
                update_values["is_featured"] = is_featured
            
            if not update_values:
                return True
            
            update_values["updated_at"] = datetime.utcnow()
            
            update_stmt = update(PublicSearch).where(PublicSearch.id == search_id).values(**update_values)
            result = await self.db_session.execute(update_stmt)
            await self.db_session.commit()
            return result.rowcount > 0
        except Exception as e:
            await self.db_session.rollback()
            return False
    
    async def delete_search(self, search_id: UUID) -> bool:
        """
        Delete a search and its messages.
        
        Args:
            search_id: UUID of the search
            
        Returns:
            True if deleted, False if not found
        """
        try:
            query = delete(PublicSearch).where(PublicSearch.id == search_id)
            result = await self.db_session.execute(query)
            await self.db_session.commit()
            return result.rowcount > 0
        except Exception as e:
            await self.db_session.rollback()
            return False
    
    async def get_search_status(self, search_id: UUID) -> Dict[str, Any]:
        """
        Get the current status of a search.
        
        Args:
            search_id: UUID of the search
            
        Returns:
            Dictionary with search status information
        """
        search_data = await self.get_search_by_id(search_id)
        if not search_data:
            return {"error": "Search not found"}
            
        # Extract status information from search data
        return {
            "id": search_data["id"],
            "status": search_data["status"],
            "created_at": search_data["created_at"],
            "updated_at": search_data["updated_at"],
            "message_count": len(search_data["messages"]) if "messages" in search_data else 0
        }