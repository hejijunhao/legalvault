# core/auth.py

from typing import List, Optional
from uuid import UUID
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from models.database.auth_user import AuthUser
from models.database.user import User
from models.schemas.auth.token import TokenData
from models.domain.user_operations import UserOperations
from core.database import get_db
import jwt

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/login")

async def get_current_user(
    token: str = Depends(oauth2_scheme), 
    session: AsyncSession = Depends(get_db)
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
    token_data = await user_ops.decode_token(token)
    
    if token_data is None:
        raise credentials_exception
        
    # Get user from database using direct SQL to avoid relationship loading issues
    from sqlalchemy import text
    
    query = text("""
        SELECT id, auth_user_id, first_name, last_name, name, role, virtual_paralegal_id, enterprise_id, created_at, updated_at
        FROM vault.users WHERE id = :user_id
    """)
    
    result = await session.execute(query, {"user_id": token_data.user_id})
    user_data = result.fetchone()
    
    if user_data is None:
        raise credentials_exception
    
    # Create a User instance manually without loading relationships
    user = User()
    user.id = user_data[0]
    user.auth_user_id = user_data[1]
    user.first_name = user_data[2]
    user.last_name = user_data[3]
    user.name = user_data[4]
    user.role = user_data[5]
    user.virtual_paralegal_id = user_data[6]
    user.enterprise_id = user_data[7]
    user.created_at = user_data[8]
    user.updated_at = user_data[9]
    
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