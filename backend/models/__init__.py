# backend/models/__init__.py

# Import models in dependency order to ensure SQLAlchemy metadata is populated correctly
# Base models and tables without foreign keys first
from .database.enterprise import Enterprise
from .database.paralegal import VirtualParalegal

# Then models with foreign keys
from .database.user import User
from .database.research.public_searches import PublicSearch
from .database.research.public_search_messages import PublicSearchMessage

# Import relationships last to set up late-binding relationships
from .database import relationships

# This ensures all models are registered with SQLAlchemy metadata in the correct order
# regardless of where they are imported in the application