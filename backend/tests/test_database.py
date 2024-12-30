# backend/tests/test_database.py
import pytest
from sqlalchemy import text
from backend.core.database import get_session

def test_database_connection():
    """Test database connection with more detailed error handling"""
    try:
        with get_session() as session:
            # Try a simple query
            result = session.execute(text("SELECT 1"))
            value = result.scalar()
            assert value == 1

            # Test another simple query
            session.execute(text("SELECT 1"))

    except Exception as e:
        pytest.fail(f"Database connection failed with error: {str(e)}\n"
                    f"Error type: {type(e)}\n"
                    f"This might be due to:\n"
                    f"1. Invalid DATABASE_URL in .env\n"
                    f"2. Database server not running\n"
                    f"3. Network connectivity issues\n"
                    f"4. Invalid credentials")
