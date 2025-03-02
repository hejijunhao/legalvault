# backend/core/database.py

import os
import ssl
from sqlmodel import SQLModel, Session, create_engine
from contextlib import contextmanager
from dotenv import load_dotenv
from sqlalchemy.engine.url import make_url

load_dotenv()

# Get the connection string
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("No DATABASE_URL found in environment")

# Configure connection arguments for psycopg2
ssl_args = {
    "sslmode": "require",      # Use SSL
    "connect_timeout": 10,     # Connection timeout in seconds
    "gssencmode": "disable",   # Disable GSSAPI authentication which was causing errors
}

# Create engine with explicit driver specification
url = make_url(DATABASE_URL)
engine = create_engine(
    url.set(drivername="postgresql+psycopg2"),  # Explicitly set the driver
    echo=False,  # Set to False in production, True for debugging
    connect_args=ssl_args,
    pool_pre_ping=True,
    pool_size=5,
    max_overflow=10
)

def init_db():
    SQLModel.metadata.create_all(engine)

@contextmanager
def get_session():
    session = Session(engine)
    try:
        yield session
    finally:
        session.close()