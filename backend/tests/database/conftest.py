# tests/database/conftest.py

"""
Database-specific test fixtures.
"""
import os
import pytest
import psycopg2
from urllib.parse import urlparse
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

@pytest.fixture(scope="session")
def db_url():
    """Return the database URL from environment"""
    url = os.getenv("DATABASE_URL")
    assert url is not None, "DATABASE_URL environment variable is not set"
    return url

@pytest.fixture(scope="session")
def db_params(db_url):
    """Return parsed database connection parameters"""
    parsed = urlparse(db_url)
    return {
        "dbname": parsed.path.strip('/'),
        "user": parsed.username,
        "password": parsed.password,
        "host": parsed.hostname,
        "port": parsed.port,
        "sslmode": "require",
        "gssencmode": "disable"  # Explicitly disable GSSAPI
    }

@pytest.fixture(scope="function")
def psycopg2_connection(db_params):
    """Create a psycopg2 connection for testing"""
    connection = psycopg2.connect(**db_params)
    yield connection
    connection.close()

@pytest.fixture(scope="function")
def psycopg2_cursor(psycopg2_connection):
    """Create a psycopg2 cursor for testing"""
    cursor = psycopg2_connection.cursor()
    yield cursor
    cursor.close()