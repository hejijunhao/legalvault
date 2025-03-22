# models/database/research/public_search_messages.py

from sqlalchemy import Column, String, ForeignKey, Text, Integer, Index, Enum as SQLAlchemyEnum
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from typing import Optional, Dict, TYPE_CHECKING
from models.database.base import PublicBase
from models.database.mixins.timestamp_mixin import TimestampMixin
from models.enums.research_enums import QueryStatus

if TYPE_CHECKING:
    from models.database.research.public_searches import PublicSearch

class PublicSearchMessage(PublicBase, TimestampMixin):
    """
    Stores individual messages within a public search conversation.
    
    Each row represents a single message in the conversation, either from the user
    or the assistant (Perplexity API). The content is stored as JSONB to allow for
    rich content including citations, links, and metadata.
    """
    __tablename__ = "public_search_messages"
    __table_args__ = (
        Index('ix_public_search_messages_search_sequence', 'search_id', 'sequence'),
        {'schema': 'public'}  # Must include this even though it's in PublicBase, as this table_args overrides the PublicBase one completely.
    )
    
    # Link to parent search
    search_id = Column(UUID(as_uuid=True), ForeignKey('public.public_searches.id'), 
                      nullable=False, index=True,
                      comment="The search conversation this message belongs to")
    
    # Message data
    role = Column(String, nullable=False, index=True,
                 comment="Role of the message sender (user/assistant)")
    content = Column(JSONB, nullable=False,
                    comment="Message content including text and metadata")
    
    # Optional sequence number for ordering
    sequence = Column(Integer, nullable=False, default=0,
                     comment="Sequence number for ordering messages within a conversation")
    
    # Message status
    status = Column(SQLAlchemyEnum(QueryStatus), nullable=False, default=QueryStatus.PENDING, index=True,
                   comment="Status of the message (pending, completed, failed, etc.)")
    
    # Relationship to parent search
    search = relationship(
        "PublicSearch",
        back_populates="messages",
        lazy="selectin"
    )

    
    def __repr__(self):
        return f"PublicSearchMessage(id={self.id}, search_id={self.search_id}, role={self.role}, status={self.status})"


