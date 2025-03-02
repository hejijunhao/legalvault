# models/database/user.py

from sqlalchemy import Column, String, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
# from sqlalchemy.orm import relationship
from uuid import uuid4
from models.database.base import VaultBase
from models.database.mixins import TimestampMixin

class User(VaultBase, TimestampMixin):
    auth_user_id = Column(UUID(as_uuid=True), ForeignKey('auth.users.id'), unique=True, nullable=False, index=True)
    first_name = Column(String, nullable=False)  # Added: First name of the user
    last_name = Column(String, nullable=False)   # Added: Last name of the user
    name = Column(String, nullable=False)        # Added: Full name (could be derived from first_name + last_name)
    role = Column(String, default="lawyer", nullable=False)
    # virtual_paralegal_id = Column(UUID, ForeignKey('vault.virtual_paralegals.id'), index=True, nullable=True)
    # enterprise_id = Column(UUID, ForeignKey('vault.enterprises.id'), index=True, nullable=False)

    # enterprise = relationship(
    #     "Enterprise",
    #     back_populates="users",
    #     lazy="selectin",
    #     primaryjoin="and_(User.enterprise_id==Enterprise.id, User.__table__.schema==Enterprise.__table__.schema)"
    # )
    # virtual_paralegal = relationship(
    #    "VirtualParalegal",
    #     back_populates="user",
    #     lazy="selectin",
    #     uselist=False,
    #     primaryjoin="and_(User.virtual_paralegal_id==VirtualParalegal.id, User.__table__.schema==VirtualParalegal.__table__.schema)"
    # )

    def __repr__(self):
        return f"User(id={self.id}, name={self.name}, role={self.role})"