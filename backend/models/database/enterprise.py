# models/database/enterprise.py

from sqlmodel import SQLModel, Field, Relationship
from uuid import UUID, uuid4
from datetime import datetime
from typing import List, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from .user import User

class Enterprise(SQLModel, table=True):
    __tablename__ = "enterprises"
    __table_args__ = {'schema': 'vault'}

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    name: str = Field(index=True)
    domain: str = Field(unique=True)  # e.g. "lawfirm.com"
    subscription_tier: str = Field(default="standard")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationship
    users: List["User"] = Relationship(
        back_populates="enterprise",
        sa_relationship_kwargs={
            "lazy": "selectin",
            "primaryjoin": "and_(Enterprise.id==User.enterprise_id, "
                          "Enterprise.__table__.schema==User.__table__.schema)",
            "uselist": True  # Explicitly indicate one-to-many
        }
    )
