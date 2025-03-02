# backend/models/database/auth_user.py

from sqlalchemy import Column, String, Boolean, DateTime
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class AuthUser(Base):
    __tablename__ = "users"
    __table_args__ = {"schema": "auth"}

    id = Column(UUID(as_uuid=True), primary_key=True)
    email = Column(String, nullable=False)
    role = Column(String)
    phone = Column(String)
    email_confirmed_at = Column(DateTime(timezone=True))
    phone_confirmed_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True))
    updated_at = Column(DateTime(timezone=True))
    last_sign_in_at = Column(DateTime(timezone=True))
    raw_app_meta_data = Column(JSONB)
    raw_user_meta_data = Column(JSONB)
    is_super_admin = Column(Boolean)
    is_sso_user = Column(Boolean)
    is_anonymous = Column(Boolean)