# alembic/migrations/env.py

import sys
import os
from pathlib import Path

# Add the project root directory to Python path
project_root = str(Path(__file__).parents[2])
sys.path.append(project_root)

from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool, MetaData
from alembic import context
from dotenv import load_dotenv

# Import the Base and models
from models.database.base import Base
from models.database.user import User
from models.database.auth_user import AuthUser

# Load environment variables
load_dotenv()

# This is the Alembic Config object
config = context.config

# Set the sqlalchemy.url from environment variable
database_url = os.environ["DATABASE_URL"]
if "gssencmode=disable" not in database_url:
    if "?" in database_url:
        database_url += "&gssencmode=disable"
    else:
        database_url += "?gssencmode=disable"
config.set_main_option("sqlalchemy.url", database_url)

# Interpret the config file for Python logging
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Create a custom metadata for migration
target_metadata = MetaData(naming_convention=Base.metadata.naming_convention)

# Only include tables you want to migrate
AuthUser.__table__.tometadata(target_metadata)
User.__table__.tometadata(target_metadata)


def include_name(name, type_, parent_names):
    # Only include objects in the 'vault' schema, and only include tables we explicitly add to target_metadata
    if type_ == "table":
        return parent_names.get("schema") == "vault"
    return True

def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        include_schemas=True,  # Ensure schema awareness for 'vault' and 'auth'
        include_name=include_name,  # Only include objects in the 'vault' schema
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
            include_name=include_name,  # Only include objects in the 'vault' schema
        )

        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()