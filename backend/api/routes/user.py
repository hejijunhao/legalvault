# api/routes/user.py

from fastapi import APIRouter, Depends, HTTPException, status, Body
from sqlalchemy.ext.asyncio import AsyncSession
from models.schemas.auth.user import UserProfile
from models.domain.user_operations import UserOperations
from core.database import get_db
from core.auth import get_current_user
from models.database.user import User
from uuid import UUID
import logging
from pydantic import EmailStr
from sqlalchemy import text

# Set up logging
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/users", tags=["Users"])

@router.get("/me", response_model=UserProfile)
async def get_current_user_profile(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db)
):
    """Get the profile of the currently authenticated user."""
    logger.info(f"Fetching profile for current user: {current_user.id}")
    user_ops = UserOperations(session)
    profile = await user_ops.get_user_profile(current_user.id)
    
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User profile not found"
        )
    
    return profile

@router.get("/{user_id}", response_model=UserProfile)
async def get_user_profile(
    user_id: UUID,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db)
):
    """Get a user's profile by their ID (either public.users.id or auth.users.id)."""
    logger.info(f"User {current_user.id} requesting profile for user: {user_id}")
    
    # Check if the user is requesting their own profile or has admin permissions
    if current_user.id != user_id and current_user.role not in ["admin", "super_admin"]:
        logger.warning(f"User {current_user.id} with role {current_user.role} attempted to access profile of user {user_id}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this user's profile",
        )
    
    user_ops = UserOperations(session)
    profile = await user_ops.get_user_profile_by_any_id(user_id)
    
    if not profile:
        logger.warning(f"Profile not found for user_id: {user_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {user_id} not found"
        )
    
    logger.info(f"Successfully found profile for user: {profile.email}")
    return profile

@router.patch("/me/email", response_model=UserProfile)
async def update_current_user_email(
    email: EmailStr = Body(..., description="New email address"),
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db)
):
    """Update the email address of the currently authenticated user."""
    logger.info(f"Updating email for user {current_user.id}")
    user_ops = UserOperations(session)
    updated_profile = await user_ops.update_user_email(current_user.id, email)
    
    if not updated_profile:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to update email address"
        )
    
    return updated_profile
