# tests/database/test_sqlalchemy.py

"""
Test SQLAlchemy database connection through the application's session management.
"""
import pytest
from sqlalchemy import text

def test_sqlalchemy_connection(session):
    """Test database connection using SQLAlchemy session"""
    # Execute a simple query
    result = session.execute(text("SELECT 1"))
    value = result.scalar()
    
    # Verify result
    assert value == 1, "SQLAlchemy query did not return expected result"

def test_database_version(session):
    """Test database version information"""
    # Get PostgreSQL version
    result = session.execute(text("SHOW server_version"))
    version = result.scalar()
    
    # Just verify we can get the version
    assert version is not None, "Could not retrieve database version"
    print(f"PostgreSQL version: {version}")