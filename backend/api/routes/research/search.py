# api/routes/research/search.py

from typing import List, Optional, Union
from uuid import UUID, uuid4
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from core.database import get_db
from core.auth import get_current_user, get_user_permissions
from models.database.user import User
from models.domain.research.search_operations import ResearchOperations
from services.workflow.research.search_workflow import ResearchSearchWorkflow, GPT4oMiniService, LLMService
from models.schemas.research.search import (
    SearchCreate,
    SearchContinue,
    SearchResponse,
    SearchListResponse,
    SearchUpdate,
    QueryStatus
)
from models.schemas.research.search_message import SearchMessageListResponse
from models.domain.research.search_message_operations import SearchMessageOperations

router = APIRouter(
    prefix="/research/searches",
    tags=["research"]
)

# Dependency to get workflow service
def get_search_workflow() -> ResearchSearchWorkflow:
    """Get a configured ResearchSearchWorkflow instance."""
    llm_service = GPT4oMiniService()
    return ResearchSearchWorkflow(llm_service)

# Dependency to get research operations
def get_research_operations(db: AsyncSession = Depends(get_db)) -> ResearchOperations:
    """Get a ResearchOperations instance with database session."""
    return ResearchOperations(db)

@router.post("/", response_model=SearchResponse)
async def create_search(
    data: SearchCreate,
    current_user: dict = Depends(get_current_user),
    user_permissions: List[str] = Depends(get_user_permissions),
    workflow: ResearchSearchWorkflow = Depends(get_search_workflow),
    operations: ResearchOperations = Depends(get_research_operations)
):
    """
    Create a new legal research search.
    
    Initiates a new search using the Perplexity Sonar API with a legal lens,
    storing both the query and results for future reference.
    """
    # Get enterprise_id from user context (implementation depends on your auth system)
    enterprise_id = await get_user_enterprise(current_user, operations.db_session)
    
    # Execute search using workflow
    response = await workflow.execute_search(
        user_id=current_user["id"],
        query=data.query,
        enterprise_id=enterprise_id,
        search_params=data.search_params
    )
    
    # Handle workflow errors
    if "error" in response:
        raise HTTPException(status_code=400, detail=response["error"])
    
    # Create search record in database
    search_id = uuid4()
    search_id, search_data = await operations.create_search_record(
        search_id=search_id,
        user_id=current_user["id"],
        query=data.query,
        enterprise_id=enterprise_id,
        search_params=data.search_params,
        response=response
    )
    
    # Handle database errors
    if "error" in search_data:
        raise HTTPException(status_code=500, detail=search_data["error"])
    
    # Return as Pydantic model
    return SearchResponse(**search_data)

@router.post("/{search_id}/continue", response_model=SearchResponse)
async def continue_search(
    search_id: UUID,
    data: SearchContinue,
    current_user: dict = Depends(get_current_user),
    user_permissions: List[str] = Depends(get_user_permissions),
    workflow: ResearchSearchWorkflow = Depends(get_search_workflow),
    operations: ResearchOperations = Depends(get_research_operations)
):
    """
    Continue an existing search with a follow-up query.
    
    Adds a follow-up question to an existing search thread, maintaining context
    from previous interactions.
    """
    # Verify search exists and user has access
    search_data = await operations.get_search_by_id(search_id)
    if not search_data:
        raise HTTPException(status_code=404, detail="Search not found")
    
    # Verify ownership or permissions
    if str(search_data["user_id"]) != str(current_user["id"]) and "admin" not in user_permissions:
        raise HTTPException(status_code=403, detail="Not authorized to access this search")
    
    # Get thread_id from last assistant message
    thread_id = None
    previous_messages = []
    if "messages" in search_data and search_data["messages"]:
        for msg in sorted(search_data["messages"], key=lambda m: m["sequence"], reverse=True):
            if msg["role"] == "assistant" and "content" in msg and "metadata" in msg["content"]:
                thread_id = msg["content"]["metadata"].get("thread_id")
                if thread_id:
                    break
        # Format messages for API
        previous_messages = [
            {"role": msg["role"], "content": msg["content"].get("text", "")} 
            for msg in sorted(search_data["messages"], key=lambda m: m["sequence"])
        ]
    
    # Execute follow-up using workflow
    response = await workflow.execute_follow_up(
        user_id=current_user["id"],
        enterprise_id=search_data.get("enterprise_id"),
        follow_up_query=data.follow_up_query,
        thread_id=thread_id,
        search_params=search_data.get("search_params"),
        previous_messages=previous_messages
    )
    
    # Handle workflow errors
    if "error" in response:
        raise HTTPException(status_code=400, detail=response["error"])
    
    # Add messages to search
    success = await operations.add_search_messages(
        search_id=search_id,
        user_query=data.follow_up_query,
        response=response
    )
    
    if not success:
        raise HTTPException(status_code=500, detail="Failed to save search messages")
    
    # Get updated search data
    updated_search = await operations.get_search_by_id(search_id)
    if not updated_search:
        raise HTTPException(status_code=404, detail="Search not found after update")
    
    # Return as Pydantic model
    return SearchResponse(**updated_search)

@router.get("/{search_id}", response_model=SearchResponse)
async def get_search(
    search_id: UUID,
    current_user: dict = Depends(get_current_user),
    user_permissions: List[str] = Depends(get_user_permissions),
    operations: ResearchOperations = Depends(get_research_operations)
):
    """
    Get a specific search by ID.
    
    Retrieves the full details of a search, including all messages in the conversation.
    """
    search_data = await operations.get_search_by_id(search_id)
    if not search_data:
        raise HTTPException(status_code=404, detail="Search not found")
    
    # Verify ownership or permissions
    if str(search_data["user_id"]) != str(current_user["id"]) and "admin" not in user_permissions:
        raise HTTPException(status_code=403, detail="Not authorized to access this search")
    
    return SearchResponse(**search_data)

@router.get("/{search_id}/messages", response_model=SearchMessageListResponse)
async def get_search_messages(
    search_id: UUID,
    limit: int = Query(100, ge=1, le=500, description="Maximum number of messages"),
    offset: int = Query(0, ge=0, description="Pagination offset"),
    current_user: dict = Depends(get_current_user),
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
    search = await search_ops.get_search_by_id(search_id)
    
    if not search or (str(search["user_id"]) != str(current_user["id"]) and "admin" not in user_permissions):
        raise HTTPException(status_code=403, detail="Not authorized to access this search")
    
    # Get messages with pagination
    message_ops = SearchMessageOperations(operations.db_session)
    return await message_ops.get_messages_list_response(search_id, limit, offset)

@router.get("/", response_model=SearchListResponse)
async def list_searches(
    featured_only: bool = Query(False, description="Only return featured searches"),
    status: Optional[QueryStatus] = Query(None, description="Filter by search status"),
    limit: int = Query(20, ge=1, le=100, description="Maximum number of results"),
    offset: int = Query(0, ge=0, description="Pagination offset"),
    current_user: dict = Depends(get_current_user),
    user_permissions: List[str] = Depends(get_user_permissions),
    operations: ResearchOperations = Depends(get_research_operations)
):
    """
    List searches with optional filtering.
    
    Returns a list of searches created by the current user. Can be filtered to show
    only featured searches or by status.
    """
    # Get enterprise_id from user context
    enterprise_id = await get_user_enterprise(current_user, operations.db_session)
    
    searches = await operations.list_searches(
        user_id=current_user["id"],
        enterprise_id=enterprise_id,
        limit=limit,
        offset=offset,
        featured_only=featured_only,
        status=status if status else None
    )
    
    return searches

@router.patch("/{search_id}", response_model=SearchResponse)
async def update_search(
    search_id: UUID,
    data: SearchUpdate,
    current_user: dict = Depends(get_current_user),
    user_permissions: List[str] = Depends(get_user_permissions),
    operations: ResearchOperations = Depends(get_research_operations)
):
    """
    Update search metadata.
    
    Updates the title, description, featured status, tags, category, type or status of a search.
    """
    # Verify ownership of search
    search = await operations.get_search_by_id(search_id)
    if not search or str(search["user_id"]) != str(current_user["id"]):
        raise HTTPException(status_code=404, detail="Search not found")
    
    # Update search
    update_data = data.model_dump(exclude_unset=True)
    success = await operations.update_search_metadata(
        search_id=search_id,
        **update_data
    )
    
    if not success:
        raise HTTPException(status_code=404, detail="Search not found or update failed")
    
    # Return updated search data
    return await operations.get_search_by_id(search_id)

@router.delete("/{search_id}", status_code=204)
async def delete_search(
    search_id: UUID,
    current_user: dict = Depends(get_current_user),
    user_permissions: List[str] = Depends(get_user_permissions),
    operations: ResearchOperations = Depends(get_research_operations)
):
    """
    Delete a search.
    
    Permanently removes a search and all its messages.
    """
    # Verify ownership of search
    search = await operations.get_search_by_id(search_id)
    if not search:
        raise HTTPException(status_code=404, detail="Search not found")
    
    # Only allow deletion by owner or admin
    if str(search["user_id"]) != str(current_user["id"]) and "admin" not in user_permissions:
        raise HTTPException(status_code=403, detail="Not authorized to delete this search")
    
    # Delete search
    success = await operations.delete_search(search_id)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to delete search")

# Helper function to get user's enterprise ID
async def get_user_enterprise(current_user: Union[dict, UUID], db: AsyncSession) -> Optional[UUID]:
    """
    Get the enterprise ID for a user.
    
    Args:
        current_user: Either a dictionary containing user data, or a UUID representing the user ID
        db: SQLAlchemy async session
        
    Returns:
        UUID of the user's enterprise or None if user has no associated enterprise
    """
    user_id = current_user["id"] if isinstance(current_user, dict) else current_user
    
    # Use SQLAlchemy ORM to query the user's enterprise_id
    stmt = select(User.enterprise_id).where(User.id == user_id)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()