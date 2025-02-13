# backend/tests/conftest.py

import pytest
from pathlib import Path
import sys
from sqlmodel import SQLModel
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Add backend directory to Python path
current_dir = Path(__file__).resolve().parent
backend_dir = current_dir.parent
sys.path.insert(0, str(backend_dir))

@pytest.fixture(scope="session")
def engine():
    """Create a test database engine"""
    # Use PostgreSQL instead of SQLite for JSONB support
    DATABASE_URL = "postgresql://philippholke@localhost:5432/test_db"
    
    engine = create_engine(
        DATABASE_URL,
        echo=True  # Set to True to see SQL statements
    )
    
    # Create all tables
    SQLModel.metadata.create_all(engine)
    
    yield engine
    
    # Clean up - drop all tables after tests
    SQLModel.metadata.drop_all(engine)

@pytest.fixture
def session(engine):
    """Create a new database session for a test"""
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()