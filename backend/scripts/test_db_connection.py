# backend/scripts/test_db_connection.py
from pathlib import Path
from urllib.parse import urlparse
import os
import sys
from sqlalchemy import text

# Add project root to path
current_dir = Path(__file__).resolve()
project_root = str(current_dir.parent.parent.parent)
sys.path.append(project_root)

from backend.core.database import get_session

def debug_database_url():
    """Debug function to check DATABASE_URL configuration"""
    db_url = os.getenv("DATABASE_URL")
    print(f"\nDEBUG: DATABASE_URL exists: {db_url is not None}")
    if db_url:
        parsed = urlparse(db_url)
        print(f"URL Format Debug:")
        print(f"- Protocol: {parsed.scheme}")
        print(f"- Host: {parsed.hostname}")
        print(f"- Port: {parsed.port}")
        print(f"- Path: {parsed.path}")
        # Check for asyncpg
        if 'asyncpg' in db_url:
            print("WARNING: DATABASE_URL still contains asyncpg!")

def test_connection():
    """Test database connection with detailed error reporting"""
    print("\nTesting database connection...")
    try:
        with get_session() as session:
            # Simple query to test connection
            result = session.execute(text("SELECT 1 as test"))
            row = result.scalar()
            
            if row == 1:
                print("✅ Database connection successful!")
                return True
            else:
                print("❌ Unexpected result from database")
                return False
                
    except Exception as e:
        print(f"❌ Database connection failed: {str(e)}")
        print(f"Error type: {type(e)}")
        return False

if __name__ == "__main__":
    print("Starting database connection test...")
    debug_database_url()
    result = test_connection()
    print(f"\nTest result: {'SUCCESS' if result else 'FAILED'}")
