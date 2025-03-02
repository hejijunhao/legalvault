# models/database/base.py

from sqlalchemy import Column, DateTime, event, MetaData
from sqlalchemy.ext.declarative import declarative_base, declared_attr
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid

# Naming convention for constraints
convention = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s"
}

metadata = MetaData(naming_convention=convention)

class BaseModel:
    """Base class for all models"""
    
    @declared_attr
    def __tablename__(cls):
        # Convert CamelCase to snake_case
        return ''.join(['_' + c.lower() if c.isupper() else c for c in cls.__name__]).lstrip('_')
    
    id = Column(UUID, primary_key=True, default=uuid.uuid4)

# Core base for all models
Base = declarative_base(cls=BaseModel, metadata=metadata)

# Schema-specific bases
class VaultBase(Base):
    """Base for vault schema models"""
    __abstract__ = True
    __table_args__ = {'schema': 'vault'}

class PublicBase(Base):
    """Base for public schema models"""
    __table_args__ = {'schema': 'public'}

# class EnterpriseBase(Base):
#    """Base for enterprise schema models"""
#    __abstract__ = True
    
#    @declared_attr
#    def __table_args__(cls):
#        # This will be set dynamically for each enterprise
#        return {'schema': f'enterprise_{cls._enterprise_id}'}
