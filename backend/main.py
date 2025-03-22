# backend/main.py

from dotenv import load_dotenv
# Load environment variables from .env before any imports that need them
load_dotenv()

from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import os
import logging
from typing import List, Dict, Any
from core.database import get_db, init_db, async_session_factory
import asyncio
from sqlalchemy.sql import text

from api.routes import api_router
from api.routes.auth.webhooks import router as webhook_router
from core.config import settings

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="LegalVault API",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json"
)

# Configure CORS
origins = settings.BACKEND_CORS_ORIGINS
if not origins:
    origins = [
        "http://localhost:3000",      # Local development HTTP
        "https://localhost:3000",     # Local development HTTPS
        "http://127.0.0.1:3000",     # Alternative local development HTTP
        "https://127.0.0.1:3000",    # Alternative local development HTTPS
        "http://localhost:8000",     # Backend local development
        "https://localhost:8000",    # Backend local development HTTPS
    ]

# In production, add production domains
if settings.ENV == "production":
    # Add your production domains when ready
    # origins.append("https://legalvault.ai")
    # origins.append("https://platform.legalvault.ai")
    pass

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

logger.info(f"Configured CORS origins: {','.join(origins)}")

# Include all routers
app.include_router(api_router, prefix="/api")
app.include_router(webhook_router, prefix="/api/webhooks")

@app.on_event("startup")
async def startup_event():
    """Initialize application on startup."""
    try:
        # Initialize database
        logger.info("Attempting to initialize database...")
        db_success = await init_db()
        if not db_success:
            db_error = "Database initialization failed"
            logger.error(f"Database connection error: {db_error}")
            logger.error(f"Error type: DatabaseInitializationError")
            
            if settings.ENV == "development":
                logger.warning("Application will continue starting up despite this error")
            else:
                raise RuntimeError(db_error)
                
        logger.info("Database initialized successfully!")
        logger.info("Testing database connection...")
        
        try:
            async with async_session_factory() as session:
                logger.info("Successfully got database session")
                test_query = text("SELECT 1").execution_options(no_parameters=True)
                await session.execute(test_query)
                logger.info("Database connection test successful!")
        except Exception as db_error:
            logger.error(f"Database connection error: {db_error}")
            logger.error(f"Error type: {type(db_error).__name__}")
            if "DuplicatePreparedStatementError" in str(db_error) or "prepared statement" in str(db_error):
                logger.info("Detected pgBouncer prepared statement issue in startup check - this is expected")
                logger.info("Application will continue starting up despite this error")
            else:
                import traceback
                logger.error(traceback.format_exc())
                raise
    except Exception as e:
        logger.error(f"Error during startup: {e}")
        logger.error(f"Error type: {type(e).__name__}")
        import traceback
        logger.error(traceback.format_exc())
        raise

# Error handling
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    logger.error(f"HTTP Exception: {exc}")
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": str(exc.detail)}
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )
