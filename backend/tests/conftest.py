# backend/tests/conftest.py
import pytest
from pathlib import Path
import sys

# Add project root to Python path
current_dir = Path(__file__).resolve()
project_root = str(current_dir.parent.parent.parent)
sys.path.append(project_root)

@pytest.fixture(scope="session", autouse=True)
def setup_test_environment():
    """Setup any test environment variables or configurations"""
    # You can add any test setup here
    pass

# Usage Example:
if __name__ == "__main__":
    # Run the database connection test directly
    from backend.scripts.test_db_connection import debug_database_url, test_connection
    
    print("Running database connection tests...")
    debug_database_url()
    test_connection()

    # Run pytest tests
    pytest.main(["-v", "backend/tests/"])