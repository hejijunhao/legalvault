# core/auth.py

import logging
import json
from typing import List, Optional, Union, Dict, Any
from uuid import UUID
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from models.database.auth_user import AuthUser
from models.database.user import User
from models.schemas.auth.token import TokenData
from models.domain.user_operations import UserOperations
from core.database import get_db, async_session_factory
import jwt

logger = logging.getLogger(__name__)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

async def get_current_user(
    token: Union[str, Depends] = Depends(oauth2_scheme), 
    session: AsyncSession = Depends(get_db)
) -> User:
    """
    Validate the access token and return the current user.
    Supports both HTTP Bearer auth and WebSocket token authentication.
    
    Args:
        token: Either a direct token string (WebSocket) or OAuth2 dependency result (HTTP)
        session: Database session for user lookup
        
    Returns:
        User: Authenticated user object with internal user ID
        
    Raises:
        HTTPException: If token is invalid, expired, or user not found
        
    Note:
        For WebSocket connections, pass the token directly as a string.
        For HTTP endpoints, the token is automatically extracted from the Authorization header.
    """
    logger.info("===== Authentication Debug =====")
    
    try:
        # Handle both direct token strings (WebSocket) and Depends(oauth2_scheme) (HTTP)
        actual_token = token if isinstance(token, str) else await token
        logger.info(f"Received token: {actual_token[:10]}...")
        
        # Decode token
        user_ops = UserOperations(session)
        token_data = await user_ops.decode_token(actual_token)
        
        if token_data is None:
            logger.info("Authentication failed: Invalid or expired token")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication failed: Invalid or expired token",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Get user from database using direct SQL to avoid prepared statements
        user_id_str = str(token_data.user_id)
        
        # Using string formatting for the query to work around pgBouncer limitations
        query = text(f"""
            SELECT id, auth_user_id, first_name, last_name, name, role, email, 
                   virtual_paralegal_id, enterprise_id, created_at, updated_at
            FROM public.users WHERE auth_user_id = '{user_id_str}'::UUID
        """).execution_options(
            no_parameters=True,
            use_server_side_cursors=False
        )
        
        logger.info(f"Looking up user with auth_user_id: {token_data.user_id}")
        
        result = await session.execute(query)
        user_row = result.fetchone()
        
        if not user_row:
            logger.info(f"No user found with auth_user_id: {token_data.user_id}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication failed: User not found",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        logger.info(f"Found user: {user_row.email} (ID: {user_row.id})")
        
        # Create a User object from the row data
        user = User(
            id=user_row.id,
            auth_user_id=user_row.auth_user_id,
            first_name=user_row.first_name,
            last_name=user_row.last_name,
            name=user_row.name,
            role=user_row.role,
            email=user_row.email,
            virtual_paralegal_id=user_row.virtual_paralegal_id,
            enterprise_id=user_row.enterprise_id,
            created_at=user_row.created_at,
            updated_at=user_row.updated_at
        )
        
        return user
    except jwt.ExpiredSignatureError:
        logger.info("Authentication failed: Token expired")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication failed: Token expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except Exception as e:
        error_message = str(e).lower()
        if ("prepared statement" in error_message or 
            "duplicatepreparedstatementerror" in error_message or 
            "invalidsqlstatementnameerror" in error_message):
            logger.info(f"pgBouncer error encountered: {e}. Attempting with a fresh session...")
            try:
                # Create a fresh session
                fresh_session = async_session_factory()
                
                # Run a test query first
                test_query = text("SELECT 1").execution_options(
                    no_parameters=True, 
                    use_server_side_cursors=False
                )
                await fresh_session.execute(test_query)
                
                # Use a direct SQL query with string formatting to avoid prepared statements
                fresh_query = text(f"""
                    SELECT id, auth_user_id, first_name, last_name, name, role, email, 
                           virtual_paralegal_id, enterprise_id, created_at, updated_at
                    FROM public.users WHERE auth_user_id = '{user_id_str}'::UUID
                """).execution_options(
                    no_parameters=True,
                    use_server_side_cursors=False
                )
                
                result = await fresh_session.execute(fresh_query)
                user_row = result.fetchone()
                
                if not user_row:
                    logger.info(f"No user found with auth_user_id: {token_data.user_id}")
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="Authentication failed: User not found",
                        headers={"WWW-Authenticate": "Bearer"},
                    )
                
                logger.info(f"Retry successful: Found user: {user_row.email} (ID: {user_row.id})")
                
                user = User(
                    id=user_row.id,
                    auth_user_id=user_row.auth_user_id,
                    first_name=user_row.first_name,
                    last_name=user_row.last_name,
                    name=user_row.name,
                    role=user_row.role,
                    email=user_row.email,
                    virtual_paralegal_id=user_row.virtual_paralegal_id,
                    enterprise_id=user_row.enterprise_id,
                    created_at=user_row.created_at,
                    updated_at=user_row.updated_at
                )
                
                # Close fresh session
                await fresh_session.close()
                
                return user
            except Exception as retry_error:
                logger.error(f"Retry also failed: {retry_error}")
                
                if 'fresh_session' in locals() and fresh_session:
                    await fresh_session.close()
                
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail=f"Database connection error: {retry_error}"
                )
        else:
            logger.error(f"Error getting user: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error retrieving user: {e}"
            )

async def get_user_permissions(
    user: User = Depends(get_current_user)
) -> List[str]:
    """
    Get permissions for the current user based on their role.
    """
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
    if user.role != "super_admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions"
        )
    return user
