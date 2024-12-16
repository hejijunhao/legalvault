# backend/tests/test_database.py
import asyncio
import pytest
from sqlalchemy import text
from backend.core.database import get_session


async def test_database_connection():
    """Test database connection with more detailed error handling"""
    try:
        async with get_session() as session:
            # Try a simple query
            result = await session.execute(text("SELECT 1"))
            value = result.scalar()
            assert value == 1

            # No need for another transaction block since get_session already manages it
            await session.execute(text("SELECT 1"))

    except Exception as e:
        pytest.fail(f"Database connection failed with error: {str(e)}\n"
                    f"Error type: {type(e)}\n"
                    f"This might be due to:\n"
                    f"1. Invalid DATABASE_URL in .env\n"
                    f"2. Database server not running\n"
                    f"3. Network connectivity issues\n"
                    f"4. Invalid credentials")


if __name__ == "__main__":
    asyncio.run(test_database_connection())