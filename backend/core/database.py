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

logger = logging.getLogger(__name__)

CERT_PATH = Path(__file__).parent.parent / "certs" / "supabase-prod.crt"

# Use settings.DATABASE_URL, which defaults to DATABASE_URL_SESSION from .env
url_obj = settings.DATABASE_URL
parsed_url = make_url(str(url_obj))
query_params = dict(parsed_url.query)

logger.info("\n===== DATABASE CONNECTION INFO =====\n")
logger.info(f"Database driver: {parsed_url.drivername}")
logger.info(f"Database host: {parsed_url.host}")
logger.info(f"Database port: {parsed_url.port}")
logger.info(f"Database name: {parsed_url.database}")
logger.info(f"Original query parameters: {query_params}")

ssl_context = ssl.create_default_context(cafile=str(CERT_PATH))
ssl_context.verify_mode = ssl.CERT_REQUIRED
ssl_context.check_hostname = True

async_url_obj = parsed_url.set(
    drivername="postgresql+asyncpg",
    query={k: v for k, v in query_params.items() if k not in ('sslmode', 'gssencmode')}
)

execution_options = {
    "isolation_level": "AUTOCOMMIT",
    "future": True,
    "logging_token": "legalvault-db"
}

async_engine = create_async_engine(
    async_url_obj,
    echo=False,
    poolclass=NullPool,  # Use NullPool to rely on pgBouncer
    connect_args={
        "ssl": ssl_context,
        "server_settings": {
            "application_name": "legalvault_backend",
            "statement_timeout": "60000",
            "standard_conforming_strings": "on",
            "client_min_messages": "warning",
            "client_encoding": "utf8"
        }
    },
    execution_options=execution_options,
)

logger.info("Database engine configured with session pooling settings:")
logger.info(f"  - Connection pooling: Using SQLAlchemy NullPool with Supabase pgBouncer")
logger.info(f"  - Prepared statements enabled (session mode)")

async_session_factory = sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False
)

async def handle_pgbouncer_error(session: AsyncSession, error: Exception) -> Optional[AsyncSession]:
    error_message = str(error).lower()
    if any(err in error_message for err in ["invalidsqlstatementnameerror", "max client connections reached", "connection closed"]):
        logger.warning(f"pgBouncer error detected: {error_message[:100]}...")
        try:
            await session.close()
            fresh_session = async_session_factory()
            await fresh_session.execute(text("SELECT 1"))
            return fresh_session
        except Exception as inner_e:
            logger.error(f"Failed to create replacement session: {str(inner_e)}")
            return None
    return None

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    logger.info("Entering get_db")
    session = None
    try:
        logger.info("Creating session")
        session = async_session_factory()
        logger.info("Session created successfully")
        
        logger.info("Executing test query: SELECT 1")
        await session.execute(text("SELECT 1"))
        logger.info("Test query succeeded")
        
        yield session
    except Exception as e:
        logger.info(f"Exception caught in get_db: {type(e).__name__}: {str(e)}")
        if session:
            await session.rollback()
        
        fresh_session = await handle_pgbouncer_error(session, e)
        if fresh_session:
            yield fresh_session
            return
        
        logger.error(f"Database connection error: {str(e)}")
        raise HTTPException(
            status_code=503,
            detail=f"Database connection failed. Please try again later. ({type(e).__name__})"
        )
    finally:
        if session:
            logger.info("Closing session")
            await session.close()
            logger.info("Session closed")

@asynccontextmanager
async def get_session_db():
    session = async_session_factory()
    try:
        await session.execute(text("SELECT 1"))
        yield session
        await session.commit()
    except Exception as e:
        await session.rollback()
        error_message = str(e).lower()
        if "json" in error_message and "serializable" in error_message:
            logger.error(f"JSON serialization error: {e}")
            raise ValueError(f"JSON serialization error: {str(e)}")
        else:
            logger.error(f"Database error in WebSocket session: {e}")
            raise
    finally:
        await session.close()

async def init_db() -> bool:
    try:
        logger.info("Attempting to initialize database...")
        async with async_engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
            await conn.execute(text("CREATE SCHEMA IF NOT EXISTS public"))
            await conn.execute(text("CREATE SCHEMA IF NOT EXISTS vault"))
            await conn.run_sync(SQLModel.metadata.create_all)
        logger.info("Database initialized successfully!")
        return True
    except Exception as e:
        logger.error(f"Error initializing database: {str(e)}")
        if settings.ENV == "development":
            logger.warning("Continuing despite error in development mode")
            return True
        return False

def get_pgbouncer_execution_options():
    return {}