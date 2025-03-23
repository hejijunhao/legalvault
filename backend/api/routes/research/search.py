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
    SearchUpdate,
    SearchMessageResponse
)
from models.schemas.research.search_message import (
    SearchMessageListResponse, 
    SearchMessageCreate, 
    SearchMessageUpdate,
    SearchMessageResponse,
    SearchMessageForwardRequest
)
from models.domain.research.search_message_operations import SearchMessageOperations

# Import DTOs
from models.dtos.research.search_dto import (
    SearchDTO, SearchListDTO, SearchCreateDTO, SearchUpdateDTO
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
    return ResearchOperations(db)

# Dependency to get workflow service
def get_search_workflow(operations: ResearchOperations = Depends(get_research_operations)) -> ResearchSearchWorkflow:
    """Get a configured ResearchSearchWorkflow instance with injected operations."""
    llm_service = GPT4oMiniService()
    return ResearchSearchWorkflow(llm_service, operations)

# Conversion functions for DTOs to API response models
def search_dto_to_response(search_dto: Union[SearchDTO, tuple]) -> SearchResponse:
    """Convert SearchDTO to SearchResponse for API layer."""
    # Handle case where search_dto is a tuple
    if isinstance(search_dto, tuple):
        try:
            # Assuming tuple structure: (id, title, description, user_id, enterprise_id, is_featured, search_params, created_at, updated_at, tags)
            return SearchResponse(
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
        except Exception as e:
            logger.error(f"Error converting tuple to SearchResponse: {str(e)}")
            logger.debug(f"Tuple structure: {search_dto}")
            # Return a minimal valid response rather than failing
            return SearchResponse(
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
    
    # Convert messages to SearchMessageResponse objects
    messages = []
    if hasattr(search_dto, 'messages') and search_dto.messages:
        messages = [
            SearchMessageResponse(
                role=msg.role,
                content=msg.content,
                sequence=msg.sequence
            ) for msg in search_dto.messages
        ]
    
    # Create SearchResponse from DTO
    return SearchResponse(
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

def search_list_dto_to_response(search_list_dto: Union[SearchListDTO, tuple]) -> SearchListResponse:
    """Convert SearchListDTO to SearchListResponse for API layer."""
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
    
    # Convert each item in items_data to a SearchResponse
    items = [search_dto_to_response(search_dto) for search_dto in items_data]
    
    return SearchListResponse(
        items=items,
        total=total,
        offset=offset,
        limit=limit
    )

def search_message_list_dto_to_response(message_list_dto: Union[SearchMessageListDTO, tuple]) -> SearchMessageListResponse:
    """Convert SearchMessageListDTO to SearchMessageListResponse for API layer."""
    # Handle case where message_list_dto is a tuple
    if isinstance(message_list_dto, tuple):
        logger.debug(f"Received tuple in search_message_list_dto_to_response: {message_list_dto}")
        # Assuming tuple structure: (items, total, offset, limit)
        items_data = message_list_dto[0] if len(message_list_dto) > 0 else []
        total = message_list_dto[1] if len(message_list_dto) > 1 else 0
        offset = message_list_dto[2] if len(message_list_dto) > 2 else 0
        limit = message_list_dto[3] if len(message_list_dto) > 3 else 20
    else:
        # Handle items whether it's a method or a property
        if callable(getattr(message_list_dto, 'items', None)):
            items_data = message_list_dto.items()
        else:
            items_data = message_list_dto.items
            
        total = getattr(message_list_dto, 'total', 0)
        offset = getattr(message_list_dto, 'offset', 0)
        limit = getattr(message_list_dto, 'limit', 20)
    
    items = []
    for msg_dto in items_data:
        # Handle case where msg_dto is a tuple
        if isinstance(msg_dto, tuple):
            # Adjust indices based on your actual query structure
            items.append(SearchMessageResponse(
                id=msg_dto[0] if len(msg_dto) > 0 else None,
                search_id=msg_dto[1] if len(msg_dto) > 1 else None,
                search_title=msg_dto[2] if len(msg_dto) > 2 else None,
                role=msg_dto[3] if len(msg_dto) > 3 else None,
                content=msg_dto[4] if len(msg_dto) > 4 else {},
                sequence=msg_dto[5] if len(msg_dto) > 5 else 0,
                created_at=msg_dto[6] if len(msg_dto) > 6 else datetime.now(),
                updated_at=msg_dto[7] if len(msg_dto) > 7 else datetime.now()
            ))
        else:
            items.append(SearchMessageResponse(
                id=getattr(msg_dto, 'id', None),
                search_id=getattr(msg_dto, 'search_id', None),
                search_title=getattr(msg_dto, 'search_title', None),
                role=getattr(msg_dto, 'role', None),
                content=getattr(msg_dto, 'content', {}),
                sequence=getattr(msg_dto, 'sequence', 0),
                created_at=getattr(msg_dto, 'created_at', datetime.now()),
                updated_at=getattr(msg_dto, 'updated_at', datetime.now())
            ))
    
    return SearchMessageListResponse(
        items=items,
        total=total,
        offset=offset,
        limit=limit
    )

@router.post("/", response_model=SearchResponse)
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
    # Get enterprise_id from user context (implementation depends on your auth system)
    enterprise_id = await get_user_enterprise(current_user, workflow.research_operations.db_session)
    
    try:
        # Execute search using workflow - now handles persistence internally
        result = await workflow.execute_search(
            user_id=current_user.id,
            query=data.query,
            enterprise_id=enterprise_id,
            search_params=data.search_params
        )
        
        # Get the search record from the database using the search_id from metadata
        search_id = UUID(result.metadata["search_id"]) if "search_id" in result.metadata else None
        
        if not search_id:
            raise HTTPException(status_code=500, detail="Search creation failed: no search_id returned")
        
        search_dto = await workflow.research_operations.get_search_by_id(search_id)
        
        # Handle database errors
        if not search_dto:
            raise HTTPException(status_code=500, detail="Failed to retrieve created search")
        
        # Convert DTO to API response model
        return search_dto_to_response(search_dto)
        
    except QueryValidationError as e:
        raise HTTPException(status_code=400, detail=e.message)
    except QueryClarificationError as e:
        # Return a structured response with suggested clarifications
        raise HTTPException(
            status_code=400, 
            detail={
                "message": e.message,
                "suggested_clarifications": e.suggested_clarifications
            }
        )
    except IrrelevantQueryError as e:
        raise HTTPException(status_code=400, detail=e.message)
    except PersistenceError as e:
        raise HTTPException(status_code=500, detail=e.message)
    except SearchWorkflowError as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except Exception as e:
        logger.error(f"Unexpected error in create_search: {str(e)}")
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")

@router.post("/{search_id}/continue", response_model=SearchResponse)
async def continue_search(
    search_id: UUID,
    data: SearchContinue,
    current_user: User = Depends(get_current_user),
    user_permissions: List[str] = Depends(get_user_permissions),
    workflow: ResearchSearchWorkflow = Depends(get_search_workflow)
):
    """
    Continue an existing search with a follow-up query.
    
    Adds a follow-up question to an existing search thread, maintaining context
    from previous interactions.
    """
    try:
        # Execute follow-up using workflow - now handles persistence internally
        result = await workflow.execute_follow_up(
            search_id=search_id,
            user_id=current_user.id,
            follow_up_query=data.follow_up_query,
            enterprise_id=data.enterprise_id,
            thread_id=data.thread_id,
            previous_messages=data.previous_messages
        )
        
        # Get updated search data
        updated_search_dto = await workflow.research_operations.get_search_by_id(search_id)
        if not updated_search_dto:
            raise HTTPException(status_code=404, detail="Search not found after update")
        
        # Convert DTO to API response model
        return search_dto_to_response(updated_search_dto)
        
    except QueryValidationError as e:
        raise HTTPException(status_code=400, detail=e.message)
    except QueryClarificationError as e:
        # Return a structured response with suggested clarifications
        raise HTTPException(
            status_code=400, 
            detail={
                "message": e.message,
                "suggested_clarifications": e.suggested_clarifications
            }
        )
    except IrrelevantQueryError as e:
        raise HTTPException(status_code=400, detail=e.message)
    except PersistenceError as e:
        raise HTTPException(status_code=500, detail=e.message)
    except SearchWorkflowError as e:
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
    try:
        # Add execution_options for pgBouncer compatibility
        search_result = await operations.get_search_by_id(
            search_id,
            execution_options={"no_parameters": True, "use_server_side_cursors": False}
        )
        
        # Check if we got an error dictionary instead of SearchDTO
        if isinstance(search_result, dict) and "error" in search_result:
            logger.error(f"Database error in get_search: {search_result['error']}")
            # If it's a "not found" error, return 404
            if "not found" in search_result["error"].lower():
                raise HTTPException(status_code=404, detail=search_result["error"])
            # For database errors, return 503
            if "database error" in search_result["error"].lower():
                raise HTTPException(
                    status_code=503, 
                    detail="Database connection failed. Please try again later."
                )
            # For other errors, return 500
            raise HTTPException(status_code=500, detail=search_result["error"])
            
        if not search_result:
            raise HTTPException(status_code=404, detail="Search not found")
        
        # Verify ownership or permissions
        if str(search_result.user_id) != str(current_user.id) and "admin" not in user_permissions:
            raise HTTPException(status_code=403, detail="Not authorized to access this search")
        
        # Convert DTO to API response model
        return search_dto_to_response(search_result)
        
    except HTTPException:
        # Re-raise HTTP exceptions as is
        raise
    except Exception as e:
        logger.error(f"Unexpected error in get_search: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="An unexpected error occurred. Please try again later."
        )

@router.get("/{search_id}/messages", response_model=SearchMessageListResponse)
async def get_search_messages(
    search_id: UUID,
    limit: int = Query(100, ge=1, le=500, description="Maximum number of messages"),
    offset: int = Query(0, ge=0, description="Pagination offset"),
    current_user: User = Depends(get_current_user),
    user_permissions: List[str] = Depends(get_user_permissions),
    operations: ResearchOperations = Depends(get_research_operations)
):
    """
    Get all messages for a specific search with pagination.
    
    This endpoint provides a convenient way to access messages directly from the search context.
    Returns messages in sequence order (oldest first).
    """
    # Verify user has access to the search
    search_ops = ResearchOperations(operations.db_session)
    search_dto = await search_ops.get_search_by_id(
        search_id,
        execution_options={"no_parameters": True, "use_server_side_cursors": False}
    )
    
    if not search_dto or (str(search_dto.user_id) != str(current_user.id) and "admin" not in user_permissions):
        raise HTTPException(status_code=403, detail="Not authorized to access this search")
    
    # Get messages with pagination
    message_ops = SearchMessageOperations(operations.db_session)
    message_list_dto = await message_ops.list_messages_by_search(
        search_id, 
        limit, 
        offset,
        execution_options={"no_parameters": True, "use_server_side_cursors": False}
    )
    
    # Convert DTO to API response model
    return search_message_list_dto_to_response(message_list_dto)

@router.get("/", response_model=SearchListResponse)
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
    # Get enterprise_id from user context
    enterprise_id = await get_user_enterprise(current_user, operations.db_session)
    
    search_list_dto = await operations.list_searches(
        user_id=current_user.id,
        enterprise_id=enterprise_id,
        limit=limit,
        offset=offset,
        sort_by=sort_by,
        sort_order=sort_order
    )
    
    # Convert DTO to API response model
    return search_list_dto_to_response(search_list_dto)

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
    # Verify ownership of search
    search_dto = await operations.get_search_by_id(
        search_id,
        execution_options={"no_parameters": True, "use_server_side_cursors": False}
    )
    if not search_dto or str(search_dto.user_id) != str(current_user.id):
        raise HTTPException(status_code=404, detail="Search not found")
    
    # Create DTO from update data
    update_data = data.model_dump(exclude_unset=True)
    update_dto = SearchUpdateDTO(**update_data)
    
    # Update search
    updated_search_dto = await operations.update_search_metadata(
        search_id=search_id,
        updates=update_dto,
        execution_options={"no_parameters": True, "use_server_side_cursors": False}
    )
    
    if not updated_search_dto:
        raise HTTPException(status_code=404, detail="Search not found or update failed")
    
    # Convert DTO to API response model
    return search_dto_to_response(updated_search_dto)

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
    # Verify ownership of search
    search_dto = await operations.get_search_by_id(
        search_id,
        execution_options={"no_parameters": True, "use_server_side_cursors": False}
    )
    if not search_dto:
        raise HTTPException(status_code=404, detail="Search not found")
    
    # Only allow deletion by owner or admin
    if str(search_dto.user_id) != str(current_user.id) and "admin" not in user_permissions:
        raise HTTPException(status_code=403, detail="Not authorized to delete this search")
    
    # Delete search
    success = await operations.delete_search(
        search_id,
        execution_options={"no_parameters": True, "use_server_side_cursors": False}
    )
    if not success:
        raise HTTPException(status_code=500, detail="Failed to delete search")

@router.post("/{search_id}/messages", response_model=SearchMessageResponse)
async def create_search_message(
    search_id: UUID,
    message: SearchMessageCreate,
    current_user: User = Depends(get_current_user),
    user_permissions: List[str] = Depends(get_user_permissions),
    operations: ResearchOperations = Depends(get_research_operations)
):
    """
    Create a new message for a search.
    
    This endpoint allows adding messages to an existing search conversation.
    """
    # Verify user has access to the search
    search_dto = await operations.get_search_by_id(
        search_id,
        execution_options={"no_parameters": True, "use_server_side_cursors": False}
    )
    
    if not search_dto or (str(search_dto.user_id) != str(current_user.id) and "admin" not in user_permissions):
        raise HTTPException(status_code=403, detail="Not authorized to access this search")
    
    # Create message
    message_ops = SearchMessageOperations(operations.db_session)
    
    # Create DTO from API model
    message_dto = SearchMessageCreateDTO(
        search_id=search_id,
        role=message.role,
        content=message.content,
        sequence=message.sequence if hasattr(message, 'sequence') else None,
        status=message.status if hasattr(message, 'status') else QueryStatus.PENDING
    )
    
    # Create the message
    created_message = await message_ops.create_message_with_commit(message_dto, execution_options={"no_parameters": True, "use_server_side_cursors": False})
    
    if not created_message:
        raise HTTPException(status_code=500, detail="Failed to create message")
    
    # Return the created message
    return search_message_dto_to_response(created_message)

@router.get("/{search_id}/messages/{message_id}", response_model=SearchMessageResponse)
async def get_search_message(
    search_id: UUID,
    message_id: UUID,
    current_user: User = Depends(get_current_user),
    user_permissions: List[str] = Depends(get_user_permissions),
    operations: ResearchOperations = Depends(get_research_operations)
):
    """
    Get a specific message from a search.
    
    This endpoint retrieves a single message by its ID within a search context.
    """
    # Verify user has access to the search
    search_dto = await operations.get_search_by_id(
        search_id,
        execution_options={"no_parameters": True, "use_server_side_cursors": False}
    )
    
    if not search_dto or (str(search_dto.user_id) != str(current_user.id) and "admin" not in user_permissions):
        raise HTTPException(status_code=403, detail="Not authorized to access this search")
    
    # Get the message
    message_ops = SearchMessageOperations(operations.db_session)
    message_dto = await message_ops.get_message_by_id(
        message_id,
        execution_options={"no_parameters": True, "use_server_side_cursors": False}
    )
    
    if not message_dto or str(message_dto.search_id) != str(search_id):
        raise HTTPException(status_code=404, detail="Message not found")
    
    # Return the message
    return search_message_dto_to_response(message_dto)

@router.patch("/{search_id}/messages/{message_id}", response_model=SearchMessageResponse)
async def update_search_message(
    search_id: UUID,
    message_id: UUID,
    message_update: SearchMessageUpdate,
    current_user: User = Depends(get_current_user),
    user_permissions: List[str] = Depends(get_user_permissions),
    operations: ResearchOperations = Depends(get_research_operations)
):
    """
    Update a message in a search.
    
    This endpoint allows updating the content or status of a message.
    """
    # Verify user has access to the search
    search_dto = await operations.get_search_by_id(
        search_id,
        execution_options={"no_parameters": True, "use_server_side_cursors": False}
    )
    
    if not search_dto or (str(search_dto.user_id) != str(current_user.id) and "admin" not in user_permissions):
        raise HTTPException(status_code=403, detail="Not authorized to access this search")
    
    # Get the message to verify it belongs to this search
    message_ops = SearchMessageOperations(operations.db_session)
    message_dto = await message_ops.get_message_by_id(
        message_id,
        execution_options={"no_parameters": True, "use_server_side_cursors": False}
    )
    
    if not message_dto or str(message_dto.search_id) != str(search_id):
        raise HTTPException(status_code=404, detail="Message not found")
    
    # Update the message
    update_data = message_update.model_dump(exclude_unset=True)
    
    # Create update DTO
    update_dto = SearchMessageUpdateDTO(**update_data)
    
    updated_message = await message_ops.update_message(
        message_id, 
        update_dto,
        execution_options={"no_parameters": True, "use_server_side_cursors": False}
    )
    
    if not updated_message:
        raise HTTPException(status_code=500, detail="Failed to update message")
    
    # Return the updated message
    return search_message_dto_to_response(updated_message)

@router.delete("/{search_id}/messages/{message_id}")
async def delete_search_message(
    search_id: UUID,
    message_id: UUID,
    current_user: User = Depends(get_current_user),
    user_permissions: List[str] = Depends(get_user_permissions),
    operations: ResearchOperations = Depends(get_research_operations)
):
    """
    Delete a message from a search.
    
    This endpoint permanently removes a message from a search conversation.
    """
    # Verify user has access to the search
    search_dto = await operations.get_search_by_id(
        search_id,
        execution_options={"no_parameters": True, "use_server_side_cursors": False}
    )
    
    if not search_dto or (str(search_dto.user_id) != str(current_user.id) and "admin" not in user_permissions):
        raise HTTPException(status_code=403, detail="Not authorized to access this search")
    
    # Get the message to verify it belongs to this search
    message_ops = SearchMessageOperations(operations.db_session)
    message_dto = await message_ops.get_message_by_id(
        message_id,
        execution_options={"no_parameters": True, "use_server_side_cursors": False}
    )
    
    if not message_dto or str(message_dto.search_id) != str(search_id):
        raise HTTPException(status_code=404, detail="Message not found")
    
    # Delete the message
    success = await message_ops.delete_message(
        message_id,
        execution_options={"no_parameters": True, "use_server_side_cursors": False}
    )
    
    if not success:
        raise HTTPException(status_code=500, detail="Failed to delete message")
    
    return {"message": "Message deleted successfully"}

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
    # If the User object already has enterprise_id, return it directly
    if hasattr(current_user, 'enterprise_id') and current_user.enterprise_id:
        return current_user.enterprise_id
    
    try:
        # If we don't have the enterprise_id yet, query the database
        query = select(User).where(User.id == current_user.id)
        # Add execution options for pgBouncer compatibility
        query = query.execution_options(no_parameters=True, use_server_side_cursors=False)
        result = await db.execute(query)
        user = result.scalars().first()
        
        if user and user.enterprise_id:
            return user.enterprise_id
    except Exception as e:
        error_message = str(e).lower()
        # Handle pgBouncer prepared statement errors
        if ("prepared statement" in error_message or 
            "duplicatepreparedstatementerror" in error_message or 
            "invalidsqlstatementnameerror" in error_message):
            # Create a fresh session directly instead of using the dependency
            async with async_session_factory() as fresh_session:
                try:
                    # Retry the query with the fresh session
                    query = select(User).where(User.id == current_user.id)
                    query = query.execution_options(no_parameters=True, use_server_side_cursors=False)
                    result = await fresh_session.execute(query)
                    user = result.scalars().first()
                    
                    if user and user.enterprise_id:
                        return user.enterprise_id
                except Exception as inner_e:
                    # Log the error but don't raise it to avoid breaking the application
                    logger.error(f"Error in get_user_enterprise retry: {inner_e}")
        else:
            # Log other errors
            logger.error(f"Error in get_user_enterprise: {e}")
    
    return None