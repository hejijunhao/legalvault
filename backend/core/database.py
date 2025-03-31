# backend/core/database.py

# Core database configuration for LegalVault that handles database connection setup.
# Configures async (asyncpg) database engine with pgBouncer compatibility,
# manages SSL and connection pooling settings, and provides database initialization functions.

import os
import ssl
import json
from pathlib import Path
from typing import AsyncGenerator, Optional, Dict, Any
import logging
from contextlib import asynccontextmanager

from fastapi import HTTPException
from sqlalchemy import text, Table, MetaData
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
async_url_obj = parsed_url.set(
    drivername="postgresql+asyncpg",
    query={k: v for k, v in query_params.items() if k not in ('sslmode', 'gssencmode')}
)

# Define execution options to be used consistently across all queries
pgbouncer_execution_options = {
    "isolation_level": "AUTOCOMMIT",
    "compiled_cache": None,
    "no_parameters": True,  # Required for pgBouncer
    "use_server_side_cursors": False,  # Disable server-side cursors for pgBouncer
    "future": True,  # Use SQLAlchemy 2.0 style execution
    "logging_token": "legalvault-db"
}

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
    },
    execution_options=pgbouncer_execution_options,
)

logger.info("Database engine configured with pgBouncer compatibility settings:")
logger.info(f"  - Connection pooling: Using SQLAlchemy NullPool with pgBouncer")
logger.info(f"  - Statement cache disabled: statement_cache_size=0")
logger.info(f"  - Prepared statement cache disabled: prepared_statement_cache_size=0")
logger.info(f"  - Server-side cursors disabled: use_server_side_cursors=False")
logger.info(f"  - Parameter binding disabled: no_parameters=True")
logger.info(f"  - Using SQLAlchemy 2.0 style execution: future=True")
logger.info(f"  - Statement timeout set to: 60 seconds")

# Create session factory with pgBouncer-compatible options
async_session_factory = sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False
)

# Helper to handle pgBouncer errors
async def handle_pgbouncer_error(session: AsyncSession, error: Exception) -> Optional[AsyncSession]:
    """
    Handle pgBouncer related errors by creating a fresh session.
    Returns a new session if successful, None if failed.
    """
    error_message = str(error).lower()
    if any(err_type in error_message for err_type in [
        "duplicatepreparedstatementerror", 
        "prepared statement",
        "invalidsqlstatementnameerror"
    ]):
        logger.warning(f"pgBouncer prepared statement warning detected: {error_message[:100]}...")
        try:
            # Close the problematic session
            if session:
                await session.close()
            
            # Create a fresh session
            fresh_session = async_session_factory()
            
            # Test the connection with a simple query
            test_query = text("SELECT 1").execution_options(
                no_parameters=True, 
                use_server_side_cursors=False
            )
            await fresh_session.execute(test_query)
            
            return fresh_session
        except Exception as inner_e:
            logger.error(f"Failed to create replacement session: {str(inner_e)}")
            if fresh_session:
                await fresh_session.close()
            return None
    return None

# Dependency for FastAPI HTTP requests
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    logger.info("Entering get_db")
    session = None
    try:
        logger.info("Creating session")
        session = async_session_factory()
        logger.info("Session created successfully")
        
        logger.info("Executing test query: SELECT 1")
        test_query = text("SELECT 1").execution_options(
            no_parameters=True, 
            use_server_side_cursors=False
        )
        await session.execute(test_query)
        logger.info("Test query succeeded")
        
        yield session
    except Exception as e:
        logger.info(f"Exception caught in get_db: {type(e).__name__}: {str(e)}")
        if session:
            await session.rollback()
        
        # Handle pgBouncer errors
        fresh_session = await handle_pgbouncer_error(session, e)
        if fresh_session:
            yield fresh_session
            return
        
        # If we couldn't recover, raise a helpful error
        logger.error(f"Database connection error: {str(e)}")
        logger.error(f"Error type: {type(e).__name__}")
        logger.error("Error traceback:", exc_info=True)
        raise HTTPException(
            status_code=503,
            detail=f"Database connection failed. Please try again later. ({type(e).__name__})"
        )
    finally:
        if session:
            logger.info("Closing session")
            await session.close()
            logger.info("Session closed")

# Dependency for WebSocket connections
@asynccontextmanager
async def get_session_db():
    """
    Context manager for short-lived database sessions.
    Designed for WebSocket operations where we need independent transaction scopes.
    """
    session = async_session_factory()
    try:
        # Test connection with simple query
        await session.execute(
            text("SELECT 1").execution_options(
                no_parameters=True, 
                use_server_side_cursors=False
            )
        )
        
        yield session
        await session.commit()
    except Exception as e:
        await session.rollback()
        
        # Handle JSON serialization errors for WebSockets
        error_message = str(e).lower()
        if "json" in error_message and "serializable" in error_message:
            logger.error(f"JSON serialization error in WebSocket session: {e}")
            # This might be an issue with UUID serialization
            raise ValueError(f"JSON serialization error: {str(e)}")
        elif any(err_type in error_message for err_type in [
            "duplicatepreparedstatementerror", 
            "prepared statement",
            "invalidsqlstatementnameerror"
        ]):
            logger.warning(f"pgBouncer error in WebSocket session: {e}")
            # WebSocket handler should retry with a fresh session
            raise ValueError(f"pgBouncer error: {str(e)}")
        else:
            logger.error(f"Database error in WebSocket session: {e}")
            raise
    finally:
        await session.close()

# Database initialization function
async def init_db() -> bool:
    """
    Initialize the database with required schemas and tables.
    Returns True if successful, False if failed.
    """
    try:
        logger.info("Attempting to initialize database...")
        
        async with async_engine.connect() as conn:
            # Test connection
            test_query = text("SELECT 1").execution_options(no_parameters=True)
            await conn.execute(test_query)
            
            # Create necessary schemas
            await conn.execute(
                text("CREATE SCHEMA IF NOT EXISTS public").execution_options(no_parameters=True)
            )
            await conn.execute(
                text("CREATE SCHEMA IF NOT EXISTS vault").execution_options(no_parameters=True)
            )
            
            # Create tables based on SQLModel metadata
            await conn.run_sync(SQLModel.metadata.create_all)
            
        logger.info("Database initialized successfully!")
        return True
        
    except Exception as e:
        logger.error(f"Error initializing database: {str(e)}")
        logger.error(f"Error type: {type(e).__name__}")
        
        # Handle pgBouncer errors specially
        if any(err_type in str(e).lower() for err_type in [
            "duplicatepreparedstatementerror", 
            "prepared statement",
            "invalidsqlstatementnameerror"
        ]):
            logger.warning("Detected pgBouncer prepared statement issue - expected during reloads")
            return True
        
        # In development, continue despite errors
        if settings.ENV == "development":
            logger.warning("Continuing despite database error in development mode")
            return True
            
        return False

# Function to get pgBouncer-compatible execution options
def get_pgbouncer_execution_options():
    """Return standard execution options for pgBouncer compatibility"""
    return {
        "no_parameters": True,
        "use_server_side_cursors": False
    }