# api/routes/auth/auth.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from models.schemas.auth.user import UserLogin, UserCreate, UserProfile
from models.schemas.auth.token import TokenResponse
from models.domain.user_operations import UserOperations
from core.database import get_db
from core.auth import get_current_user
from models.database.user import User
from uuid import UUID

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/login", response_model=TokenResponse)
async def login(
    data: UserLogin,
    session: AsyncSession = Depends(get_db)
):
    """
    Authenticate a user and return an access token.
    """
    user_ops = UserOperations(session)
    token = await user_ops.authenticate(data)
    
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    return token

@router.post("/register", response_model=UserProfile)
async def register(
    data: UserCreate,
    session: AsyncSession = Depends(get_db)
):
    """
    Register a new user.
    """
    print(f"Attempting to register user with email: {data.email}")
    user_ops = UserOperations(session)
    profile = await user_ops.register(data)
    
    print(f"Registration result: {profile}")
    
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User already exists or auth user not found",
        )
        
    return profile

@router.get("/me", response_model=UserProfile)
async def get_current_user_profile(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db)
):
    """
    Get the current user's profile.
    """
    user_ops = UserOperations(session)
    profile = await user_ops.get_user_profile(current_user.id)
    
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User profile not found",
        )
        
    return profile

@router.get("/user/{user_id}", response_model=UserProfile)
async def get_user_profile(
    user_id: UUID,
    current_user: dict = Depends(get_current_user),
    session: AsyncSession = Depends(get_db)
):
    """
    Get a user's profile by ID.
    """
    # Check if the user is requesting their own profile or has admin permissions
    if current_user["id"] != user_id and current_user["role"] not in ["admin", "super_admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this user's profile",
        )
        
    user_ops = UserOperations(session)
    profile = await user_ops.get_user_profile(user_id)
    
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User profile not found",
        )
        
    return profile

@router.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: UUID,
    current_user: dict = Depends(get_current_user),
    session: AsyncSession = Depends(get_db)
):
    """
    Delete a user from both Supabase Auth and application database.
    Only admins can delete users.
    """
    # Check if the current user has permission to delete users
    if current_user["role"] != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only administrators can delete users",
        )
    
    user_ops = UserOperations(session)
    result = await user_ops.delete_user(user_id)
    
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found or could not be deleted",
        )
    
    return None  # 204 No Content