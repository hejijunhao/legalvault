# backend/scripts/test_db_connection.py
import asyncio
from sqlalchemy import text
import sys
from pathlib import Path
from urllib.parse import urlparse
import os

current_dir = Path(__file__).resolve()
project_root = str(current_dir.parent.parent.parent)
sys.path.append(project_root)

from backend.core.database import get_session

def debug_database_url():
    db_url = os.getenv("DATABASE_URL")
    print(f"\nDEBUG: DATABASE_URL exists: {db_url is not None}")
    if db_url:
        parsed = urlparse(db_url)
        print(f"URL Format Debug:")
        print(f"- Protocol: {parsed.scheme}")
        print(f"- Host: {parsed.hostname}")
        print(f"- Port: {parsed.port}")
        print(f"- Path: {parsed.path}")

async def test_connection():
    print("\nTesting database connection...")
    session = None
    try:
        session = await get_session()
        # Use raw SQL execution without prepared statements
        query = text("SELECT 1 as test")
        result = await session.execute(query, execution_options={"prebuffer_rows": True})
        row = result.first()
        if row and row.test == 1:
            print("Database connection successful!")
            return True
    except Exception as e:
        print(f"Database connection failed: {str(e)}")
        return False
    finally:
        if session:
            await session.close()

if __name__ == "__main__":
    debug_database_url()
    asyncio.run(test_connection())