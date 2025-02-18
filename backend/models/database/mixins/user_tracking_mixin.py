# models/database/mixins/user_tracking_mixin.py

from sqlalchemy import Column, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declared_attr

class UserAuditMixin:
    """Mixin for full user-based audit tracking"""

    @declared_attr
    def created_by(cls):
        return Column(
            UUID(as_uuid=True),
            ForeignKey("vault.users.id", ondelete="RESTRICT"),
            nullable=False,
            comment="User ID of record creator"
        )

    @declared_attr
    def modified_by(cls):
        return Column(
            UUID(as_uuid=True),
            ForeignKey("vault.users.id", ondelete="RESTRICT"),
            nullable=False,
            comment="User ID of last modifier"
        )
