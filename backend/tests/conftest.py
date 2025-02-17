# backend/tests/conftest.py

import pytest
import logging
from pathlib import Path
import sys
from sqlmodel import SQLModel
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Add backend directory to Python path
current_dir = Path(__file__).resolve().parent
backend_dir = current_dir.parent
sys.path.insert(0, str(backend_dir))

# Set up SQLAlchemy logging
logging.basicConfig()
logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)
logging.getLogger('sqlalchemy.pool').setLevel(logging.DEBUG)


@pytest.fixture(scope="session")
def engine():
    """Create a test database engine"""
    DATABASE_URL = "postgresql://philippholke@localhost:5432/test_db"

    print("\n=== Creating Database Engine ===")
    engine = create_engine(
        DATABASE_URL,
        echo=True,  # SQL statements
        echo_pool=True  # Connection pool activity
    )

    print("\n=== Creating Schemas ===")
    with engine.connect() as conn:
        print("Creating public schema...")
        conn.execute(text('CREATE SCHEMA IF NOT EXISTS public'))
        print("Creating vault schema...")
        conn.execute(text('CREATE SCHEMA IF NOT EXISTS vault'))
        conn.commit()
        print("Schemas created successfully")

    print("\n=== Inspecting Metadata ===")
    print("Available tables:", SQLModel.metadata.tables.keys())
    for table in SQLModel.metadata.tables.values():
        print(f"\nTable: {table.name}")
        print(f"Schema: {table.schema}")
        print("Columns:", [c.name for c in table.columns])
        print("Constraints:", [c for c in table.constraints])
        print("Foreign Keys:", [f"{fk.parent}.{fk.column}" for fk in table.foreign_keys])

    print("\n=== Creating Tables ===")
    try:
        SQLModel.metadata.create_all(engine)
        print("Tables created successfully")
    except Exception as e:
        print(f"Error creating tables: {str(e)}")
        raise

    yield engine

    print("\n=== Cleaning Up ===")
    try:
        SQLModel.metadata.drop_all(engine)
        print("Tables dropped successfully")
    except Exception as e:
        print(f"Error dropping tables: {str(e)}")
        raise


@pytest.fixture
def session(engine):
    """Create a new database session for a test"""
    print("\n=== Creating New Session ===")
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = SessionLocal()
    try:
        yield session
    finally:
        print("\n=== Closing Session ===")
        session.close()