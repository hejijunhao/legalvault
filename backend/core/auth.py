# core/auth.py

from typing import List, Optional
from uuid import UUID
from fastapi import Depends, HTTPException, status, Query
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from models.database.auth_user import AuthUser
from models.database.user import User
from models.schemas.auth.token import TokenData
from models.domain.user_operations import UserOperations
from core.database import get_db, async_session_factory
import jwt
from sqlalchemy import text
import logging

logger = logging.getLogger(__name__)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login", auto_error=False)

async def get_current_user(
    token: Optional[str] = Depends(oauth2_scheme), 
    session: AsyncSession = Depends(get_db)
) -> Optional[User]:
    """
    Validate the access token and return the current user.
    Returns None if no token is provided or if token is invalid.
    """
    if not token:
        return None
        
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
    
    # Create a safe string representation of the UUID
    # UUIDs have a fixed format and come from a validated token, so this is safe from SQL injection
    user_id_str = str(token_data.user_id)
    
    # Create a query with the UUID as a string literal with proper type casting
    query = text(f"""
        SELECT id, auth_user_id, first_name, last_name, name, role, email, virtual_paralegal_id, enterprise_id, created_at, updated_at
        FROM public.users WHERE auth_user_id = '{user_id_str}'::UUID
    """).execution_options(
        no_parameters=True,  # Required for pgBouncer compatibility
        use_server_side_cursors=False  # Disable server-side cursors
    )
    
    print(f"Looking up user with auth_user_id: {token_data.user_id}")
    
    try:
        # Execute without parameters since they're already embedded in the query
        result = await session.execute(query)
        user_row = result.fetchone()
        
        if not user_row:
            print(f"No user found with auth_user_id: {token_data.user_id}")
            raise credentials_exception
            
        print(f"Found user: {user_row[6]} (ID: {user_row[0]})")
        
        # Create a User object from the row data
        user = User(
            id=user_row[0],
            auth_user_id=user_row[1],
            first_name=user_row[2],
            last_name=user_row[3],
            name=user_row[4],
            role=user_row[5],
            email=user_row[6],
            virtual_paralegal_id=user_row[7],
            enterprise_id=user_row[8],
            created_at=user_row[9],
            updated_at=user_row[10]
        )
        
        return user
    except Exception as e:
        error_message = str(e).lower()
        # Check for pgBouncer-related errors
        if ("prepared statement" in error_message or 
            "duplicatepreparedstatementerror" in error_message or 
            "invalidsqlstatementnameerror" in error_message):
            print(f"pgBouncer error encountered: {e}. Attempting with a fresh session...")
            # Close the current session
            await session.close()
            
            # Create a fresh session directly instead of using get_db() as a context manager
            fresh_session = async_session_factory()
            try:
                # Execute the test query to ensure connection is valid
                test_query = text("SELECT 1").execution_options(
                    no_parameters=True, 
                    use_server_side_cursors=False
                )
                await fresh_session.execute(test_query)
                
                # Create a completely new query with the fresh session
                # Use a parameterized query with execution_options instead of string interpolation
                fresh_query = text("""
                    SELECT id, auth_user_id, first_name, last_name, name, role, email, virtual_paralegal_id, enterprise_id, created_at, updated_at
                    FROM public.users WHERE auth_user_id = :auth_user_id
                """).execution_options(
                    no_parameters=True,  # Required for pgBouncer compatibility
                    use_server_side_cursors=False  # Disable server-side cursors
                )
                
                # Execute the fresh query
                # Convert the UUID string back to a UUID object for the parameter
                result = await fresh_session.execute(fresh_query, {"auth_user_id": UUID(user_id_str)})
                user_row = result.fetchone()
                
                if not user_row:
                    print(f"No user found with auth_user_id: {token_data.user_id}")
                    raise credentials_exception
                
                print(f"Retry successful: Found user: {user_row[6]} (ID: {user_row[0]})")
                
                # Create a User object from the row data
                user = User(
                    id=user_row[0],
                    auth_user_id=user_row[1],
                    first_name=user_row[2],
                    last_name=user_row[3],
                    name=user_row[4],
                    role=user_row[5],
                    email=user_row[6],
                    virtual_paralegal_id=user_row[7],
                    enterprise_id=user_row[8],
                    created_at=user_row[9],
                    updated_at=user_row[10]
                )
                
                return user
            except Exception as retry_error:
                print(f"Retry also failed: {retry_error}")
                # If the retry error is also a prepared statement error, try one more approach
                if ("prepared statement" in str(retry_error).lower() or 
                    "duplicatepreparedstatementerror" in str(retry_error).lower() or 
                    "invalidsqlstatementnameerror" in str(retry_error).lower()):
                    try:
                        # Try a final approach with a completely raw query and no parameters at all
                        final_query = text(f"""
                            SELECT id, auth_user_id, first_name, last_name, name, role, email, virtual_paralegal_id, enterprise_id, created_at, updated_at
                            FROM public.users WHERE auth_user_id = '{user_id_str}'::UUID
                        """).execution_options(
                            no_parameters=True,
                            use_server_side_cursors=False
                        )
                        result = await fresh_session.execute(final_query)
                        user_row = result.fetchone()
                        
                        if not user_row:
                            print(f"No user found with auth_user_id: {token_data.user_id}")
                            raise credentials_exception
                        
                        print(f"Final retry successful: Found user: {user_row[6]} (ID: {user_row[0]})")
                        
                        # Create a User object from the row data
                        user = User(
                            id=user_row[0],
                            auth_user_id=user_row[1],
                            first_name=user_row[2],
                            last_name=user_row[3],
                            name=user_row[4],
                            role=user_row[5],
                            email=user_row[6],
                            virtual_paralegal_id=user_row[7],
                            enterprise_id=user_row[8],
                            created_at=user_row[9],
                            updated_at=user_row[10]
                        )
                        
                        return user
                    except Exception as final_error:
                        print(f"Final retry also failed: {final_error}")
                        raise HTTPException(
                            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                            detail=f"Database connection error after multiple retries: {final_error}"
                        )
                else:
                    raise HTTPException(
                        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                        detail=f"Database connection error: {retry_error}"
                    )
            finally:
                # Always close the fresh session
                await fresh_session.close()
        else:
            # For non-pgBouncer errors, log and raise appropriate exception
            print(f"Error getting user: {e}")
            if "no user found" in error_message:
                raise credentials_exception
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error retrieving user: {e}"
            )

async def get_current_user_from_token(
    token: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db)
) -> Optional[User]:
    """
    Dependency for token-based authentication, primarily used for SSE endpoints.
    Returns None if no token is provided, allowing the endpoint to handle authentication flexibly.
    Raises HTTPException(401) if an invalid token is provided.
    """
    if not token:
        return None

    try:
        user_ops = UserOperations(db)
        token_data = await user_ops.decode_token(token)
        
        if not token_data or not token_data.user_id:
            logger.warning("Invalid token: missing or invalid user_id")
            raise HTTPException(
                status_code=401,
                detail="Invalid authentication token"
            )
        
        # Get user from database using raw SQL for pgBouncer compatibility
        user = await user_ops.get_user_by_auth_id(token_data.user_id)
        if not user:
            logger.warning(f"User not found for auth_id {token_data.user_id}")
            raise HTTPException(
                status_code=401,
                detail="User not found"
            )
        
        return user
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Token authentication error: {str(e)}")
        raise HTTPException(
            status_code=401,
            detail="Authentication failed"
        )

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