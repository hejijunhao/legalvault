# tests/database/test_configuration.py

"""
Test database configuration and environment setup.
"""
import os
import pytest
from urllib.parse import urlparse
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_database_url_format():
    """Test DATABASE_URL format and structure"""
    db_url = os.getenv("DATABASE_URL")
    assert db_url is not None, "DATABASE_URL environment variable is not set"
    
    # Parse the URL
    parsed = urlparse(db_url)
    
    # Check URL structure
    assert parsed.scheme in ["postgresql", "postgres"], f"Invalid scheme: {parsed.scheme}"
    assert parsed.hostname is not None, "Hostname is missing"
    assert parsed.username is not None, "Username is missing"
    assert parsed.password is not None, "Password is missing"
    assert parsed.path.strip('/') != "", "Database name is missing"

def test_supabase_credentials():
    """Test Supabase credentials are available"""
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_KEY")
    
    assert supabase_url is not None, "SUPABASE_URL environment variable is not set"
    assert supabase_key is not None, "SUPABASE_KEY environment variable is not set"
    
    # Verify URL format
    assert supabase_url.startswith("https://"), "SUPABASE_URL should start with https://"
    assert ".supabase.co" in supabase_url, "SUPABASE_URL should contain .supabase.co"