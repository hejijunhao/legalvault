# backend/core/database.py

# Core database configuration for LegalVault that handles database connection setup.
# Configures async (asyncpg) database engine with pgBouncer compatibility,
# manages SSL and connection pooling settings, and provides database initialization functions.


import os
import ssl
from pathlib import Path
from typing import AsyncGenerator
import logging

from fastapi import HTTPException
from sqlalchemy import text
from sqlalchemy.engine.url import make_url
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool
from sqlmodel import SQLModel

from .config import settings

# Get logger for this module
logger = logging.getLogger(__name__)

# Get the path to the CA certificate
CERT_PATH = Path(__file__).parent.parent / "certs" / "supabase-prod.crt"

# Parse database URL and remove SSL-related query parameters (handled in connect_args)
url_obj = settings.DATABASE_URL
parsed_url = make_url(str(url_obj))
query_params = dict(parsed_url.query)

logger.info("\n===== DATABASE CONNECTION INFO =====\n")
logger.info(f"Database driver: {parsed_url.drivername}")
logger.info(f"Database host: {parsed_url.host}")
logger.info(f"Database port: {parsed_url.port}")
logger.info(f"Database name: {parsed_url.database}")
logger.info(f"Original query parameters: {query_params}")

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
    logger.info("Entering get_db")
    try:
        logger.info("Creating session")
        session = async_session_factory()
        logger.info("Session created successfully")
        
        logger.info("Executing test query: SELECT 1")
        test_query = text("SELECT 1").execution_options(no_parameters=True)
        await session.execute(test_query)
        logger.info("Test query succeeded")
        
        yield session
    except Exception as e:
        logger.info(f"Exception caught in get_db: {type(e).__name__}: {str(e)}")
        if session:
            await session.rollback()
        if "DuplicatePreparedStatementError" in str(e) or "prepared statement" in str(e):
            logger.warning(f"pgBouncer prepared statement warning (non-fatal): {str(e)[:100]}...")
            if session:
                yield session  # Still yield session for pgBouncer errors
        else:
            logger.error(f"Database connection error: {str(e)}")
            logger.error(f"Error type: {type(e).__name__}")
            logger.error(f"Error traceback:", exc_info=True)  # Add full traceback
            raise HTTPException(
                status_code=503,
                detail="Database connection failed. Please try again later."
            )
    finally:
        if session:
            logger.info("Closing session")
            await session.close()
            logger.info("Session closed")

# Database initialization function
async def init_db() -> bool:
    try:
        logger.info("Attempting to initialize database...")
        async with async_engine.connect() as conn:
            # Execute a simple query with no_parameters=True
            test_query = text("SELECT 1").execution_options(no_parameters=True)
            await conn.execute(test_query)
            
            # Create tables with explicit execution options
            await conn.run_sync(SQLModel.metadata.create_all)
            
        logger.info("Database initialized successfully!")
        return True
        
    except Exception as e:
        logger.error(f"Error initializing database: {str(e)}")
        logger.error(f"Error type: {type(e).__name__}")
        
        if "DuplicatePreparedStatementError" in str(e) or "prepared statement" in str(e):
            logger.warning("Detected pgBouncer prepared statement issue - this is expected during reloads")
            return True  # Continue despite pgBouncer errors
        
        # For other errors, we still want to continue in development
        if settings.ENV == "development":
            logger.warning("Continuing despite database error in development mode")
            return True
            
        return False