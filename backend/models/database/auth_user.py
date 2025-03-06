# backend/models/database/auth_user.py

from sqlalchemy import Column, String, Boolean, DateTime, Text, Integer
from sqlalchemy.dialects.postgresql import UUID, JSONB
from models.database.base import Base

class AuthUser(Base):
    __tablename__ = "users"
    __table_args__ = {"schema": "auth"}

    id = Column(UUID(as_uuid=True), primary_key=True)
    instance_id = Column(UUID(as_uuid=True))
    email = Column(String, nullable=False)
    encrypted_password = Column(String)  # Changed from hashed_password to match Supabase
    role = Column(String)
    aud = Column(String)
    email_confirmed_at = Column(DateTime(timezone=True))
    invited_at = Column(DateTime(timezone=True))
    confirmation_token = Column(String)
    confirmation_sent_at = Column(DateTime(timezone=True))
    recovery_token = Column(String)
    recovery_sent_at = Column(DateTime(timezone=True))
    email_change_token = Column(String)
    email_change = Column(String)
    email_change_sent_at = Column(DateTime(timezone=True))
    last_sign_in_at = Column(DateTime(timezone=True))
    raw_app_meta_data = Column(JSONB)
    raw_user_meta_data = Column(JSONB)
    is_super_admin = Column(Boolean)
    created_at = Column(DateTime(timezone=True))
    updated_at = Column(DateTime(timezone=True))
    phone = Column(Text)
    phone_confirmed_at = Column(DateTime(timezone=True))
    phone_change = Column(Text)
    phone_change_token = Column(String)
    phone_change_sent_at = Column(DateTime(timezone=True))
    confirmed_at = Column(DateTime(timezone=True))
    email_change_confirm_status = Column(Integer)
    banned_until = Column(DateTime(timezone=True))
    reauthentication_token = Column(String)
    reauthentication_sent_at = Column(DateTime(timezone=True))
    is_sso_user = Column(Boolean)
    deleted_at = Column(DateTime(timezone=True))
    is_anonymous = Column(Boolean)