# models/domain/user_operations.py

from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from uuid import UUID
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from passlib.context import CryptContext
from jose import jwt
from models.database.auth_user import AuthUser
from models.database.user import User
from models.schemas.auth.user import UserCreate, UserLogin, UserProfile
from models.schemas.auth.token import TokenResponse, TokenData
import os
from core.database import get_async_session

# Get JWT settings from environment
JWT_SECRET = os.getenv("JWT_SECRET_KEY", "your-secret-key")  # Use a secure key in production
JWT_ALGORITHM = "HS256"
JWT_EXPIRATION = 30  # minutes

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class UserOperations:
    def __init__(self, session: AsyncSession):
        self.session = session

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
            
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, JWT_SECRET, algorithm=JWT_ALGORITHM)
        return encoded_jwt

    async def register(self, data: UserCreate) -> Optional[User]:
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
            from sqlalchemy import text
            
            # Create the user with minimal fields to avoid relationship loading
            query = text("""
                INSERT INTO vault.users (id, auth_user_id, first_name, last_name, name, role, created_at, updated_at)
                VALUES (:id, :auth_user_id, :first_name, :last_name, :name, :role, NOW(), NOW())
                RETURNING id
            """)
            
            import uuid
            user_id = uuid.uuid4()
            
            result = await self.session.execute(
                query,
                {
                    "id": user_id,
                    "auth_user_id": auth_user_id,
                    "first_name": data.first_name,
                    "last_name": data.last_name,
                    "name": f"{data.first_name} {data.last_name}",
                    "role": data.role
                }
            )
            await self.session.commit()
            
            # Now fetch the user directly to avoid relationship loading
            query = text("""
                SELECT id, auth_user_id, first_name, last_name, name, role, virtual_paralegal_id, enterprise_id, created_at, updated_at
                FROM vault.users WHERE id = :id
            """)
            result = await self.session.execute(query, {"id": user_id})
            user_data = result.fetchone()

            # Create a UserProfile object instead of a User instance to avoid circular imports
            if user_data:
                return UserProfile(
                    id=user_data[0],
                    email=data.email,
                    first_name=user_data[2],
                    last_name=user_data[3],
                    name=user_data[4],
                    role=user_data[5],
                    virtual_paralegal_id=user_data[6],
                    enterprise_id=user_data[7],
                    created_at=user_data[8],
                    updated_at=user_data[9]
                )
            
            return None
        except Exception as e:
            print(f"Error during registration: {str(e)}")
            # Print more detailed error information
            import traceback
            traceback.print_exc()
            await self.session.rollback()
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
            
            # Get the application user
            query = select(User).where(User.auth_user_id == auth_user_id)
            result = await self.session.execute(query)
            user = result.scalar_one_or_none()
            
            if not user:
                return None
            
            # Create access token
            access_token = await self._create_access_token(
                data={"sub": str(user.id), "email": data.email}
            )
            
            return TokenResponse(
                access_token=access_token,
                token_type="bearer",
                user_id=user.id,
                expires_in=JWT_EXPIRATION * 60  # convert minutes to seconds
            )
        except Exception as e:
            print(f"Error during authentication: {str(e)}")
            return None

    async def get_user_by_id(self, user_id: UUID) -> Optional[User]:
        """Get a user by ID"""
        query = select(User).where(User.id == user_id)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_user_by_email(self, email: str) -> Optional[User]:
        """Get a user by email (via auth user)"""
        from core.supabase_client import get_supabase_client
        
        supabase = get_supabase_client()
        
        try:
            # Get the user ID from Supabase Auth
            auth_response = supabase.auth.admin.get_user_by_email(email)
            auth_user_id = auth_response.id
            
            # Get the application user
            query = select(User).where(User.auth_user_id == auth_user_id)
            result = await self.session.execute(query)
            return result.scalar_one_or_none()
        except Exception as e:
            print(f"Error getting user by email: {str(e)}")
            return None

    async def get_user_profile(self, user_id: UUID) -> Optional[UserProfile]:
        """Get user profile information"""
        user = await self.get_user_by_id(user_id)
        if not user:
            return None
            
        # Get auth user for additional info
        from core.supabase_client import get_supabase_client
        
        supabase = get_supabase_client()
        
        try:
            auth_response = supabase.auth.admin.get_user(user.auth_user_id)
            auth_user = auth_response.user
            
            return UserProfile(
                id=user.id,
                email=auth_user.email,
                first_name=user.first_name,
                last_name=user.last_name,
                name=user.name,
                role=user.role,
                virtual_paralegal_id=user.virtual_paralegal_id,
                enterprise_id=user.enterprise_id,
                created_at=user.created_at,
                last_login=auth_user.last_sign_in_at
            )
        except Exception as e:
            print(f"Error getting user profile: {str(e)}")
            return None

    async def decode_token(self, token: str) -> Optional[TokenData]:
        """Decode and validate a JWT token"""
        try:
            payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
            user_id = payload.get("sub")
            if user_id is None:
                return None
                
            return TokenData(user_id=UUID(user_id))
        except jwt.PyJWTError:
            return None

    async def delete_user(self, user_id: UUID) -> bool:
        """
        Delete a user from both application database and Supabase Auth.
        """
        try:
            # Get the user to find the auth_user_id
            user = await self.get_user_by_id(user_id)
            if not user:
                return False
                
            # Store the auth_user_id before deleting the user
            auth_user_id = user.auth_user_id
            
            # First delete from application database
            query = delete(User).where(User.id == user_id)
            await self.session.execute(query)
            await self.session.commit()
            
            # Then delete from Supabase Auth
            from core.supabase_client import get_supabase_client
            supabase = get_supabase_client()
            supabase.auth.admin.delete_user(auth_user_id)
            
            return True
        except Exception as e:
            print(f"Error deleting user: {str(e)}")
            await self.session.rollback()
            return False