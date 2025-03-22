# models/database/user.py

from models.database.enterprise import Enterprise
from sqlalchemy import Column, String, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from uuid import uuid4
from typing import TYPE_CHECKING, List
from models.database.base import PublicBase
from models.database.mixins import TimestampMixin

if TYPE_CHECKING:
    from models.database.research.public_searches import PublicSearch
    # Keep type hints for future use
    from models.database.paralegal import VirtualParalegal

class User(PublicBase, TimestampMixin):
    __tablename__ = "users"  # Explicitly set to plural form to match Supabase naming convention
    
    auth_user_id = Column(UUID(as_uuid=True), ForeignKey('auth.users.id'), unique=True, nullable=False, index=True)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=True, index=True)
    role = Column(String, default="lawyer", nullable=False)
    virtual_paralegal_id = Column(UUID(as_uuid=True), ForeignKey('virtual_paralegals.id'), index=True, nullable=True)
    enterprise_id = Column(UUID(as_uuid=True), ForeignKey('enterprises.id'), index=True, nullable=True)

    # Relationships are now defined in models.database.relationships
    # to avoid circular import issues

    def __repr__(self):
        return f"User(id={self.id}, name={self.name}, role={self.role})"
