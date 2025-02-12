# models/database/user.py

from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, TYPE_CHECKING
from uuid import UUID, uuid4
from datetime import datetime

if TYPE_CHECKING:
    from .enterprise import Enterprise
    from .paralegal import VirtualParalegal

class User(SQLModel, table=True):
    __tablename__ = "users"
    __table_args__ = {'schema': 'vault'}

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    email: str = Field(unique=True, index=True)
    name: str
    role: str = Field(default="lawyer")
    virtual_paralegal_id: Optional[UUID] = Field(default=None, foreign_key="vault.virtual_paralegals.id", index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    enterprise_id: UUID = Field(foreign_key="vault.enterprises.id", index=True)

    # Relationships
    enterprise: Optional["Enterprise"] = Relationship(
        back_populates="users",
        sa_relationship_kwargs={
            "lazy": "selectin",
            "primaryjoin": "and_(User.enterprise_id==Enterprise.id, "
                           "User.__table__.schema==Enterprise.__table__.schema)"
        }
    )
    virtual_paralegal: Optional["VirtualParalegal"] = Relationship(
        back_populates="user",
        sa_relationship_kwargs={
            "lazy": "selectin",
            "uselist": False,
            "primaryjoin": "and_(User.virtual_paralegal_id==VirtualParalegal.id, "
                           "User.__table__.schema==VirtualParalegal.__table__.schema)"
        }
    )
