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

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

async def get_current_user(
    token: str = Depends(oauth2_scheme), 
    session: AsyncSession = Depends(get_db)
) -> dict:
    """
    Validate the access token and return the current user as a dictionary.
    """
    print(f"\n\n===== Authentication Debug =====\nReceived token: {token[:10]}...")
    
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    # Decode token
    user_ops = UserOperations(session)
    token_data = await user_ops.decode_token(token)
    
    print(f"Token data after decoding: {token_data}")
    
    if token_data is None:
        print("Token data is None, raising credentials exception")
        raise credentials_exception
        
    # Get user from database using direct SQL to avoid relationship loading issues
    from sqlalchemy import text
    
    # First try to get user by ID
    query = text("""
        SELECT id, auth_user_id, first_name, last_name, name, role, email, virtual_paralegal_id, enterprise_id, created_at, updated_at
        FROM vault.users WHERE id = :user_id
    """)
    
    print(f"Executing query with user_id: {token_data.user_id}")
    
    result = await session.execute(query, {"user_id": token_data.user_id})
    user_data = result.fetchone()
    
    print(f"Query result by ID: {user_data}")
    
    # If not found by ID, try by auth_user_id
    if user_data is None:
        print("User not found by ID, trying by auth_user_id")
        query = text("""
            SELECT id, auth_user_id, first_name, last_name, name, role, email, virtual_paralegal_id, enterprise_id, created_at, updated_at
            FROM vault.users WHERE auth_user_id = :auth_user_id
        """)
        result = await session.execute(query, {"auth_user_id": token_data.user_id})
        user_data = result.fetchone()
        print(f"Query result by auth_user_id: {user_data}")
    
    if user_data is None:
        print("User data is still None after both queries, raising credentials exception")
        raise credentials_exception
    
    print(f"Successfully found user: {user_data[0]} with role: {user_data[5]}")
    print("===== End Authentication Debug =====\n\n")
    
    # Return user data as a dictionary instead of creating a User instance
    return {
        "id": user_data[0],
        "auth_user_id": user_data[1],
        "first_name": user_data[2],
        "last_name": user_data[3],
        "name": user_data[4],
        "role": user_data[5],
        "email": user_data[6],
        "virtual_paralegal_id": user_data[7],
        "enterprise_id": user_data[8],
        "created_at": user_data[9],
        "updated_at": user_data[10]
    }

async def get_user_permissions(
    user: dict = Depends(get_current_user)
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
    
    return role_permissions.get(user["role"], [])

async def require_admin(user: dict = Depends(get_current_user)):
    """
    Require the user to have admin role.
    """
    if user["role"] != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions"
        )
    return user

async def require_super_admin(user: dict = Depends(get_current_user)):
    """
    Require the user to have super_admin role.
    """
    # This would typically check the auth_user.is_super_admin flag
    # For now, we'll just check the role
    if user["role"] != "super_admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions"
        )
    return user