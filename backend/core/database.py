# backend/core/database.py

import os
import ssl
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool
from sqlmodel import SQLModel, Session
from contextlib import asynccontextmanager
from dotenv import load_dotenv
from sqlalchemy.engine.url import make_url
from fastapi import Depends
from sqlalchemy import create_engine
from sqlalchemy import text

load_dotenv()

# Get the connection string
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("No DATABASE_URL found in environment")

# Print diagnostic information about the connection string
# (Be careful not to print the full connection string with credentials)
print(f"\n===== DATABASE CONNECTION INFO =====\n")
url_obj = make_url(DATABASE_URL)
print(f"Database driver: {url_obj.drivername}")
print(f"Database host: {url_obj.host}")
print(f"Database port: {url_obj.port}")
print(f"Database name: {url_obj.database}")
print(f"Query parameters in URL: {dict(url_obj.query)}")

# For asyncpg, we need to modify the URL
# Use connect_args instead of query parameters for SSL and other settings
async_url_obj = url_obj.set(
    drivername="postgresql+asyncpg",
    query={}
)
print(f"Modified async URL (credentials hidden): {async_url_obj.render_as_string(hide_password=True)}")

# For psycopg2, keep the original query parameters
sync_url_obj = url_obj.set(drivername="postgresql+psycopg2")
print(f"Sync URL (credentials hidden): {sync_url_obj.render_as_string(hide_password=True)}")

print("\n===== END DATABASE CONNECTION INFO =====\n")

# Create SSL context if needed
ssl_context = None
if url_obj.query.get("sslmode") == "require":
    # Create an SSL context that doesn't verify certificates
    # This is needed because Supabase appears to be using a self-signed certificate
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE

# Configure connection arguments for asyncpg with pgBouncer compatibility
async_connect_args = {
    # These settings are critical for pgBouncer compatibility
    "statement_cache_size": 0,
    "prepared_statement_cache_size": 0,
    "command_timeout": 60,
    # Explicitly disable prepared statements for pgBouncer compatibility
    "server_settings": {
        "statement_timeout": "10000",  # 10 seconds
        "application_name": "LegalVault",
        "prepared_statements": "false"  # Explicitly disable prepared statements
    }
}

# Add SSL context if needed
if ssl_context:
    async_connect_args["ssl"] = ssl_context

# Configure connection arguments for psycopg2
# No need to specify sslmode here as it's already in the URL
ssl_args_sync = {
    "connect_timeout": 10,     # Connection timeout in seconds
}

# Create engines with the appropriate SSL args and URLs
async_engine = create_async_engine(
    async_url_obj.render_as_string(hide_password=False),  # Use the full URL string
    echo=True,  # Set to True for debugging
    connect_args=async_connect_args,
    poolclass=NullPool,  # Disable connection pooling to avoid pgBouncer issues
    pool_pre_ping=True,
    execution_options={
        "isolation_level": "AUTOCOMMIT",  # Helps with pgBouncer in transaction mode
        "use_native_hstore": False,       # Disable native hstore to avoid prepared statements
        "use_native_uuid": False,         # Disable native UUID to avoid prepared statements
        "use_native_json": False          # Disable native JSON to avoid prepared statements
    }
)

# Create a separate sync engine for backward compatibility
sync_engine = create_engine(
    sync_url_obj,
    echo=False,
    connect_args=ssl_args_sync,
    pool_pre_ping=True,
    pool_size=5,
    max_overflow=10
)

# Create async session factory
async_session_factory = sessionmaker(
    async_engine, class_=AsyncSession, expire_on_commit=False
)

async def init_db():
    try:
        print("Attempting to initialize database...")
        # Use connect() instead of begin() to have more control
        async with async_engine.connect() as conn:
            # Test connection with a simple query that doesn't use prepared statements
            await conn.execute(text("SELECT 1"))
            # Then run the schema creation
            await conn.run_sync(SQLModel.metadata.create_all)
        print("Database initialized successfully!")
        return True
    except Exception as e:
        print(f"Error initializing database: {e}")
        print(f"Error type: {type(e).__name__}")
        # Check if this is a DuplicatePreparedStatementError
        if "DuplicatePreparedStatementError" in str(e) or "prepared statement" in str(e):
            print("Detected pgBouncer prepared statement issue - this is expected during reloads")
            # Consider this a non-fatal error during development
            print("Database initialization continuing despite pgBouncer error")
            return True
        import traceback
        print(traceback.format_exc())
        # Don't raise here - allow the application to start even if DB init fails
        # This helps with debugging
        return False

# Async context manager for FastAPI dependency injection
@asynccontextmanager
async def get_async_session():
    async with async_session_factory() as session:
        try:
            yield session
        finally:
            pass  # Don't explicitly close the session here, it will be closed by the context manager

# FastAPI dependency
async def get_db():
    # Create a new session for each request
    session = async_session_factory()
    try:
        # Use the session in the request
        yield session
    finally:
        # Close the session when the request is done
        await session.close()


# Backward compatibility for existing code
# This will allow existing code to continue working while you migrate
def get_session():
    # Use the dedicated sync engine we created above
    session = Session(sync_engine)
    try:
        yield session
    finally:
        session.close()