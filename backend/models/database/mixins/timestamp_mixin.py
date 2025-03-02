# models/database/mixins/timestamp_mixin.py

from datetime import datetime
from sqlalchemy import Column, DateTime, func
from sqlalchemy.ext.declarative import declared_attr

class TimestampMixin:
    """Mixin for timestamp tracking only"""

    @declared_attr
    def created_at(cls):
        return Column(
            DateTime,
            nullable=False,
            server_default=func.now(),
            comment="Timestamp when the record was created"
        )

    @declared_attr
    def updated_at(cls):
        return Column(
            DateTime,
            nullable=False,
            server_default=func.now(),
            onupdate=func.now(),
            comment="Timestamp when the record was last updated"
        )