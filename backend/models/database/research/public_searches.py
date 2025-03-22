# models/database/research/public_searches.py

from sqlalchemy import Column, String, ForeignKey, Text, Boolean, Index
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from typing import Optional, List, TYPE_CHECKING
from models.database.base import PublicBase
from models.database.mixins.timestamp_mixin import TimestampMixin
from uuid import uuid4

if TYPE_CHECKING:
    from models.database.user import User
    from models.database.enterprise import Enterprise
    from models.database.research.public_search_messages import PublicSearchMessage

class PublicSearch(PublicBase, TimestampMixin):
    """
    Stores metadata about public search sessions across all enterprises.
    
    This table exists in the public schema as it contains cross-enterprise data.
    Each row represents a search conversation session initiated by a user.
    The actual messages/interactions are stored in a separate PublicSearchMessage table.
    """
    __tablename__ = "public_searches"
    
    # Create a composite index for efficient querying
    __table_args__ = (
        Index('ix_public_searches_enterprise_user', 'enterprise_id', 'user_id'),
        {'schema': 'public', 'extend_existing': True}  # Add extend_existing and preserve schema
    )
    
    # Search metadata
    title = Column(String, nullable=False, index=True, 
                  comment="Title of the search, initially the first query, can be edited by user")
    description = Column(Text, nullable=True,
                        comment="Optional user-provided description of this search")
    is_featured = Column(Boolean, default=False, nullable=False, index=True,
                        comment="Whether this search is featured/highlighted in the UI")
    tags = Column(JSONB, nullable=True, 
                 comment="Array of tags associated with this search")
    
    # User attribution
    user_id = Column(UUID(as_uuid=True), ForeignKey('public.users.id'), 
                    nullable=False, index=True,
                    comment="User who created this search")
    enterprise_id = Column(UUID(as_uuid=True), ForeignKey('public.enterprises.id'), 
                          nullable=True, index=True,
                          comment="Enterprise the user belongs to (optional)")
    
    # Search parameters/metadata
    search_params = Column(JSONB, nullable=True,
                          comment="Parameters used for this search (jurisdiction, practice area, etc.)")
    
    # Relationships - Simplified to avoid schema-related initialization issues
    user = relationship(
        "User",
        back_populates="public_searches",
        lazy="selectin"
    )
    
    # Comment out enterprise relationship until needed
    # enterprise = relationship(
    #     "Enterprise",
    #     lazy="selectin"
    # )
    
    messages = relationship(
        "PublicSearchMessage",
        back_populates="search",
        lazy="selectin",
        cascade="all, delete-orphan"
    )
    
    
    def __repr__(self):
        return f"PublicSearch(id={self.id}, title={self.title}, user_id={self.user_id})"