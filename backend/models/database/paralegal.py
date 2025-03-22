# models/database/paralegal.py

from sqlalchemy import Column, String, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from typing import Optional, Dict, TYPE_CHECKING
from models.database.base import PublicBase
from models.database.mixins.timestamp_mixin import TimestampMixin
from uuid import uuid4

if TYPE_CHECKING:
    from .user import User
    # from .profile_picture import VPProfilePicture

class VirtualParalegal(PublicBase, TimestampMixin):
    # Explicitly setting table name to plural form instead of using auto-generated singular form
    __tablename__ = "virtual_paralegals"
    
    first_name = Column(String, nullable=False, index=True)
    last_name = Column(String, nullable=False, index=True)
    email = Column(String, nullable=False, unique=True)
    phone = Column(String, nullable=True)
    whatsapp = Column(String, nullable=True)
    # profile_picture_id = Column(UUID(as_uuid=True), ForeignKey('vault.vp_profile_pictures.id'), nullable=True, index=True)

    # Relationships are now defined in models.database.relationships
    # to avoid circular import issues
    
    @property
    def name(self):
        """Return the full name by combining first and last name"""
        return f"{self.first_name} {self.last_name}"
    
    def __repr__(self):
        return f"VirtualParalegal(id={self.id}, name={self.name}, email={self.email})"
