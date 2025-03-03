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
    auth_user_id = Column(UUID(as_uuid=True), ForeignKey('auth.users.id'), unique=True, nullable=False, index=True)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    name = Column(String, nullable=False)
    role = Column(String, default="lawyer", nullable=False)
    virtual_paralegal_id = Column(UUID(as_uuid=True), ForeignKey('vault.virtual_paralegals.id'), index=True, nullable=True)
    enterprise_id = Column(UUID(as_uuid=True), ForeignKey('vault.enterprises.id'), index=True, nullable=True)

    enterprise = relationship(
        "Enterprise",
        back_populates="users",
        lazy="selectin",
        primaryjoin="and_(User.enterprise_id==Enterprise.id, User.__table__.schema==Enterprise.__table__.schema)"
    )
    virtual_paralegal = relationship(
        "VirtualParalegal",
         back_populates="user",
         lazy="selectin",
         uselist=False,
         primaryjoin="and_(User.virtual_paralegal_id==VirtualParalegal.id, User.__table__.schema==VirtualParalegal.__table__.schema)"
     )
    public_searches = relationship(
        "PublicSearch",
        back_populates="user",
        lazy="selectin",
        primaryjoin="and_(User.id==PublicSearch.user_id, User.__table__.schema==PublicSearch.__table__.schema)"
    )


    def __repr__(self):
        return f"User(id={self.id}, name={self.name}, role={self.role})"