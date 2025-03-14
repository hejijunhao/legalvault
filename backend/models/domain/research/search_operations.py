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
    
    async def create_search(self, user_id: UUID, query: str, 
                           enterprise_id: Optional[UUID] = None,
                           search_params: Optional[Dict] = None) -> Tuple[Optional[UUID], Dict[str, Any]]:
        """
        Create and execute a new search, persisting it and its messages.
        
        Args:
            user_id: UUID of the user initiating the search
            query: The search query
            enterprise_id: Optional UUID of the user's enterprise
            search_params: Optional parameters for the search
            
        Returns:
            Tuple of (search_id, search_response) or (None, error_response)
        """
        try:
            # Execute search using the domain model
            search_domain = ResearchSearch(user_id=user_id, enterprise_id=enterprise_id)
            response = await search_domain.start_search(query, search_params)
            
            # If search execution failed, return the error
            if "error" in response:
                return None, response
            
            # Create search record
            search_id = uuid4()
            db_search = PublicSearch(
                id=search_id,
                title=query[:255],
                user_id=user_id,
                enterprise_id=enterprise_id,
                search_params=search_params or {}
            )
            self.db_session.add(db_search)
        
            # Use SearchMessageOperations to create messages
            message_ops = SearchMessageOperations(self.db_session)
            message_ops.create_message(search_id, "user", {"text": query}, 0)
            message_ops.create_message(search_id, "assistant", response, 1)
        
            # Commit everything
            await self.db_session.commit()
            return search_id, response
        except Exception as e:
            await self.db_session.rollback()
            return None, {"error": f"Database error: {str(e)}"}
    
    async def continue_search(self, search_id: UUID, follow_up_query: str) -> Dict[str, Any]:
        """
        Continue an existing search with a follow-up query, persisting the result.
        
        Args:
            search_id: UUID of the existing search
            follow_up_query: Follow-up query from the user
            
        Returns:
            Search response or error dict
        """
        try:
            # Fetch search to get context
            query = select(PublicSearch).where(PublicSearch.id == search_id)
            result = await self.db_session.execute(query)
            db_search = result.scalars().first()
            if not db_search:
                return {"error": "Search not found"}
            
            # Get thread_id from last assistant message
            thread_query = select(PublicSearchMessage).where(
                PublicSearchMessage.search_id == search_id,
                PublicSearchMessage.role == "assistant"
            ).order_by(PublicSearchMessage.sequence.desc()).limit(1)
            thread_result = await self.db_session.execute(thread_query)
            last_msg = thread_result.scalars().first()
            thread_id = last_msg.content.get("thread_id") if last_msg else None
            
            # If thread_id is missing, log and handle gracefully
            if not thread_id:
                print(f"Warning: No thread_id found for search {search_id}, starting new conversation context")
            
            # Get next sequence
            seq_query = select(func.max(PublicSearchMessage.sequence)).where(
                PublicSearchMessage.search_id == search_id
            )
            seq_result = await self.db_session.execute(seq_query)
            next_seq = (seq_result.scalar() or -1) + 1
            
            # Execute follow-up using domain model
            search_domain = ResearchSearch(user_id=db_search.user_id, enterprise_id=db_search.enterprise_id)
            response = await search_domain.continue_search(follow_up_query, thread_id) if thread_id else \
                       await search_domain.start_search(follow_up_query, db_search.search_params)
            
            # If search execution failed, return the error
            if "error" in response:
                return response
            
            # Use SearchMessageOperations to create messages
            message_ops = SearchMessageOperations(self.db_session)
            message_ops.create_message(search_id, "user", {"text": follow_up_query}, next_seq)
            message_ops.create_message(search_id, "assistant", response, next_seq + 1)
            
            # Update timestamp
            db_search.updated_at = datetime.utcnow()
            await self.db_session.commit()
            return response
        except Exception as e:
            await self.db_session.rollback()
            return {"error": f"Database error: {str(e)}"}
    
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
            
            search_data = {
                "id": str(db_search.id),
                "title": db_search.title,
                "description": db_search.description,
                "user_id": str(db_search.user_id),
                "enterprise_id": str(db_search.enterprise_id),
                "is_featured": db_search.is_featured,
                "tags": db_search.tags,
                "search_params": db_search.search_params,
                "created_at": db_search.created_at.isoformat() if db_search.created_at else None,
                "updated_at": db_search.updated_at.isoformat() if db_search.updated_at else None,
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
                    "enterprise_id": str(db_search.enterprise_id),
                    "is_featured": db_search.is_featured,
                    "tags": db_search.tags,
                    "created_at": db_search.created_at.isoformat() if db_search.created_at else None,
                    "updated_at": db_search.updated_at.isoformat() if db_search.updated_at else None
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