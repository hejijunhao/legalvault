# backend/main.py

from fastapi import FastAPI, Depends, HTTPException
from dotenv import load_dotenv
import os
from logging import getLogger
from typing import List
from core.database import get_db, init_db, async_session_factory
import asyncio
from sqlalchemy.sql import text

from api.routes import router as api_router

logger = getLogger(__name__)
app = FastAPI()

app.include_router(api_router, prefix="/api")

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
                result = await session.execute(text("SELECT NOW();"))
                current_time = result.scalar()
                print(f"Database connection successful! Current time: {current_time}")
        except Exception as db_error:
            print(f"Database connection error: {db_error}")
            print(f"Error type: {type(db_error).__name__}")
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
    return {"detail": str(exc.detail), "status_code": exc.status_code}

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    logger.error(f"Unhandled exception: {str(exc)}")
    return {"detail": "Internal server error", "status_code": 500}
