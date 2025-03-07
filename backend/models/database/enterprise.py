# models/database/enterprise.py

from sqlalchemy import Column, String
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from typing import List, TYPE_CHECKING
from models.database.base import VaultBase
from models.database.mixins.timestamp_mixin import TimestampMixin

if TYPE_CHECKING:
    from .user import User

class Enterprise(VaultBase, TimestampMixin):
    # Auto-generated table name would be 'enterprise', but we're using plural form
    __tablename__ = "enterprises"
    
    name = Column(String, nullable=False, index=True)
    domain = Column(String, nullable=False, unique=True)  # e.g. "lawfirm.com"
    subscription_tier = Column(String, default="standard", nullable=False)

    # Relationship - commented out for uni-directional relationship. Prev. removed type annotation to fix SQLAlchemy error
    # users = relationship(
    #     "User",
    #     back_populates="enterprise",
    #     lazy="selectin",
    #     uselist=True  # Explicitly indicate one-to-many
    # )

    def __repr__(self):
        return f"Enterprise(id={self.id}, name={self.name}, domain={self.domain})"
