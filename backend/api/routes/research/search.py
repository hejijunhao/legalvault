# api/routes/research/search.py

from typing import List, Optional, Union
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db
from core.auth import get_current_user, get_user_permissions
from models.database.user import User
from models.domain.research.search_operations import ResearchOperations
from models.schemas.research.search import (
    SearchCreate,
    SearchContinue,
    SearchResponse,
    SearchListResponse,
    SearchUpdate
)

router = APIRouter(
    prefix="/research/searches",
    tags=["research"]
)

@router.post("/", response_model=SearchResponse)
async def create_search(
    data: SearchCreate,
    current_user: dict = Depends(get_current_user),
    user_permissions: List[str] = Depends(get_user_permissions),
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new legal research search.
    
    Initiates a new search using the Perplexity Sonar API with a legal lens,
    storing both the query and results for future reference.
    """
    # Get enterprise_id from user context (implementation depends on your auth system)
    enterprise_id = await get_user_enterprise(current_user, db)
    
    operations = ResearchOperations(db)
    search_id, response = await operations.create_search(
        user_id=current_user["id"],
        enterprise_id=enterprise_id,
        query=data.query,
        search_params=data.search_params
    )
    
    # Check for errors
    if not search_id or "error" in response:
        error_message = response.get("error", "Failed to create search")
        raise HTTPException(status_code=500, detail=error_message)
    
    # Return the full search with messages
    search_data = await operations.get_search_by_id(search_id)
    if not search_data:
        raise HTTPException(status_code=500, detail="Search created but failed to retrieve details")
    
    return search_data

@router.post("/{search_id}/continue", response_model=SearchResponse)
async def continue_search(
    search_id: UUID,
    data: SearchContinue,
    current_user: dict = Depends(get_current_user),
    user_permissions: List[str] = Depends(get_user_permissions),
    db: AsyncSession = Depends(get_db)
):
    """
    Continue an existing search with a follow-up query.
    
    Adds a follow-up question to an existing search thread, maintaining context
    from previous interactions.
    """
    operations = ResearchOperations(db)
    
    # Verify ownership of search
    search = await operations.get_search_by_id(search_id)
    if not search or str(search["user_id"]) != str(current_user["id"]):
        raise HTTPException(status_code=404, detail="Search not found")
    
    # Process follow-up
    response = await operations.continue_search(
        search_id=search_id,
        follow_up_query=data.follow_up_query
    )
    
    # Check for errors
    if "error" in response:
        error_message = response.get("error", "Failed to continue search")
        raise HTTPException(status_code=500, detail=error_message)
    
    # Return updated search
    updated_search = await operations.get_search_by_id(search_id)
    if not updated_search:
        raise HTTPException(status_code=500, detail="Failed to retrieve updated search")
    
    return updated_search

@router.get("/{search_id}", response_model=SearchResponse)
async def get_search(
    search_id: UUID,
    current_user: dict = Depends(get_current_user),
    user_permissions: List[str] = Depends(get_user_permissions),
    db: AsyncSession = Depends(get_db)
):
    """
    Get a specific search by ID.
    
    Retrieves the full details of a search, including all messages in the conversation.
    """
    operations = ResearchOperations(db)
    search = await operations.get_search_by_id(search_id)
    
    if not search:
        raise HTTPException(status_code=404, detail="Search not found")
    
    # Check if user has access to this search
    if str(search["user_id"]) != str(current_user["id"]) and "admin" not in user_permissions:
        raise HTTPException(status_code=403, detail="Not authorized to access this search")
    
    return search

@router.get("/", response_model=SearchListResponse)
async def list_searches(
    featured_only: bool = Query(False, description="Only return featured searches"),
    limit: int = Query(20, ge=1, le=100, description="Maximum number of results"),
    offset: int = Query(0, ge=0, description="Pagination offset"),
    current_user: dict = Depends(get_current_user),
    user_permissions: List[str] = Depends(get_user_permissions),
    db: AsyncSession = Depends(get_db)
):
    """
    List searches with optional filtering.
    
    Returns a list of searches created by the current user. Can be filtered to show
    only featured searches.
    """
    # Get enterprise_id from user context
    enterprise_id = await get_user_enterprise(current_user, db)
    
    operations = ResearchOperations(db)
    searches = await operations.list_searches(
        user_id=current_user["id"],
        enterprise_id=enterprise_id,
        limit=limit,
        offset=offset,
        featured_only=featured_only
    )
    
    return searches

@router.patch("/{search_id}", response_model=SearchResponse)
async def update_search(
    search_id: UUID,
    data: SearchUpdate,
    current_user: dict = Depends(get_current_user),
    user_permissions: List[str] = Depends(get_user_permissions),
    db: AsyncSession = Depends(get_db)
):
    """
    Update search metadata.
    
    Updates the title, description, featured status, or tags of a search.
    """
    operations = ResearchOperations(db)
    
    # Verify ownership of search
    search = await operations.get_search_by_id(search_id)
    if not search or str(search["user_id"]) != str(current_user["id"]):
        raise HTTPException(status_code=404, detail="Search not found")
    
    # Update search
    success = await operations.update_search_metadata(
        search_id=search_id,
        title=data.title,
        description=data.description,
        tags=data.tags,
        is_featured=data.is_featured
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
    db: AsyncSession = Depends(get_db)
):
    """
    Delete a search.
    
    Permanently removes a search and all its messages.
    """
    operations = ResearchOperations(db)
    
    # Verify ownership of search
    search = await operations.get_search_by_id(search_id)
    if not search or str(search["user_id"]) != str(current_user["id"]):
        raise HTTPException(status_code=404, detail="Search not found")
    
    # Delete search
    success = await operations.delete_search(search_id)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to delete search")

# Helper function to get user's enterprise ID
async def get_user_enterprise(current_user: Union[dict, UUID], db: AsyncSession) -> UUID:
    """
    Get the enterprise ID for a user.
    
    Args:
        current_user: Either a dictionary containing user data, or a UUID representing the user ID
        db: SQLAlchemy async session
        
    Returns:
        UUID of the user's enterprise
        
    Raises:
        HTTPException: If user has no associated enterprise
    """
    from sqlalchemy import text
    
    # If current_user is a dictionary with enterprise_id
    if isinstance(current_user, dict) and "enterprise_id" in current_user:
        return current_user["enterprise_id"]
    
    # Otherwise, query the database using the UUID
    user_id = current_user if isinstance(current_user, UUID) else current_user["id"]
    
    # Use direct SQL query to avoid ORM relationship issues
    query = text("""
        SELECT enterprise_id FROM vault.users WHERE id = :user_id
    """)
    
    result = await db.execute(query, {"user_id": user_id})
    enterprise_id = result.scalar_one_or_none()
    
    if not enterprise_id:
        raise HTTPException(status_code=400, detail="User not associated with an enterprise")
    
    return enterprise_id