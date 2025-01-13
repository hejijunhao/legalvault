import sys
import os
from pathlib import Path

# Add the project root directory to Python path
project_root = str(Path(__file__).parents[2])  # Go up two levels from alembic/env.py
sys.path.append(project_root)

from logging.config import fileConfig
from sqlalchemy import engine_from_config
from sqlalchemy import pool
from alembic import context
from dotenv import load_dotenv
from sqlmodel import SQLModel

#models
from models.database.user import User
from models.database.paralegal import VirtualParalegal
from models.database.ability import Ability
from models.database.ability_taskmanagement import TaskManagementAbility
from models.database.ability_receive_email import ReceiveEmailAbility
from models.database.profile_picture import VPProfilePicture
from models.database.behaviour import Behaviour, AbilityBehaviour, BehaviourVP
from models.database.longterm_memory.self_identity import SelfIdentity
from models.database.longterm_memory.global_knowledge import GlobalKnowledge
from models.database.longterm_memory.educational_knowledge import EducationalKnowledge

# Load environment variables
load_dotenv()

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Set the sqlalchemy.url from environment variable
config.set_main_option("sqlalchemy.url", os.environ["SYNC_DATABASE_URL"])

# Interpret the config file for Python logging.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

print("Available tables:", SQLModel.metadata.tables.keys())
# Set SQLModel metadata as target
target_metadata = SQLModel.metadata

def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()