# alembic/migrations/env.py

import sys
import os
from pathlib import Path

# Add the project root directory to Python path
project_root = str(Path(__file__).parents[2])  # Go up two levels from alembic/env.py
sys.path.append(project_root)

from logging.config import fileConfig
from sqlalchemy import engine_from_config, MetaData
from sqlalchemy import pool
from alembic import context
from dotenv import load_dotenv

# Import only the migratable models (classes with tables, not mixins)
from models.database.user import User

# Create a custom MetaData object for the specific models you want to migrate
target_metadata = MetaData()
User.__table__.tometadata(target_metadata)

# Load environment variables
load_dotenv()

# This is the Alembic Config object, which provides access to the values within the .ini file in use.
config = context.config

# Set the sqlalchemy.url from environment variable
config.set_main_option("sqlalchemy.url", os.environ["DATABASE_URL"])

# Interpret the config file for Python logging.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        include_schemas=True,  # Ensure schema awareness for 'vault' and 'auth'
    )

    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    # Configure SSL and authentication settings
    connect_args = {
        "sslmode": "require",      # Use SSL
        "connect_timeout": 10,     # Connection timeout in seconds
        "gssencmode": "disable",   # Disable GSSAPI authentication which was causing errors
    }
    
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
        connect_args=connect_args
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, 
            target_metadata=target_metadata,
            include_schemas=True,  # Ensure schema awareness for 'vault' and 'auth'
        )

        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()