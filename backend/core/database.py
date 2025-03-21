# backend/core/database.py

# Core database configuration for LegalVault that handles database connection setup.
# Configures async (asyncpg) database engine with pgBouncer compatibility,
# manages SSL and connection pooling settings, and provides database initialization functions.


import os
import ssl
from pathlib import Path
from typing import AsyncGenerator

from fastapi import HTTPException
from sqlalchemy import text
from sqlalchemy.engine.url import make_url
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool
from sqlmodel import SQLModel

from .config import settings

# Get the path to the CA certificate
CERT_PATH = Path(__file__).parent.parent / "certs" / "supabase-prod.crt"

# Parse database URL and remove SSL-related query parameters (handled in connect_args)
url_obj = settings.DATABASE_URL
parsed_url = make_url(str(url_obj))
query_params = dict(parsed_url.query)

print("\n===== DATABASE CONNECTION INFO =====\n")
print(f"Database driver: {parsed_url.drivername}")
print(f"Database host: {parsed_url.host}")
print(f"Database port: {parsed_url.port}")
print(f"Database name: {parsed_url.database}")
print(f"Original query parameters: {query_params}")

# Create SSL context with Supabase CA certificate
ssl_context = ssl.create_default_context(cafile=str(CERT_PATH))
ssl_context.verify_mode = ssl.CERT_REQUIRED  # Enforce certificate verification
ssl_context.check_hostname = True  # Enable hostname verification

# Configure async engine with proper SSL and pgBouncer settings
# Remove SSL-related parameters from URL as they're handled in connect_args
async_url_obj = parsed_url.set(
    drivername="postgresql+asyncpg",
    query={k: v for k, v in query_params.items() if k not in ('sslmode', 'gssencmode')}
)

async_engine = create_async_engine(
    async_url_obj,
    echo=False,
    poolclass=NullPool,  # Required for pgBouncer
    connect_args={
        "ssl": ssl_context,
        "statement_cache_size": 0,  # Disable statement cache for pgBouncer
        "prepared_statement_cache_size": 0,  # Disable prepared statement cache
        "server_settings": {
            "application_name": "legalvault_backend",
            "statement_timeout": "60000",
            "standard_conforming_strings": "on",
            "client_min_messages": "warning",
            "client_encoding": "utf8"
        }
    }
).execution_options(
    isolation_level="AUTOCOMMIT",  # Required for pgBouncer
    compiled_cache=None,
    no_parameters=True
)

# Create session factory - execution_options will be set on the engine instead
async_session_factory = sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False
)

# Dependency for FastAPI
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    session = async_session_factory()
    try:
        # Simple connection test with no prepared statements
        test_query = text("SELECT 1").execution_options(no_parameters=True)
        await session.execute(test_query)
        yield session
    except Exception as e:
        await session.rollback()
        if "DuplicatePreparedStatementError" in str(e) or "prepared statement" in str(e):
            print(f"pgBouncer prepared statement warning (non-fatal): {str(e)[:100]}...")
            yield session  # Still yield session for pgBouncer errors
        else:
            print(f"Database connection error: {str(e)}")
            print(f"Error type: {type(e).__name__}")
            raise HTTPException(
                status_code=503,
                detail="Database connection failed. Please try again later."
            )
    finally:
        await session.close()

# Database initialization function
async def init_db() -> bool:
    try:
        print("Attempting to initialize database...")
        async with async_engine.connect() as conn:
            # Execute a simple query with no_parameters=True
            test_query = text("SELECT 1").execution_options(no_parameters=True)
            await conn.execute(test_query)
            
            # Create tables with explicit execution options
            await conn.run_sync(SQLModel.metadata.create_all)
            
        print("Database initialized successfully!")
        return True
        
    except Exception as e:
        print(f"Error initializing database: {str(e)}")
        print(f"Error type: {type(e).__name__}")
        
        if "DuplicatePreparedStatementError" in str(e) or "prepared statement" in str(e):
            print("Detected pgBouncer prepared statement issue - this is expected during reloads")
            return True  # Continue despite pgBouncer errors
        
        # For other errors, we still want to continue in development
        if settings.ENV == "development":
            print("Continuing despite database error in development mode")
            return True
            
        return False