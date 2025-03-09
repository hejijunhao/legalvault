# models/database/user.py

from sqlalchemy import Column, String, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from uuid import uuid4
from typing import TYPE_CHECKING, List
from models.database.base import VaultBase
from models.database.mixins import TimestampMixin

if TYPE_CHECKING:
    from models.database.research.public_searches import PublicSearch
    from models.database.enterprise import Enterprise
    from models.database.paralegal import VirtualParalegal

class User(VaultBase, TimestampMixin):
    __tablename__ = "users"  # Explicitly set to plural form to match Supabase naming convention
    
    auth_user_id = Column(UUID(as_uuid=True), ForeignKey('auth.users.id'), unique=True, nullable=False, index=True)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=True, index=True)
    role = Column(String, default="lawyer", nullable=False)
    virtual_paralegal_id = Column(UUID(as_uuid=True), ForeignKey('vault.virtual_paralegals.id'), index=True, nullable=True)
    enterprise_id = Column(UUID(as_uuid=True), ForeignKey('vault.enterprises.id'), index=True, nullable=True)

    # Temporarily comment out all relationships to fix circular import issues
    # enterprise = relationship(
    #     "Enterprise",
    #     lazy="selectin",
    #     foreign_keys=[enterprise_id]
    # )
    # virtual_paralegal = relationship(
    #     "VirtualParalegal",
    #     back_populates="user",
    #     lazy="selectin",
    #     uselist=False,
    #     primaryjoin="and_(models.database.user.User.virtual_paralegal_id==models.database.paralegal.VirtualParalegal.id, models.database.user.User.__table__.schema==models.database.paralegal.VirtualParalegal.__table__.schema)"
    # )
    # public_searches = relationship(
    #     "PublicSearch",
    #     back_populates="user",
    #     lazy="selectin",
    #     primaryjoin="and_(models.database.user.User.id==models.database.research.public_searches.PublicSearch.user_id, models.database.user.User.__table__.schema==models.database.research.public_searches.PublicSearch.__table__.schema)"
    # )
    def __repr__(self):
        return f"User(id={self.id}, name={self.name}, role={self.role})"