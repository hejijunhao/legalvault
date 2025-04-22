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

class VirtualParalegal(PublicBase, TimestampMixin):
    """Virtual Paralegal database model representing an AI assistant.
    
    This model stores the core attributes of a virtual paralegal in the public schema.
    It maintains relationships with users and profile pictures, and tracks basic
    identity information.
    
    Attributes:
        first_name (str): The VP's first name
        last_name (str): The VP's last name
        email (Optional[str]): Contact email, if applicable
        phone (Optional[str]): Contact phone number, if applicable
        whatsapp (Optional[str]): WhatsApp contact, if applicable
        gender (Optional[str]): VP's gender representation
    """
    __tablename__ = "virtual_paralegals"
    
    first_name: str = Column(String, nullable=False, index=True)
    last_name: str = Column(String, nullable=False, index=True)
    email: Optional[str] = Column(String, nullable=True, unique=True)
    phone: Optional[str] = Column(String, nullable=True)
    whatsapp: Optional[str] = Column(String, nullable=True)
    gender: Optional[str] = Column(String, nullable=True)
    
    def __repr__(self) -> str:
        """Return string representation of the Virtual Paralegal."""
        return f"VirtualParalegal(id={self.id}, first_name={self.first_name}, last_name={self.last_name})"
