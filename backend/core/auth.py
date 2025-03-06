# core/auth.py

from typing import List, Optional
from uuid import UUID
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlmodel import Session
from models.database.auth_user import AuthUser
from models.database.user import User
from models.schemas.auth.token import TokenData
from models.domain.user_operations import UserOperations
from core.database import get_session
import jwt

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/login")

async def get_current_user(
    token: str = Depends(oauth2_scheme), 
    session: Session = Depends(get_session)
) -> User:
    """
    Validate the access token and return the current user.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    # Decode token
    user_ops = UserOperations(session)
    token_data = user_ops.decode_token(token)
    
    if token_data is None:
        raise credentials_exception
        
    # Get user from database
    user = await user_ops.get_user_by_id(token_data.user_id)
    
    if user is None:
        raise credentials_exception
        
    return user

async def get_user_permissions(
    user: User = Depends(get_current_user)
) -> List[str]:
    """
    Get permissions for the current user based on their role.
    """
    # Simple role-based permissions
    role_permissions = {
        "lawyer": ["read:all", "write:own"],
        "admin": ["read:all", "write:all", "admin:all"],
        "paralegal": ["read:all", "write:limited"],
    }
    
    return role_permissions.get(user.role, [])

async def require_admin(user: User = Depends(get_current_user)):
    """
    Require the user to have admin role.
    """
    if user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions"
        )
    return user

async def require_super_admin(user: User = Depends(get_current_user)):
    """
    Require the user to have super_admin role.
    """
    # This would typically check the auth_user.is_super_admin flag
    # For now, we'll just check the role
    if user.role != "super_admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions"
        )
    return user