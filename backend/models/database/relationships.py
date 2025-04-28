# models/database/relationships.py

"""
This module sets up SQLAlchemy relationships after all models are loaded
to avoid circular import issues.
"""
from sqlalchemy.orm import relationship
from sqlalchemy import and_

# Import all models that need relationships
from models.database.user import User
from models.database.enterprise import Enterprise
from models.database.paralegal import VirtualParalegal
from models.database.research.public_searches import PublicSearch
from models.database.research.public_search_messages import PublicSearchMessage
from models.database.vp_profile_picture import VPProfilePicture

# User relationships
User.enterprise = relationship(
    "Enterprise",
    back_populates="users",
    lazy="selectin",
    foreign_keys=[User.enterprise_id]
)

User.virtual_paralegal = relationship(
    "VirtualParalegal",
    back_populates="user",
    lazy="selectin",
    uselist=False
)

User.public_searches = relationship(
    "PublicSearch",
    back_populates="user",
    lazy="selectin"
)

# Enterprise relationships
Enterprise.users = relationship(
    "User",
    back_populates="enterprise",
    lazy="selectin",
    uselist=True
)

Enterprise.public_searches = relationship(
    "PublicSearch",
    back_populates="enterprise",
    lazy="selectin"
)

# VirtualParalegal relationships
VirtualParalegal.user = relationship(
    "User",
    back_populates="virtual_paralegal",
    lazy="selectin",
    uselist=False,
    primaryjoin="VirtualParalegal.id==User.virtual_paralegal_id"
)

VirtualParalegal.profile_picture = relationship(
    "VPProfilePicture",
    lazy="selectin",
    uselist=False,
    foreign_keys=[VirtualParalegal.profile_picture_id],
    back_populates="virtual_paralegals"
)

# VPProfilePicture relationships
VPProfilePicture.virtual_paralegals = relationship(
    "VirtualParalegal",
    back_populates="profile_picture",
    lazy="selectin",
    uselist=True
)

# PublicSearch relationships
PublicSearch.enterprise = relationship(
    "Enterprise",
    back_populates="public_searches",
    lazy="selectin",
    foreign_keys=[PublicSearch.enterprise_id]
)

PublicSearch.user = relationship(
    "User",
    back_populates="public_searches",
    lazy="selectin"
)

PublicSearch.messages = relationship(
    "PublicSearchMessage",
    back_populates="search",
    lazy="selectin",
    cascade="all, delete-orphan"
)

# PublicSearchMessage relationships
PublicSearchMessage.search = relationship(
    "PublicSearch",
    back_populates="messages",
    lazy="selectin"
)

# Remove the configure_mappers() call - SQLAlchemy will handle this automatically when needed