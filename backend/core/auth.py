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

# Schema configuration (adjust based on your setup)
USER_SCHEMA = "public"

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
        User: Authenticated user object
        
    Raises:
        HTTPException: If token is invalid/expired, user not found, or UUID invalid
    """
    logger.info("Starting user authentication")
    
    try:
        # Handle token
        actual_token = token if isinstance(token, str) else await token
        
        # Decode token
        user_ops = UserOperations(session)
        token_data = await user_ops.decode_token(actual_token)
        
        if token_data is None:
            logger.warning("Authentication failed: Invalid or expired token")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication failed: Invalid or expired token",
                headers={"WWW-Authenticate": "Bearer"},
            )
            
        # Validate UUID
        try:
            user_id = UUID(str(token_data.user_id))
        except ValueError:
            logger.error(f"Invalid UUID format: {token_data.user_id}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid user ID format"
            )

        # Define parameterized query
        query = text(f"""
            SELECT id, auth_user_id, first_name, last_name, name, role, email,
                   virtual_paralegal_id, enterprise_id, created_at, updated_at
            FROM {USER_SCHEMA}.users 
            WHERE auth_user_id = :user_id
        """).bindparams(user_id=user_id)
        
        # Attempt query with original session
        logger.debug(f"Executing query for user_id: {user_id}")
        user = await _execute_user_query(session, query, user_id)
        if user:
            logger.info(f"Found user: {user.email} (ID: {user.id})")
            return user
            
        # Retry with fresh session
        async with async_session_factory() as fresh_session:
            logger.info("Retrying with fresh session")
            user = await _execute_user_query(fresh_session, query, user_id)
            if user:
                logger.info(f"Retry successful: Found user: {user.email} (ID: {user.id})")
                return user
            
        # User not found
        logger.warning(f"No user found with auth_user_id: {user_id}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication failed: User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    except jwt.ExpiredSignatureError:
        logger.warning("Authentication failed: Token expired")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication failed: Token expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error during authentication: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error during authentication"
        )

async def _execute_user_query(
    session: AsyncSession,
    query: text,
    user_id: UUID,
    max_retries: int = 2
) -> Optional[User]:
    """
    Execute the user query with pgBouncer handling.
    
    Args:
        session: Database session
        query: Parameterized query
        user_id: UUID of the user to find
        max_retries: Maximum retry attempts for pgBouncer errors
        
    Returns:
        Optional[User]: User object if found, None otherwise
    """
    for attempt in range(max_retries):
        try:
            result = await session.execute(
                query.execution_options(
                    no_parameters=True,
                    use_server_side_cursors=False
                )
            )
            user_row = result.fetchone()
            
            if not user_row:
                return None
                
            return User(
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
        except Exception as e:
            error_message = str(e).lower()
            if any(err in error_message for err in [
                "prepared statement",
                "duplicatepreparedstatementerror",
                "invalidsqlstatementnameerror"
            ]):
                logger.info(f"pgBouncer compatibility error (attempt {attempt + 1}/{max_retries}): {e}")
                if attempt < max_retries - 1:
                    continue
            raise
    return None

async def get_user_permissions(
    user: User = Depends(get_current_user)
) -> List[str]:
    """
    Get permissions for the current user based on their role.
    """
    logger.info(f"Retrieving permissions for user {user.id} with role {user.role}")
    role_permissions = {
        "lawyer": ["read:all", "write:own"],
        "admin": ["read:all", "write:all", "admin:all"],
        "paralegal": ["read:all", "write:limited"],
    }
    permissions = role_permissions.get(user.role, [])
    logger.info(f"Permissions for user {user.id}: {permissions}")
    return permissions

async def require_admin(user: User = Depends(get_current_user)):
    """
    Require the user to have admin role.
    """
    logger.info(f"Checking admin role for user {user.id}")
    if user.role != "admin":
        logger.error(f"User {user.id} does not have admin role")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions"
        )
    logger.info(f"User {user.id} confirmed as admin")
    return user

async def require_super_admin(user: User = Depends(get_current_user)):
    """
    Require the user to have super_admin role.
    """
    logger.info(f"Checking super_admin role for user {user.id}")
    if user.role != "super_admin":
        logger.error(f"User {user.id} does not have super_admin role")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions"
        )
    logger.info(f"User {user.id} confirmed as super_admin")
    return user


