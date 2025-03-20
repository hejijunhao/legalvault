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
    
    try:
        result = await session.execute(query, {"user_id": token_data.user_id})
        user_row = result.fetchone()
        
        if not user_row:
            print(f"No user found with ID {token_data.user_id}, trying with email: {token_data.email}")
            
            # If no user found by ID, try by email
            query = text("""
                SELECT id, auth_user_id, first_name, last_name, name, role, email, virtual_paralegal_id, enterprise_id, created_at, updated_at
                FROM vault.users WHERE email = :email
            """)
            
            result = await session.execute(query, {"email": token_data.email})
            user_row = result.fetchone()
            
            if not user_row:
                print(f"No user found with email {token_data.email} either, raising credentials exception")
                raise credentials_exception
        
        # Convert row to dict
        user_dict = {}
        for idx, column_name in enumerate(result.keys()):
            user_dict[column_name] = user_row[idx]
            
        print(f"Found user: {user_dict['email']} (ID: {user_dict['id']})")
        return user_dict
        
    except Exception as e:
        print(f"Error querying user: {str(e)}")
        raise credentials_exception

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