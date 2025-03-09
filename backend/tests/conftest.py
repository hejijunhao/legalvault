# backend/tests/conftest.py (full file with hybrid fixture)

import os
import sys
import pytest
from unittest.mock import MagicMock, AsyncMock
from sqlalchemy.sql import text
from sqlalchemy import create_engine, make_url
from sqlalchemy.pool import NullPool
from sqlalchemy.orm import sessionmaker
from datetime import datetime

# Add the backend directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Load environment variables from .env
from dotenv import load_dotenv
from logging import getLogger

logger = getLogger(__name__)
load_dotenv()

# Use the DATABASE_URL from environment
DATABASE_URL = os.environ["DATABASE_URL"]

@pytest.fixture(scope="session")
def engine():
    """Create a test database engine."""
    print("\n=== Creating Database Engine ===")
    connect_args = {
        "sslmode": "require",
        "connect_timeout": 10,
        "gssencmode": "disable",
    }
    url = make_url(DATABASE_URL)
    engine = create_engine(
        url.set(drivername="postgresql+psycopg2"),
        poolclass=NullPool,
        connect_args=connect_args
    )
    return engine

@pytest.fixture
def session(engine):
    """Create a new database session for a test."""
    print("\n=== Creating New Session ===")
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = SessionLocal()
    try:
        yield session
    finally:
        print("\n=== Closing Session ===")
        session.close()

@pytest.fixture
async def test_db_session():
    """Create a fully mocked async database session for testing."""
    class MockResult:
        def __init__(self, data=None):
            self.data = data if data is not None else []
            
        def fetchone(self):
            return self.data[0] if self.data else None
            
        def fetchall(self):
            return self.data
            
        def scalar_one(self):
            if not self.data:
                return None
            if isinstance(self.data[0], tuple):
                return self.data[0][0]
            if isinstance(self.data[0], dict) and 'email' in self.data[0]:
                return self.data[0]['email']
            return None
    
    class MockAsyncSession:
        def __init__(self):
            self.committed = False
            self.rolled_back = False
            self.closed = False
            self.queries = []
            self.mock_data = {"users": {}}
            print("MockAsyncSession initialized")
        
        async def execute(self, statement, *args, **kwargs):
            query_str = str(statement)
            params = kwargs.get("parameters", {}) or args[0] if args else {}
            self.queries.append((query_str, params))
            
            # Debug logging
            print(f"\nEXECUTING QUERY: {query_str}")
            print(f"WITH PARAMS: {params}")
            print(f"CURRENT MOCK DATA: {self.mock_data}")
            
            # Handle INSERT
            if "INSERT INTO vault.users" in query_str:
                user_id = params.get("id")
                auth_user_id = params.get("auth_user_id")
                email = params.get("email")
                self.mock_data["users"][str(auth_user_id)] = {
                    "id": user_id,
                    "auth_user_id": auth_user_id,
                    "email": email,
                    "first_name": "Test",
                    "last_name": "User",
                    "name": "Test User",
                    "role": "user",
                    "virtual_paralegal_id": None,
                    "enterprise_id": None,
                    "created_at": datetime.now(),
                    "updated_at": datetime.now()
                }
                print(f"INSERTED USER: {self.mock_data['users'][str(auth_user_id)]}")
                return MockResult([{"id": user_id}])
            
            # Handle SELECT for get_user_by_id - special case
            elif "SELECT id, auth_user_id, first_name, last_name, name, role, email" in query_str and "WHERE id =" in query_str:
                user_id = params.get("user_id")
                print(f"LOOKING FOR USER BY ID: {user_id}")
                
                # Find user by ID
                for auth_id, user in self.mock_data["users"].items():
                    if str(user["id"]) == str(user_id):
                        print(f"FOUND USER: {user}")
                        # Return as a tuple in the exact order expected by get_user_by_id
                        return MockResult([(user["id"], user["auth_user_id"], user["first_name"], 
                                          user["last_name"], user["name"], user["role"], user["email"],
                                          user["virtual_paralegal_id"], user["enterprise_id"], 
                                          user["created_at"], user["updated_at"])])
                print("USER NOT FOUND BY ID")
                return MockResult()
            
            # Handle SELECT * FROM vault.users WHERE id =
            elif "SELECT * FROM vault.users WHERE id =" in query_str:
                user_id = params.get("user_id")
                print(f"LOOKING FOR USER BY ID: {user_id}")
                
                # Find user by ID
                for auth_id, user in self.mock_data["users"].items():
                    if str(user["id"]) == str(user_id):
                        print(f"FOUND USER: {user}")
                        return MockResult([user])
                print("USER NOT FOUND BY ID")
                return MockResult()
            
            # Handle other SELECT queries
            elif "SELECT" in query_str and "FROM vault.users" in query_str:
                # Determine search key and value
                if "WHERE auth_user_id =" in query_str:
                    key = "auth_user_id"
                    value = params.get("auth_user_id")
                elif "WHERE id =" in query_str:
                    key = "id"
                    value = params.get("id") or params.get("user_id")
                elif "WHERE email =" in query_str:
                    key = "email"
                    value = params.get("email")
                else:
                    print("UNRECOGNIZED SELECT QUERY")
                    return MockResult()
                
                print(f"SEARCHING FOR USER WITH {key} = {value}")
                
                # Find matching user
                for user in self.mock_data["users"].values():
                    if str(user.get(key)) == str(value):
                        print(f"FOUND USER: {user}")
                        
                        # Format result based on query type
                        if "SELECT email FROM" in query_str:
                            return MockResult([(user["email"],)])
                        elif "SELECT id, email FROM" in query_str:
                            return MockResult([(user["id"], user["email"])])
                        elif "SELECT * FROM" in query_str:
                            return MockResult([user])
                        else:
                            return MockResult([(user["id"],)])
                
                print("NO MATCHING USER FOUND")
                return MockResult()
            
            # Handle UPDATE
            elif "UPDATE vault.users" in query_str:
                user_id = params.get("user_id") or params.get("id")
                new_email = params.get("email")
                print(f"UPDATING USER {user_id} WITH EMAIL {new_email}")
                
                # Find and update user
                for auth_id, user in self.mock_data["users"].items():
                    if str(user["id"]) == str(user_id):
                        old_email = user["email"]
                        user["email"] = new_email
                        user["updated_at"] = datetime.now()
                        print(f"UPDATED USER EMAIL FROM {old_email} TO {new_email}")
                        return MockResult([(user["id"],)])
                
                print("USER NOT FOUND FOR UPDATE")
                return MockResult()
            
            print("UNHANDLED QUERY TYPE")
            return MockResult()
        
        async def commit(self):
            self.committed = True
            print("COMMIT CALLED")
        
        async def rollback(self):
            self.rolled_back = True
            print("ROLLBACK CALLED")
        
        async def close(self):
            self.closed = True
        
        def add(self, instance):
            pass
        
        def add_all(self, instances):
            pass
        
        async def refresh(self, instance, **kwargs):
            pass
        
        def expunge(self, instance):
            pass
        
        def expunge_all(self):
            pass
        
        def flush(self):
            pass
        
        async def begin(self):
            return self
        
        async def __aenter__(self):
            return self
        
        async def __aexit__(self, exc_type, exc_val, exc_tb):
            if exc_type is not None:
                await self.rollback()
    
    return MockAsyncSession()