# backend/main.py

from fastapi import FastAPI, Depends, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os
from logging import getLogger
from typing import List
from core.database import get_db, init_db, async_session_factory
import asyncio
from sqlalchemy.sql import text

from api.routes import api_router
from api.routes.auth.webhooks import router as webhook_router
from core.config import settings


logger = getLogger(__name__)
app = FastAPI()

# Configure CORS - Use settings from config.py
origins = settings.BACKEND_CORS_ORIGINS

# In development, always include localhost
if not origins:
    logger.warning("No CORS origins configured. Using default development origins.")
    origins = [
        "http://localhost:3000",      # Local development HTTP
        "https://localhost:3000",     # Local development HTTPS
    ]
    # Log a warning in production
    if settings.ENV == "production":
        logger.error("WARNING: No CORS origins configured in production environment!")

logger.info(f"Configured CORS origins: {origins}")

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api")
app.include_router(webhook_router, prefix="/api/auth", tags=["auth"])


@app.get("/health")
async def health_check():
    return {"status": "healthy"}

# Load environment variables from .env
load_dotenv()

# Startup event to initialize database
@app.on_event("startup")
async def startup_event():
    try:
        # Initialize database tables
        print("Attempting to initialize database...")
        await init_db()
        print("Database initialized successfully!")
        
        # Test database connection
        print("Testing database connection...")
        try:
            # Create a session directly for testing instead of using the dependency
            async with async_session_factory() as session:
                print("Successfully got database session")
                # Use execute with a text object that explicitly disables prepared statements
                # by setting a unique name for each execution
                import uuid
                unique_stmt_name = f"stmt_{uuid.uuid4().hex}"
                stmt = text("SELECT NOW();").execution_options(
                    no_parameters=True,  # Helps with pgBouncer compatibility
                )
                result = await session.execute(stmt)
                current_time = result.scalar()
                print(f"Database connection successful! Current time: {current_time}")
        except Exception as db_error:
            print(f"Database connection error: {db_error}")
            print(f"Error type: {type(db_error).__name__}")
            # Check if this is a pgBouncer prepared statement issue
            if "DuplicatePreparedStatementError" in str(db_error) or "prepared statement" in str(db_error):
                print("Detected pgBouncer prepared statement issue in startup check - this is expected")
                print("Application will continue starting up despite this error")
            else:
                import traceback
                print(traceback.format_exc())
        
    except Exception as e:
        print(f"Error during startup: {e}")
        print(f"Error type: {type(e).__name__}")
        import traceback
        print(traceback.format_exc())
        # Don't raise here - allow the application to start even if DB init fails
        # This helps with debugging

# Error handling
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": str(exc.detail)}
    )

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    logger.error(f"Unhandled exception: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )
