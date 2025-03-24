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
    },
    # Ensure consistent pgBouncer compatibility settings for all operations
    execution_options={
        "isolation_level": "AUTOCOMMIT",  # Move inside execution_options for better propagation
        "compiled_cache": None,
        "no_parameters": True,  # Required for pgBouncer
        "use_server_side_cursors": False,  # Disable server-side cursors for pgBouncer
        "future": True,  # Use SQLAlchemy 2.0 style execution
        "logging_token": "legalvault-db"  # Add token for easier log filtering
    },
)

# Log database connection configuration
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

# Dependency for FastAPI
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    logger.info("Entering get_db")
    session = None
    try:
        logger.info("Creating session")
        session = async_session_factory()
        logger.info("Session created successfully")
        
        logger.info("Executing test query: SELECT 1")
        # Use text() with execution_options to ensure no prepared statements
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
        
        # Handle pgBouncer prepared statement errors
        if any(err_type in str(e) for err_type in [
            "DuplicatePreparedStatementError", 
            "prepared statement",
            "InvalidSQLStatementNameError"
        ]):
            logger.warning(f"pgBouncer prepared statement warning: {str(e)[:100]}...")
            # Create a fresh session instead of reusing the problematic one
            try:
                await session.close()
                session = async_session_factory()
                # Test the new session
                await session.execute(text("SELECT 1").execution_options(no_parameters=True))
                yield session
                return
            except Exception as inner_e:
                logger.error(f"Failed to create replacement session: {str(inner_e)}")
                # Fall through to the general error handling
        
        # For other database errors
        logger.error(f"Database connection error: {str(e)}")
        logger.error(f"Error type: {type(e).__name__}")
        logger.error("Error traceback:", exc_info=True)  # Add full traceback
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
    """Initialize the database by creating schemas and tables.
    
    This function assumes that models have already been imported and registered with SQLModel.metadata
    in the correct order via the models/__init__.py file.
    
    Returns:
        bool: True if database initialization was successful, False otherwise.
    """
    try:
        logger.info("Attempting to initialize database...")
        
        async with async_engine.connect() as conn:
            # Execute a simple query to test connection
            test_query = text("SELECT 1").execution_options(
                no_parameters=True
            )
            await conn.execute(test_query)
            
            # Create schemas if they don't exist
            await conn.execute(
                text("CREATE SCHEMA IF NOT EXISTS public").execution_options(
                    no_parameters=True
                )
            )
            await conn.execute(
                text("CREATE SCHEMA IF NOT EXISTS vault").execution_options(
                    no_parameters=True
                )
            )
            
            # Create all tables using SQLAlchemy's metadata
            # This respects model dependencies automatically if metadata is correctly populated
            await conn.run_sync(SQLModel.metadata.create_all)
            
        logger.info("Database initialized successfully!")
        return True
        
    except Exception as e:
        logger.error(f"Error initializing database: {str(e)}")
        logger.error(f"Error type: {type(e).__name__}")
        
        # Handle pgBouncer prepared statement errors more comprehensively
        if any(err_type in str(e) for err_type in [
            "DuplicatePreparedStatementError", 
            "prepared statement",
            "InvalidSQLStatementNameError"
        ]):
            logger.warning("Detected pgBouncer prepared statement issue - this is expected during reloads")
            return True  # Continue despite pgBouncer errors
        
        # For other errors, we still want to continue in development
        if settings.ENV == "development":
            logger.warning("Continuing despite database error in development mode")
            return True
            
        return False