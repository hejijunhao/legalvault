# models/domain/user_operations.py

from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from uuid import UUID
from sqlalchemy import select, delete, text
from sqlalchemy.ext.asyncio import AsyncSession
from passlib.context import CryptContext
from jose import jwt, JWTError
from models.database.auth_user import AuthUser
from models.database.user import User
from models.schemas.auth.user import UserCreate, UserLogin, UserProfile
from models.schemas.auth.token import TokenResponse, TokenData
import os
from core.database import get_db
import logging
import re
from core.config import settings

# Get JWT settings from environment
JWT_SECRET = settings.SUPABASE_JWT_SECRET or os.getenv("JWT_SECRET_KEY") or os.getenv("SUPABASE_JWT_SECRET", "your-secret-key")  # Use a secure key in production
JWT_ALGORITHM = "HS256"
JWT_EXPIRATION = 30  # minutes

# Set up logging
logger = logging.getLogger(__name__)

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class UserOperations:
    def __init__(self, db):
        self.db = db

    async def _verify_password(self, plain_password: str, encrypted_password: str) -> bool:
        """Verify a password against a hash."""
        return pwd_context.verify(plain_password, encrypted_password)
    
    async def _get_password_hash(self, password: str) -> str:
        """Generate a password hash."""
        return pwd_context.hash(password)

    async def _create_access_token(self, data: dict, expires_delta: Optional[timedelta] = None) -> str:
        """Create a JWT access token."""
        to_encode = data.copy()
        
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=JWT_EXPIRATION)
            
        # Ensure the token has the required claims for Supabase compatibility
        to_encode.update({
            "exp": expire,
            "iat": datetime.utcnow(),
            "iss": os.getenv("SUPABASE_URL", "https://aeeqdxfcjthzzkuirbrd.supabase.co/auth/v1")
        })
        
        encoded_jwt = jwt.encode(to_encode, JWT_SECRET, algorithm=JWT_ALGORITHM)
        return encoded_jwt

    async def register(self, data: UserCreate) -> Optional[UserProfile]:
        """
        Register a new user using Supabase Auth.
        Creates both Supabase Auth user and application User records.
        """
        from core.supabase_client import get_supabase_client
        
        supabase = get_supabase_client()
        
        try:
            # Register user with Supabase Auth
            auth_response = supabase.auth.sign_up({
                "email": data.email,
                "password": data.password,
                "options": {
                    "data": {
                        "first_name": data.first_name,
                        "last_name": data.last_name,
                        "role": data.role
                    }
                }
            })
            
            # Check if user was created successfully
            if not auth_response.user:
                print(f"Failed to create Supabase user: {auth_response}")
                return None
                
            # Get the user ID from the response
            auth_user_id = auth_response.user.id
            
            # Ensure auth_user_id is a UUID object, not a string
            from uuid import UUID
            try:
                auth_user_id = UUID(auth_user_id)
            except ValueError as e:
                print(f"Error converting auth_user_id to UUID: {e}")
                return None
            
            # Create application user record using direct SQL to avoid relationship issues
            query = text("""
                INSERT INTO public.users (id, auth_user_id, first_name, last_name, name, role, email, created_at, updated_at)
                VALUES (:id, :auth_user_id, :first_name, :last_name, :name, :role, :email, NOW(), NOW())
                RETURNING id
            """)
            
            import uuid
            user_id = uuid.uuid4()
            
            result = await self.db.execute(
                query,
                {
                    "id": user_id,
                    "auth_user_id": auth_user_id,
                    "first_name": data.first_name,
                    "last_name": data.last_name,
                    "name": f"{data.first_name} {data.last_name}",
                    "role": data.role,
                    "email": data.email
                }
            )
            await self.db.commit()
            
            # Now fetch the user directly to avoid relationship loading
            query = text("""
                SELECT id, auth_user_id, first_name, last_name, name, role, email, virtual_paralegal_id, enterprise_id, created_at, updated_at
                FROM public.users WHERE id = :id
            """)
            result = await self.db.execute(query, {"id": user_id})
            user_data = result.fetchone()

            # Create a UserProfile object instead of a User instance to avoid circular imports
            if user_data:
                return UserProfile(
                    id=user_data[0],
                    email=user_data[6],  # Use email from database
                    first_name=user_data[2],
                    last_name=user_data[3],
                    name=user_data[4],
                    role=user_data[5],
                    virtual_paralegal_id=user_data[7],
                    enterprise_id=user_data[8],
                    created_at=user_data[9],
                    updated_at=user_data[10]
                )
            
            return None
        except Exception as e:
            print(f"Error during registration: {str(e)}")
            # Print more detailed error information
            import traceback
            traceback.print_exc()
            await self.db.rollback()
            return None

    async def update_user_email(self, user_id: UUID, email: str) -> Optional[UserProfile]:
        """
        Update a user's email in both Supabase Auth and public.users table.
        
        Args:
            user_id: UUID of the user in the application database
            email: New email address
        
        Returns:
            Updated UserProfile or None if update failed
        """
        import re
        from core.supabase_client import get_supabase_client
        
        # Validate email format
        email_pattern = r"[^@]+@[^@]+\.[^@]+"
        if not re.match(email_pattern, email):
            logger.error(f"Invalid email format: {email}")
            return None
        
        try:
            # Get the user to find the auth_user_id
            user = await self.get_user_by_id(user_id)
            if not user:
                logger.error(f"User not found with ID: {user_id}")
                return None
                
            auth_user_id = user["auth_user_id"]
            
            # Check email uniqueness in public.users
            query = text("""
                SELECT id FROM public.users WHERE email = :email AND id != :user_id
            """)
            result = await self.db.execute(query, {"email": email, "user_id": user_id})
            if result.fetchone():
                logger.error(f"Email {email} already in use in public.users")
                return None
            
            # Check email uniqueness in Supabase Auth
            supabase = get_supabase_client()
            try:
                auth_users = supabase.auth.admin.list_users()
                if any(u.email == email and u.id != str(auth_user_id) for u in auth_users):
                    logger.error(f"Email {email} already in use in Supabase Auth")
                    return None
            except Exception as auth_error:
                logger.error(f"Error checking email uniqueness in Supabase Auth: {str(auth_error)}")
                return None
            
            # Update public.users first (safer transaction approach)
            query = text("""
                UPDATE public.users
                SET email = :email, updated_at = NOW()
                WHERE id = :user_id
                RETURNING id
            """)
            
            result = await self.db.execute(query, {"email": email, "user_id": user_id})
            if not result.fetchone():
                logger.error(f"Failed to update email in public.users for user {user_id}")
                await self.db.rollback()
                return None
            
            # Then update Supabase Auth
            try:
                supabase.auth.admin.update_user_by_id(auth_user_id, {"email": email})
                logger.info(f"Successfully updated email in Supabase Auth for user {auth_user_id}")
            except Exception as auth_error:
                logger.error(f"Error updating email in Supabase Auth: {str(auth_error)}")
                await self.db.rollback()
                return None
            
            # Commit the transaction
            await self.db.commit()
            logger.info(f"Successfully updated email for user {user_id} to {email}")
            
            # Return updated user profile
            return await self.get_user_profile(user_id)
        except Exception as e:
            logger.error(f"Error updating user email: {str(e)}")
            await self.db.rollback()
            return None

    async def authenticate(self, data: UserLogin) -> Optional[TokenResponse]:
        """
        Authenticate a user using Supabase Auth.
        """
        from core.supabase_client import get_supabase_client
        
        supabase = get_supabase_client()
        
        try:
            # Sign in with Supabase Auth
            auth_response = supabase.auth.sign_in_with_password({
                "email": data.email,
                "password": data.password
            })
            
            # Get the user ID from the response
            auth_user_id = auth_response.user.id
            
            # Create query with minimal execution options for pgBouncer compatibility
            query = text("""
                SELECT id, auth_user_id, first_name, last_name, name, role, email, virtual_paralegal_id, enterprise_id, created_at, updated_at
                FROM public.users WHERE auth_user_id = :auth_user_id
            """).execution_options(
                no_parameters=True  # This option is supported on statements
            )
            
            try:
                # Execute query directly on the session
                result = await self.db.execute(query, {"auth_user_id": auth_user_id})
                user_data = result.fetchone()
                
            except Exception as e:
                print(f"Error during authentication: {str(e)}")
                print(f"Traceback:", traceback.format_exc())
                
                # Handle pgBouncer errors
                if "DuplicatePreparedStatementError" in str(e) or "prepared statement" in str(e):
                    print("Detected pgBouncer prepared statement issue - retrying with no_parameters")
                    # Retry with no_parameters
                    result = await self.db.execute(query)
                    user_data = result.fetchone()
                else:
                    raise HTTPException(
                        status_code=503,
                        detail="Database connection failed. Please try again later."
                    )
            
            if not user_data:
                return None
            
            # Get the access token directly from Supabase response
            access_token = auth_response.session.access_token
            refresh_token = auth_response.session.refresh_token
            expires_in = auth_response.session.expires_in
            
            return TokenResponse(
                access_token=access_token,
                token_type="bearer",
                user_id=user_data[0],
                expires_in=expires_in
            )
        except Exception as e:
            print(f"Error during authentication: {str(e)}")
            # Print more detailed error information
            import traceback
            traceback.print_exc()
            return None

    async def get_user_by_id(self, user_id: UUID) -> Optional[Dict[str, Any]]:
        """Get a user by ID"""
        query = text("""
            SELECT id, auth_user_id, first_name, last_name, name, role, email, virtual_paralegal_id, enterprise_id, created_at, updated_at
            FROM public.users WHERE id = :user_id
        """).execution_options(
            no_parameters=True,  # Required for pgBouncer compatibility
            use_server_side_cursors=False  # Disable server-side cursors
        )
        result = await self.db.execute(query, {"user_id": user_id})
        user_data = result.fetchone()

        if not user_data:
            return None
            
        # Return as a dictionary for easier access
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

    async def get_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """Get a user by email (via auth user)"""
        from core.supabase_client import get_supabase_client
        
        supabase = get_supabase_client()
        
        try:
            # Get the user ID from Supabase Auth
            auth_response = supabase.auth.admin.get_user_by_email(email)
            auth_user_id = auth_response.id
            
            # Get the application user using direct SQL
            query = text("""
                SELECT id, auth_user_id, first_name, last_name, name, role, email, virtual_paralegal_id, enterprise_id, created_at, updated_at
                FROM public.users WHERE auth_user_id = :auth_user_id
            """).execution_options(
                no_parameters=True,  # Required for pgBouncer compatibility
                use_server_side_cursors=False  # Disable server-side cursors
            )
            result = await self.db.execute(query, {"auth_user_id": auth_user_id})
            user_data = result.fetchone()
            
            if not user_data:
                return None
                
            # Return as a dictionary for easier access
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
        except Exception as e:
            print(f"Error getting user by email: {str(e)}")
            return None

    async def get_user_profile(self, user_id: UUID) -> Optional[UserProfile]:
        """Get user profile information including email from public.users table.
        
        Args:
            user_id: UUID of the user in the application database
        
        Returns:
            UserProfile object with complete user information or None if user not found
        """
        # Use direct SQL to get the user to avoid relationship loading issues
        query = text("""
            SELECT id, auth_user_id, first_name, last_name, name, role, email, virtual_paralegal_id, enterprise_id, created_at, updated_at
            FROM public.users WHERE id = :user_id
        """).execution_options(
            no_parameters=True,  # Required for pgBouncer compatibility
            use_server_side_cursors=False  # Disable server-side cursors
        )
        
        try:
            logger.debug(f"Retrieving user profile for user_id: {user_id}")
            result = await self.db.execute(query, {"user_id": user_id})
            user_data = result.fetchone()
            
            if not user_data:
                logger.warning(f"No user found with ID: {user_id}")
                return None
            
            # Get last login time from Supabase Auth if possible
            last_login = None
            try:
                from core.supabase_client import get_supabase_client
                supabase = get_supabase_client()
                
                # Get user details from Supabase Auth using auth_user_id
                auth_user_id = user_data[1]  # auth_user_id is at index 1
                auth_response = supabase.auth.admin.get_user_by_id(auth_user_id)
                last_login = auth_response.last_sign_in_at
            except Exception as auth_error:
                logger.error(f"Error retrieving last login from Supabase Auth: {str(auth_error)}")
                last_login = None
            
            # Use email from public.users table
            email = user_data[6]  # email is now at index 6
            
            # If email is not set in the database, use a fallback
            if not email:
                email = f"{user_data[2].lower()}.{user_data[3].lower()}@example.com"
                logger.warning(f"Using fallback email for user {user_id}: {email}")
            
            return UserProfile(
                id=user_data[0],
                email=email,
                first_name=user_data[2],
                last_name=user_data[3],
                name=user_data[4],
                role=user_data[5],
                virtual_paralegal_id=user_data[7],
                enterprise_id=user_data[8],
                created_at=user_data[9],
                last_login=last_login
            )
        except Exception as e:
            logger.error(f"Error getting user profile: {str(e)}", exc_info=True)
            return None

    async def decode_token(self, token: str) -> Optional[TokenData]:
        """Decode and validate a JWT token"""
        try:
            # Get JWT secret from settings or environment
            supabase_jwt_secret = settings.SUPABASE_JWT_SECRET or os.getenv("SUPABASE_JWT_SECRET")
            if not supabase_jwt_secret:
                logger.error("SUPABASE_JWT_SECRET environment variable is not set")
                return None
                
            # Log token details (first 10 chars only for security)
            logger.info(f"Decoding token: {token[:10]}...")
                
            # Decode token with options to disable audience validation
            # This is necessary because Supabase tokens have an audience claim that may not match our expectations
            payload = jwt.decode(
                token, 
                supabase_jwt_secret, 
                algorithms=[JWT_ALGORITHM],
                options={
                    "verify_aud": False,  # Disable audience validation
                    "verify_signature": True,  # Still verify the signature
                    "verify_exp": True,  # Verify expiration
                    "verify_iat": False,  # Don't verify issued at time
                    "verify_nbf": False,  # Don't verify not before time
                    "verify_iss": False,  # Don't verify issuer
                    "verify_sub": False,  # Don't verify subject
                    "verify_jti": False,  # Don't verify JWT ID
                    "verify_at_hash": False,  # Don't verify access token hash
                }
            )
            
            # Log the payload for debugging (excluding sensitive parts)
            safe_payload = {k: v for k, v in payload.items() if k not in ["sub"]}
            logger.info(f"Token payload: {safe_payload}")
            
            # Check for user ID in different possible locations
            user_id = None
            
            # First check 'sub' claim (standard JWT subject)
            if "sub" in payload:
                user_id = payload.get("sub")
                logger.info(f"Found user_id in 'sub' claim: {user_id}")
            
            # If not found, check Supabase-specific locations
            elif "user_id" in payload:
                user_id = payload.get("user_id")
                logger.info(f"Found user_id in 'user_id' claim: {user_id}")
            
            # If still not found, check for custom claims
            elif "user" in payload and isinstance(payload["user"], dict) and "id" in payload["user"]:
                user_id = payload["user"]["id"]
                logger.info(f"Found user_id in 'user.id' claim: {user_id}")
            
            if user_id is None:
                logger.warning("Token missing user identifier claims")
                return None
            
            # Extract email from payload if available
            email = None
            if "email" in payload:
                email = payload.get("email")
                logger.info(f"Email from token: {email}")
            elif "user" in payload and isinstance(payload["user"], dict) and "email" in payload["user"]:
                email = payload["user"]["email"]
                logger.info(f"Email from token user object: {email}")
            
            # Return TokenData with both user_id and email
            return TokenData(user_id=UUID(user_id), email=email)
        except jwt.ExpiredSignatureError:
            logger.error("Token has expired")
            return None
        except jwt.InvalidTokenError as e:
            logger.error(f"Invalid token: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error decoding token: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            return None

    async def delete_user(self, user_id: UUID) -> bool:
        """
        Delete a user from both application database and Supabase Auth.
        """
        try:
            # Get the user to find the auth_user_id using direct SQL
            user = await self.get_user_by_id(user_id)
            if not user:
                return False
                
            # Store the auth_user_id before deleting the user
            auth_user_id = user["auth_user_id"]
            
            # Delete from application database using direct SQL
            query = text("""
                DELETE FROM public.users WHERE id = :user_id
            """)
            await self.db.execute(query, {"user_id": user_id})
            await self.db.commit()
            
            # Then delete from Supabase Auth
            from core.supabase_client import get_supabase_client
            supabase = get_supabase_client()
            supabase.auth.admin.delete_user(auth_user_id)
            
            return True
        except Exception as e:
            print(f"Error deleting user: {str(e)}")
            await self.db.rollback()
            return False