# tests/database/test_connection.py

"""
Test direct database connection using psycopg2.
"""
import pytest

def test_direct_connection(psycopg2_cursor):
    """Test direct database connection with psycopg2"""
    # Execute a simple query
    psycopg2_cursor.execute("SELECT 1 as test")
    result = psycopg2_cursor.fetchone()
    
    # Verify result
    assert result[0] == 1, "Database query did not return expected result"

def test_connection_parameters(db_params, psycopg2_cursor):
    """Test connection using individual parameters"""
    # The connection is already established using the fixtures
    # Just verify we can execute a query
    psycopg2_cursor.execute("SELECT 1 as test")
    result = psycopg2_cursor.fetchone()
    
    # Verify result
    assert result[0] == 1, "Database query did not return expected result"
    
    # Also verify we have the expected parameters
    assert db_params["gssencmode"] == "disable", "GSSAPI should be disabled"
    assert db_params["sslmode"] == "require", "SSL should be required"