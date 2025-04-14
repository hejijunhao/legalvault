# backend/main.py

from dotenv import load_dotenv
load_dotenv()

import logging
import json

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

logger.info("Starting LegalVault API server")
logger.info("Importing models to initialize SQLAlchemy metadata")
import models  # noqa: E402
logger.info("SQLAlchemy metadata initialized with all models")

from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from core.database import get_db, init_db, async_session_factory
import asyncio
from sqlalchemy.sql import text
from urllib.parse import urlparse

from api.routes import api_router
from api.routes.auth.webhooks import router as webhook_router
from core.config import settings

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="LegalVault API",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json"
)

# CORS
origins = set(settings.BACKEND_CORS_ORIGINS.split(","))
parsed_url = urlparse(settings.BASE_URL)
if "localhost" not in parsed_url.netloc and "127.0.0.1" not in parsed_url.netloc:
    origins.update([
        "https://legalvault.ai",
        "https://platform.legalvault.ai"
    ])

logger.info(f"Configured CORS origins: {', '.join(sorted(origins))}")

app.add_middleware(
    CORSMiddleware,
    allow_origins=list(origins),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["Content-Length", "Content-Range"],
    max_age=600,
)
logger.info("CORS middleware configured")

app.include_router(api_router, prefix="/api")
app.include_router(webhook_router, prefix="/api/webhooks")
logger.info("API routers included")

@app.on_event("startup")
async def startup_event():
    try:
        logger.info("Attempting to initialize database...")
        db_success = await init_db()
        if not db_success:
            logger.error("Database initialization failed")
            raise RuntimeError("Database initialization failed")
        logger.info("Database initialized successfully!")
        logger.info("Testing database connection...")
        async with async_session_factory() as session:
            logger.info("Successfully got database session")
            await session.execute(text("SELECT 1").execution_options(no_parameters=True))
            logger.info("Database connection test successful!")
    except Exception as e:
        logger.error(f"Startup error: {e}")
        raise

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    logger.error(f"HTTP Exception: {exc}")
    return JSONResponse(status_code=exc.status_code, content={"detail": str(exc.detail)})

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(status_code=500, content={"detail": "Internal server error"})

@app.get("/api/health")
async def health_check():
    logger.info("Received health check request")
    response = {"status": "ok", "version": settings.VERSION}
    logger.info("Returning health check response")
    return response