# backend/core/database.py
import os
from sqlmodel import SQLModel
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from typing import AsyncGenerator
from dotenv import load_dotenv
from contextlib import asynccontextmanager

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("No DATABASE_URL found in environment")

# Create async engine with minimal configuration
async_engine = create_async_engine(
    DATABASE_URL,
    echo=True,
    future=True,
    poolclass=None  # Disable connection pooling as we're using pgbouncer
)

# Use async_sessionmaker instead of sessionmaker
async_session_maker = async_sessionmaker(
    async_engine,
    class_=AsyncSession,
    expire_on_commit=False
)

async def init_db() -> None:
    async with async_engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)

@asynccontextmanager
async def get_session() -> AsyncGenerator[AsyncSession, None]:
    session = async_session_maker()
    try:
        yield session
    finally:
        await session.close()