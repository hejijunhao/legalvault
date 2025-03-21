# backend/core/database.py

# Core database configuration for LegalVault that handles database connection setup.
# Configures both async (asyncpg) and sync (psycopg2) database engines with pgBouncer compatibility,
# manages SSL and connection pooling settings, and provides database initialization functions.


import os
import ssl
from pathlib import Path
from typing import AsyncGenerator

from fastapi import HTTPException
from sqlalchemy import create_engine, text
from sqlalchemy.engine.url import make_url
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool
from sqlmodel import SQLModel

from .config import settings

# Get the path to the CA certificate
CERT_PATH = Path(__file__).parent.parent / "certs" / "supabase-prod.crt"

# Parse database URL
url_obj = settings.DATABASE_URL
parsed_url = make_url(str(url_obj))

print("\n===== DATABASE CONNECTION INFO =====\n")
print(f"Database driver: {parsed_url.drivername}")
print(f"Database host: {parsed_url.host}")
print(f"Database port: {parsed_url.port}")
print(f"Database name: {parsed_url.database}")
print(f"Query parameters in URL: {dict(parsed_url.query)}")

# Create SSL context with Supabase CA certificate
ssl_context = ssl.create_default_context(cafile=str(CERT_PATH))
ssl_context.verify_mode = ssl.CERT_REQUIRED  # Enforce certificate verification
ssl_context.check_hostname = True  # Enable hostname verification

# Configure async engine with proper SSL and pgBouncer settings
async_url_obj = parsed_url.set(
    drivername="postgresql+asyncpg",
    query={}  # Remove query parameters, we'll handle these in connect_args
)

async_engine = create_async_engine(
    async_url_obj,
    echo=False,
    poolclass=NullPool,  # Required for pgBouncer
    connect_args={
        "ssl": ssl_context,
        "server_settings": {
            "application_name": "legalvault_backend",
            "statement_timeout": "60000",  # Must be string for asyncpg
            "standard_conforming_strings": "on",
            "client_min_messages": "warning",
            "client_encoding": "utf8"
        },
        "prepared_statement_cache_size": 0,
        "statement_cache_size": 0
    },
    execution_options={
        "isolation_level": "AUTOCOMMIT",  # Required for pgBouncer
        "compiled_cache": None,
        "no_parameters": True  # Disable parameter binding for pgBouncer compatibility
    }
)

# Configure sync engine with same SSL settings
sync_url_obj = parsed_url.set(drivername="postgresql+psycopg2")
print(f"Sync URL (credentials hidden): {sync_url_obj.render_as_string(hide_password=True)}")

sync_engine = create_engine(
    sync_url_obj,
    echo=False,
    poolclass=NullPool,
    connect_args={
        "sslmode": "require",
        "sslrootcert": str(CERT_PATH),
        "connect_timeout": 10,
        "application_name": "legalvault_backend_sync"
    }
)

# Create session factories
async_session_factory = sessionmaker(
    async_engine, class_=AsyncSession, expire_on_commit=False
)

# Dependency for FastAPI
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    session = async_session_factory()
    try:
        # Test connection with disabled prepared statements
        session = session.execution_options(compiled_cache=None)
        test_query = text("SELECT 1").execution_options(no_parameters=True)
        await session.execute(test_query)
        
        yield session
    except Exception as e:
        await session.rollback()
        
        # Handle pgBouncer-specific errors gracefully
        if "DuplicatePreparedStatementError" in str(e) or "prepared statement" in str(e):
            print(f"pgBouncer prepared statement warning (non-fatal): {str(e)[:100]}...")
            yield session
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
            # Set execution options to disable prepared statements
            conn = await conn.execution_options(compiled_cache=None)
            
            # Test query with disabled prepared statements
            test_query = text("SELECT 1").execution_options(no_parameters=True)
            await conn.execute(test_query)
            
            # Create all SQLModel tables
            await conn.run_sync(SQLModel.metadata.create_all)
            
        print("Database initialized successfully!")
        return True
        
    except Exception as e:
        print(f"Error initializing database: {str(e)}")
        print(f"Error type: {type(e).__name__}")
        
        # Handle pgBouncer-specific errors gracefully
        if "DuplicatePreparedStatementError" in str(e) or "prepared statement" in str(e):
            print("Detected pgBouncer prepared statement issue - this is expected during reloads")
            return True
            
        import traceback
        print(traceback.format_exc())
        return False