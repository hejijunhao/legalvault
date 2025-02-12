# models/database/paralegal.py

from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, Dict, TYPE_CHECKING
from uuid import UUID, uuid4
from datetime import datetime
from sqlalchemy import JSON, Column

if TYPE_CHECKING:
    from .user import User
    from .profile_picture import VPProfilePicture

class VirtualParalegal(SQLModel, table=True):
    __tablename__ = "virtual_paralegals"
    __table_args__ = {'schema': 'vault'}

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    name: str = Field(index=True)
    email: str = Field(unique=True)
    phone: Optional[str] = None
    whatsapp: Optional[str] = None
    profile_picture_id: Optional[int] = Field(default=None, foreign_key="vault.vp_profile_pictures.id")
    abilities: list = Field(sa_column=Column(JSON), default=[])
    behaviors: Dict = Field(sa_column=Column(JSON), default={})
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    tech_tree_progress: Dict = Field(
        default={
            "unlocked_nodes": {},  # node_id -> unlock_timestamp
            "progress": {},  # node_id -> completion_percentage
            "metadata": {}  # Additional tracking data
        },
        sa_column=Column(JSON)
    )

    # Add relationship
    profile_picture: Optional["VPProfilePicture"] = Relationship(
        back_populates="virtual_paralegals",
        sa_relationship_kwargs={
            "lazy": "selectin",
            "primaryjoin": "and_(VirtualParalegal.profile_picture_id==VPProfilePicture.id, "
                           "VirtualParalegal.__table__.schema==VPProfilePicture.__table__.schema)"
        }
    )
    user: Optional["User"] = Relationship(
        back_populates="virtual_paralegal",
        sa_relationship_kwargs={
            "lazy": "selectin",
            "uselist": False,
            "primaryjoin": "and_(VirtualParalegal.id==User.virtual_paralegal_id, "
                           "VirtualParalegal.__table__.schema==User.__table__.schema)"
        }
    )
