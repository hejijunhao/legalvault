# backend/tests/conftest.py

import os
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool
from sqlalchemy.engine.url import make_url

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
    # Configure SSL and authentication settings
    connect_args = {
        "sslmode": "require",      # Use SSL
        "connect_timeout": 10,     # Connection timeout in seconds
        "gssencmode": "disable",   # Disable GSSAPI authentication which was causing errors
    }
    
    # Use NullPool to avoid connection pooling issues in tests
    # Explicitly set the driver to psycopg2
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