# backend/main.py

from dotenv import load_dotenv
# Load environment variables from .env before any imports that need them
load_dotenv()

from fastapi import FastAPI, Depends, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
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
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION
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
    # origins.append("https://app.legalvault.ai")
    # Add Vercel preview domains
    origins.append("https://*.vercel.app")
    logger.info("Running in production mode")

logger.info(f"Configured CORS origins: {origins}")

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["Content-Disposition"],  # Allow frontend to access Content-Disposition header for file downloads
)

app.include_router(api_router, prefix="/api")
app.include_router(webhook_router, prefix="/api/auth", tags=["auth"])


@app.get("/health")
async def health_check():
    return {"status": "healthy"}

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
            async with async_session_factory() as session:
                print("Successfully got database session")
                test_query = text("SELECT 1").execution_options(no_parameters=True)
                await session.execute(test_query)
                print("Database connection test successful!")
        except Exception as db_error:
            print(f"Database connection error: {db_error}")
            print(f"Error type: {type(db_error).__name__}")
            if "DuplicatePreparedStatementError" in str(db_error) or "prepared statement" in str(db_error):
                print("Detected pgBouncer prepared statement issue in startup check - this is expected")
                print("Application will continue starting up despite this error")
            else:
                import traceback
                print(traceback.format_exc())
                raise
    except Exception as e:
        print(f"Error during startup: {e}")
        print(f"Error type: {type(e).__name__}")
        import traceback
        print(traceback.format_exc())
        raise

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
