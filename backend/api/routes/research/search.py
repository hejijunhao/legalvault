# api/routes/research/search.py

from typing import List, Optional, Union
from uuid import UUID, uuid4
from fastapi import APIRouter, Depends, HTTPException, Query
import logging
from datetime import datetime

# Get logger for this module
logger = logging.getLogger(__name__)

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from core.database import get_db, async_session_factory
from core.auth import get_current_user, get_user_permissions
from models.database.user import User
from models.domain.research.search_operations import ResearchOperations
from services.workflow.research.search_workflow import ResearchSearchWorkflow, GPT4oMiniService, LLMService

# Import schemas for API responses
from models.schemas.research.search import (
    SearchCreate,
    SearchContinue,
    SearchResponse,
    SearchListResponse,
    SearchUpdate
)
from models.schemas.research.search_message import SearchMessageResponse

# Import DTOs
from models.dtos.research.search_dto import (
    SearchDTO, SearchListDTO, SearchCreateDTO, SearchUpdateDTO, SearchContinueDTO
)
from models.dtos.research.search_message_dto import (
    SearchMessageDTO, SearchMessageListDTO
)

# Import custom exceptions
from services.workflow.research.search_workflow import (
    SearchWorkflowError, QueryValidationError, QueryClarificationError,
    IrrelevantQueryError, PersistenceError
)

router = APIRouter(
    prefix="/research/searches",
    tags=["research"]
)

# Dependency to get research operations
def get_research_operations(db: AsyncSession = Depends(get_db)) -> ResearchOperations:
    """Get a ResearchOperations instance with database session."""
    logger.info("Creating ResearchOperations instance")
    return ResearchOperations(db)

# Dependency to get workflow service
def get_search_workflow(operations: ResearchOperations = Depends(get_research_operations)) -> ResearchSearchWorkflow:
    """Get a configured ResearchSearchWorkflow instance with injected operations."""
    logger.info("Creating ResearchSearchWorkflow instance")
    llm_service = GPT4oMiniService()
    return ResearchSearchWorkflow(llm_service, operations)

# Conversion functions for DTOs to API response models
def search_dto_to_response(search_dto: Union[SearchDTO, tuple]) -> SearchResponse:
    """Convert SearchDTO to SearchResponse for API layer."""
    logger.info("Converting SearchDTO to SearchResponse")
    # Handle case where search_dto is a tuple
    if isinstance(search_dto, tuple):
        logger.debug(f"Received tuple for conversion: {search_dto}")
        try:
            # Assuming tuple structure: (id, title, description, user_id, enterprise_id, is_featured, search_params, created_at, updated_at, tags)
            response = SearchResponse(
                id=search_dto[0] if search_dto[0] else uuid4(),
                query=search_dto[1],  # Title is used as query
                title=search_dto[1],
                description=search_dto[2],
                user_id=search_dto[3] if search_dto[3] else uuid4(),
                enterprise_id=search_dto[4],
                is_featured=search_dto[5] if len(search_dto) > 5 else False,
                search_params=search_dto[6] if len(search_dto) > 6 else {},
                created_at=search_dto[7] if len(search_dto) > 7 else datetime.now(),
                updated_at=search_dto[8] if len(search_dto) > 8 else datetime.now(),
                tags=search_dto[9] if len(search_dto) > 9 else [],
                messages=[],
                category=None,
                query_type=None
            )
            logger.info("Successfully converted tuple to SearchResponse")
            return response
        except Exception as e:
            logger.error(f"Error converting tuple to SearchResponse: {str(e)}")
            logger.debug(f"Tuple structure: {search_dto}")
            # Return a minimal valid response rather than failing
            response = SearchResponse(
                id=uuid4(),
                query="Error retrieving search data",  # Use error message as query
                title="Error retrieving search data",
                description="An error occurred while retrieving search data",
                user_id=uuid4(),
                enterprise_id=None,
                is_featured=False,
                search_params={},
                created_at=datetime.now(),
                updated_at=datetime.now(),
                messages=[],
                tags=[],
                category=None,
                query_type=None
            )
            logger.info("Returned minimal SearchResponse due to conversion error")
            return response
    
    # Convert messages to SearchMessageResponse objects
    messages = []
    if hasattr(search_dto, 'messages') and search_dto.messages:
        logger.debug(f"Converting {len(search_dto.messages)} messages")
        messages = [
            SearchMessageResponse(
                role=msg.role,
                content=msg.content,
                sequence=msg.sequence
            ) for msg in search_dto.messages
        ]
        logger.debug("Messages converted successfully")
    
    # Create SearchResponse from DTO
    response = SearchResponse(
        id=search_dto.id,
        query=search_dto.title,  # Use title as query for API response
        title=search_dto.title,
        description=search_dto.description,
        user_id=search_dto.user_id,
        enterprise_id=search_dto.enterprise_id,
        is_featured=search_dto.is_featured,
        tags=search_dto.tags,
        search_params=search_dto.search_params or {},
        created_at=search_dto.created_at,
        updated_at=search_dto.updated_at,
        messages=messages,
        category=getattr(search_dto, 'category', None),
        query_type=getattr(search_dto, 'query_type', None)
    )
    logger.info("Successfully converted SearchDTO to SearchResponse")
    return response

def search_list_dto_to_response(search_list_dto: Union[SearchListDTO, tuple]) -> SearchListResponse:
    """Convert SearchListDTO to SearchListResponse for API layer."""
    logger.info("Converting SearchListDTO to SearchListResponse")
    # Handle case where search_list_dto is a tuple
    if isinstance(search_list_dto, tuple):
        logger.debug(f"Received tuple in search_list_dto_to_response: {search_list_dto}")
        # Assuming tuple structure: (items, total, offset, limit)
        items_data = search_list_dto[0] if len(search_list_dto) > 0 else []
        total = search_list_dto[1] if len(search_list_dto) > 1 else 0
        offset = search_list_dto[2] if len(search_list_dto) > 2 else 0
        limit = search_list_dto[3] if len(search_list_dto) > 3 else 20
    else:
        # Handle items whether it's a method or a property
        if callable(getattr(search_list_dto, 'items', None)):
            items_data = search_list_dto.items()
        else:
            items_data = search_list_dto.items
        
        total = getattr(search_list_dto, 'total', 0)
        offset = getattr(search_list_dto, 'offset', 0)
        limit = getattr(search_list_dto, 'limit', 20)
    
    logger.debug(f"Converting {len(items_data)} search items")
    # Convert each item in items_data to a SearchResponse
    items = [search_dto_to_response(search_dto) for search_dto in items_data]
    
    response = SearchListResponse(
        items=items,
        total=total,
        offset=offset,
        limit=limit
    )
    logger.info("Successfully converted SearchListDTO to SearchListResponse")
    return response

@router.post("", response_model=SearchResponse)
async def create_search(
    data: SearchCreate,
    current_user: User = Depends(get_current_user),
    user_permissions: List[str] = Depends(get_user_permissions),
    workflow: ResearchSearchWorkflow = Depends(get_search_workflow)
):
    """
    Create a new legal research search.
    
    Initiates a new search using the Perplexity Sonar API with a legal lens,
    storing both the query and results for future reference.
    """
    logger.info(f"Received create_search request for user {current_user.id}")
    try:
        # Create DTO for workflow
        create_dto = SearchCreateDTO(
            user_id=current_user.id,
            query=data.query,
            enterprise_id=current_user.enterprise_id,
            search_params=data.search_params,
            title=data.title,
            description=data.description,
            tags=data.tags,
            is_featured=data.is_featured
        )
        logger.debug(f"Created SearchCreateDTO: {create_dto}")
        
        # Execute search using workflow - now handles persistence internally
        logger.info("Executing search workflow")
        result = await workflow.execute_search(create_dto)
        if not result or not result.metadata.get("search_id"):
            logger.error("Search workflow failed: No search_id returned")
            raise HTTPException(status_code=500, detail="Failed to create search")
        logger.info("Search workflow executed successfully")
            
        # Get created search and return response
        search_id = UUID(result.metadata["search_id"])
        logger.info(f"Retrieving created search with ID {search_id}")
        search_dto = await workflow.research_operations.get_search_by_id(
            search_id,
            execution_options={"no_parameters": True, "use_server_side_cursors": False}
        )
        
        # Handle database errors
        if not search_dto:
            logger.error(f"Failed to retrieve search {search_id} after creation")
            raise HTTPException(status_code=500, detail="Failed to retrieve created search")
        logger.info(f"Retrieved search {search_id} successfully")
        
        # Convert DTO to API response model
        response = search_dto_to_response(search_dto)
        logger.info(f"Returning create_search response for search {search_id}")
        return response
        
    except QueryValidationError as e:
        logger.error(f"QueryValidationError in create_search: {e.message}")
        raise HTTPException(status_code=400, detail=e.message)
    except QueryClarificationError as e:
        logger.error(f"QueryClarificationError in create_search: {e.message}")
        # Return a structured response with suggested clarifications
        raise HTTPException(
            status_code=400, 
            detail={
                "message": e.message,
                "suggested_clarifications": e.suggested_clarifications
            }
        )
    except IrrelevantQueryError as e:
        logger.error(f"IrrelevantQueryError in create_search: {e.message}")
        raise HTTPException(status_code=400, detail=e.message)
    except PersistenceError as e:
        logger.error(f"PersistenceError in create_search: {e.message}")
        raise HTTPException(status_code=500, detail=e.message)
    except SearchWorkflowError as e:
        logger.error(f"SearchWorkflowError in create_search: {e.message}")
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except Exception as e:
        logger.error(f"Unexpected error in create_search: {str(e)}")
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")

@router.post("/{search_id}/continue", response_model=SearchResponse)
async def continue_search(
    search_id: UUID,
    data: SearchContinue,
    workflow: ResearchSearchWorkflow = Depends(get_search_workflow),
    user: User = Depends(get_current_user)
) -> SearchResponse:
    """Continue an existing search with a follow-up query"""
    logger.info(f"Received continue_search request for search {search_id} by user {user.id}")
    # Verify search exists and user has access
    logger.info(f"Retrieving search {search_id} for verification")
    search = await workflow.research_operations.get_search_by_id(
        search_id,
        execution_options={"no_parameters": True, "use_server_side_cursors": False}
    )
    if not search:
        logger.error(f"Search {search_id} not found")
        raise HTTPException(status_code=404, detail="Search not found")
    logger.info(f"Search {search_id} found")
    if search.user_id != user.id:
        logger.error(f"User {user.id} not authorized for search {search_id}")
        raise HTTPException(status_code=403, detail="Not authorized to continue this search")
    logger.info(f"User {user.id} authorized for search {search_id}")
    
    try:
        # Create continue DTO for workflow
        continue_dto = SearchContinueDTO(
            search_id=search_id,
            user_id=user.id,
            follow_up_query=data.follow_up_query,
            enterprise_id=user.enterprise_id,
            thread_id=data.thread_id,
            previous_messages=data.previous_messages,
            search_params=data.search_params if hasattr(data, 'search_params') else {}
        )
        logger.debug(f"Created SearchContinueDTO: {continue_dto}")
        
        # Execute follow-up workflow
        logger.info("Executing follow-up workflow")
        result = await workflow.execute_follow_up(continue_dto)
        if not result or not result.get("search_id"):
            logger.error("Follow-up workflow failed: No search_id returned")
            raise HTTPException(status_code=500, detail="Failed to execute follow-up query")
        logger.info("Follow-up workflow executed successfully")
            
        # Get updated search and return response
        logger.info(f"Retrieving updated search {search_id}")
        updated_search = await workflow.research_operations.get_search_by_id(
            search_id,
            execution_options={"no_parameters": True, "use_server_side_cursors": False}
        )
        if not updated_search:
            logger.error(f"Updated search {search_id} not found")
            raise HTTPException(status_code=404, detail="Updated search not found")
        logger.info(f"Retrieved updated search {search_id} successfully")
            
        response = search_dto_to_response(updated_search)
        logger.info(f"Returning continue_search response for search {search_id}")
        return response
        
    except QueryValidationError as e:
        logger.error(f"QueryValidationError in continue_search: {e.message}")
        raise HTTPException(status_code=400, detail=e.message)
    except QueryClarificationError as e:
        logger.error(f"QueryClarificationError in continue_search: {e.message}")
        # Return a structured response with suggested clarifications
        raise HTTPException(
            status_code=400, 
            detail={
                "message": e.message,
                "suggested_clarifications": e.suggested_clarifications
            }
        )
    except IrrelevantQueryError as e:
        logger.error(f"IrrelevantQueryError in continue_search: {e.message}")
        raise HTTPException(status_code=400, detail=e.message)
    except PersistenceError as e:
        logger.error(f"PersistenceError in continue_search: {e.message}")
        raise HTTPException(status_code=500, detail=e.message)
    except SearchWorkflowError as e:
        logger.error(f"SearchWorkflowError in continue_search: {e.message}")
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except Exception as e:
        logger.error(f"Unexpected error in continue_search: {str(e)}")
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")

@router.get("/{search_id}", response_model=SearchResponse)
async def get_search(
    search_id: UUID,
    current_user: User = Depends(get_current_user),
    user_permissions: List[str] = Depends(get_user_permissions),
    operations: ResearchOperations = Depends(get_research_operations)
):
    """
    Get a specific search by ID.
    
    Retrieves the full details of a search, including all messages in the conversation.
    """
    logger.info(f"Request to get search {search_id} by user {current_user.id}")
    try:
        # Add execution_options for pgBouncer compatibility
        logger.info(f"Executing get_search_by_id for search {search_id}")
        search_result = await operations.get_search_by_id(
            search_id,
            execution_options={"no_parameters": True, "use_server_side_cursors": False}
        )
        logger.debug(f"Search result from operations: {search_result}")
        
        # Handle potential error dictionary from operations layer
        if isinstance(search_result, dict) and "error" in search_result:
            error_detail = search_result["error"]
            logger.error(f"Database error returned from operations for search {search_id}: {error_detail}")
            if "not found" in error_detail.lower():
                raise HTTPException(status_code=404, detail=error_detail)
            elif "database error" in error_detail.lower() or "connection failed" in error_detail.lower():
                raise HTTPException(status_code=503, detail="Database connection failed. Please try again later.")
            else:
                raise HTTPException(status_code=500, detail=f"Internal error retrieving search: {error_detail}")

        if not search_result:
            logger.warning(f"Search {search_id} not found after operations call.")
            raise HTTPException(status_code=404, detail="Search not found")
        logger.info(f"Search {search_id} retrieved successfully")
        
        # Verify ownership or permissions
        if str(search_result.user_id) != str(current_user.id) and "admin" not in user_permissions:
            logger.warning(f"User {current_user.id} unauthorized for search {search_result.user_id}")
            raise HTTPException(status_code=403, detail="Not authorized to access this search")
        logger.info(f"User {current_user.id} authorized for search {search_id}")
        
        # Convert DTO to API response model
        logger.info(f"Converting search {search_id} to response")
        response = search_dto_to_response(search_result)
        logger.info(f"Returning search {search_id} successfully for user {current_user.id}")
        return response
        
    except HTTPException as e:
        # Log HTTP exceptions specifically if they weren't caught above
        logger.error(f"HTTP exception during get_search for {search_id}: {e.status_code} - {e.detail}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error during get_search for {search_id}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"An unexpected error occurred while retrieving the search. Please try again later."
        )

@router.get("", response_model=SearchListResponse)
async def list_searches(
    limit: int = Query(20, ge=1, le=100, description="Maximum number of results"),
    offset: int = Query(0, ge=0, description="Pagination offset"),
    sort_by: str = Query("created_at", description="Field to sort by (created_at, updated_at, title)"),
    sort_order: str = Query("desc", description="Sort direction (asc or desc)"),
    current_user: User = Depends(get_current_user),
    user_permissions: List[str] = Depends(get_user_permissions),
    operations: ResearchOperations = Depends(get_research_operations)
):
    """
    List searches with optional filtering.
    
    Returns a list of searches created by the current user.
    Can be sorted by various fields.
    """
    logger.info(f"Received list_searches request for user {current_user.id} with limit={limit}, offset={offset}")
    # Get enterprise_id from user context
    logger.info(f"Retrieving enterprise_id for user {current_user.id}")
    enterprise_id = await get_user_enterprise(current_user, operations.db_session)
    logger.info(f"Enterprise_id for user {current_user.id}: {enterprise_id}")
    
    logger.info(f"Executing list_searches for user {current_user.id}")
    search_list_dto = await operations.list_searches(
        user_id=current_user.id,
        enterprise_id=enterprise_id,
        limit=limit,
        offset=offset,
        sort_by=sort_by,
        sort_order=sort_order
    )
    logger.info(f"Retrieved {search_list_dto.total if hasattr(search_list_dto, 'total') else 0} searches")
    
    # Convert DTO to API response model
    logger.info("Converting search list to response")
    response = search_list_dto_to_response(search_list_dto)
    logger.info("Returning list_searches response")
    return response

@router.patch("/{search_id}", response_model=SearchResponse)
async def update_search(
    search_id: UUID,
    data: SearchUpdate,
    current_user: User = Depends(get_current_user),
    user_permissions: List[str] = Depends(get_user_permissions),
    operations: ResearchOperations = Depends(get_research_operations)
):
    """
    Update search metadata.
    
    Updates the title, description, featured status, tags, category, and type of a search.
    """
    logger.info(f"Received update_search request for search {search_id} by user {current_user.id}")
    # Verify ownership of search
    logger.info(f"Retrieving search {search_id} for update verification")
    search_dto = await operations.get_search_by_id(
        search_id,
        execution_options={"no_parameters": True, "use_server_side_cursors": False}
    )
    if not search_dto or str(search_dto.user_id) != str(current_user.id):
        logger.error(f"Search {search_id} not found or user {current_user.id} unauthorized")
        raise HTTPException(status_code=404, detail="Search not found")
    logger.info(f"Search {search_id} found and user {current_user.id} authorized")
    
    # Create DTO from update data
    logger.debug(f"Creating SearchUpdateDTO for search {search_id}")
    update_data = data.model_dump(exclude_unset=True)
    update_dto = SearchUpdateDTO(**update_data)
    
    # Update search
    logger.info(f"Executing update_search for search {search_id}")
    updated_search_dto = await operations.update_search_metadata(
        search_id=search_id,
        updates=update_dto,
        execution_options={"no_parameters": True, "use_server_side_cursors": False}
    )
    
    if not updated_search_dto:
        logger.error(f"Update failed for search {search_id}")
        raise HTTPException(status_code=404, detail="Search not found or update failed")
    logger.info(f"Search {search_id} updated successfully")
    
    # Convert DTO to API response model
    logger.info(f"Converting updated search {search_id} to response")
    response = search_dto_to_response(updated_search_dto)
    logger.info(f"Returning update_search response for search {search_id}")
    return response

@router.delete("/{search_id}")
async def delete_search(
    search_id: UUID,
    current_user: User = Depends(get_current_user),
    user_permissions: List[str] = Depends(get_user_permissions),
    operations: ResearchOperations = Depends(get_research_operations)
):
    """
    Delete a search.
    
    Permanently removes a search and all its messages.
    """
    logger.info(f"Received delete_search request for search {search_id} by user {current_user.id}")
    # Verify ownership of search
    logger.info(f"Retrieving search {search_id} for deletion verification")
    search_dto = await operations.get_search_by_id(
        search_id,
        execution_options={"no_parameters": True, "use_server_side_cursors": False}
    )
    if not search_dto:
        logger.error(f"Search {search_id} not found")
        raise HTTPException(status_code=404, detail="Search not found")
    logger.info(f"Search {search_id} found")
    
    # Only allow deletion by owner or admin
    if str(search_dto.user_id) != str(current_user.id) and "admin" not in user_permissions:
        logger.error(f"User {current_user.id} unauthorized to delete search {search_id}")
        raise HTTPException(status_code=403, detail="Not authorized to delete this search")
    logger.info(f"User {current_user.id} authorized to delete search {search_id}")
    
    # Delete search
    logger.info(f"Executing delete_search for search {search_id}")
    success = await operations.delete_search(
        search_id,
        execution_options={"no_parameters": True, "use_server_side_cursors": False}
    )
    if not success:
        logger.error(f"Failed to delete search {search_id}")
        raise HTTPException(status_code=500, detail="Failed to delete search")
    logger.info(f"Search {search_id} deleted successfully")

# Helper function to get user's enterprise ID
async def get_user_enterprise(current_user: User, db: AsyncSession) -> Optional[UUID]:
    """
    Get the enterprise ID for a user.
    
    Args:
        current_user: User object
        db: SQLAlchemy async session
        
    Returns:
        UUID of the user's enterprise or None if user has no associated enterprise
    """
    logger.info(f"Retrieving enterprise_id for user {current_user.id}")
    # If the User object already has enterprise_id, return it directly
    if hasattr(current_user, 'enterprise_id') and current_user.enterprise_id:
        logger.info(f"Enterprise_id {current_user.enterprise_id} found in user object")
        return current_user.enterprise_id
    
    try:
        # If we don't have the enterprise_id yet, query the database
        logger.info(f"Querying database for enterprise_id of user {current_user.id}")
        query = select(User).where(User.id == current_user.id)
        # Add execution options for pgBouncer compatibility
        query = query.execution_options(no_parameters=True, use_server_side_cursors=False)
        result = await db.execute(query)
        user = result.scalars().first()
        
        if user and user.enterprise_id:
            logger.info(f"Enterprise_id {user.enterprise_id} retrieved from database")
            return user.enterprise_id
        logger.info(f"No enterprise_id found for user {current_user.id}")
    except Exception as e:
        error_message = str(e).lower()
        # Handle pgBouncer prepared statement errors
        if ("prepared statement" in error_message or 
            "duplicatepreparedstatementerror" in error_message or 
            "invalidsqlstatementnameerror" in error_message):
            logger.warning(f"pgBouncer error in get_user_enterprise: {e}")
            # Create a fresh session directly instead of using the dependency
            async with async_session_factory() as fresh_session:
                try:
                    # Retry the query with the fresh session
                    logger.info(f"Retrying enterprise_id query for user {current_user.id} with fresh session")
                    query = select(User).where(User.id == current_user.id)
                    query = query.execution_options(no_parameters=True, use_server_side_cursors=False)
                    result = await fresh_session.execute(query)
                    user = result.scalars().first()
                    
                    if user and user.enterprise_id:
                        logger.info(f"Retry successful: Enterprise_id {user.enterprise_id} retrieved")
                        return user.enterprise_id
                    logger.info(f"Retry found no enterprise_id for user {current_user.id}")
                except Exception as inner_e:
                    # Log the error but don't raise it to avoid breaking the application
                    logger.error(f"Error in get_user_enterprise retry: {inner_e}")
        else:
            # Log other errors
            logger.error(f"Error in get_user_enterprise: {e}")
    
    return None

