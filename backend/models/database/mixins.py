# models/database/mixins.py

from datetime import datetime
from sqlalchemy import Column, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlmodel import Field, SQLModel


class TimestampMixin(SQLModel):
    """Mixin for timestamp tracking only"""
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        nullable=False,
        description="Timestamp when the record was created"
    )
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        nullable=False,
        description="Timestamp when the record was last updated"
    )

class UserAuditMixin(TimestampMixin):
    """Mixin for full user-based audit tracking"""
    created_by: UUID = Field(
        sa_column=Column(
            UUID(as_uuid=True),
            ForeignKey("vault.users.id", ondelete="RESTRICT"),
            nullable=False
        ),
        description="User ID of record creator"
    )
    modified_by: UUID = Field(
        sa_column=Column(
            UUID(as_uuid=True),
            ForeignKey("vault.users.id", ondelete="RESTRICT"),
            nullable=False
        ),
        description="User ID of last modifier"
    )