# backend/models/database/vp_profile_picture.py

from sqlalchemy import Column, String, ForeignKey, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from models.database.base import PublicBase
from models.database.mixins.timestamp_mixin import TimestampMixin
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .paralegal import VirtualParalegal

class VPProfilePicture(PublicBase, TimestampMixin):
    """Virtual Paralegal profile picture model.
    
    Stores profile picture information for virtual paralegals in the public schema.
    Each VP can have only one profile picture (enforced by unique constraint).
    
    Attributes:
        bucket_id (str): Storage bucket identifier, defaults to 'vp_profile_pictures'
        path (str): Path to the profile image file in the predefined set
        virtual_paralegal_id (UUID): Foreign key to the associated virtual paralegal
    """
    __tablename__ = "vp_profile_pictures"
    __table_args__ = (
        UniqueConstraint('virtual_paralegal_id'),
    )

    bucket_id: str = Column(String, nullable=False, default="vp_profile_pictures")
    path: str = Column(String, nullable=False)  # Path to predefined image, e.g., "default_1.jpg"
    virtual_paralegal_id: UUID = Column(UUID(as_uuid=True), ForeignKey('public.virtual_paralegals.id'), nullable=False)

    # Relationship to VP defined in relationships.py

    def __repr__(self) -> str:
        """Return string representation of the profile picture."""
        return f"VPProfilePicture(id={self.id}, virtual_paralegal_id={self.virtual_paralegal_id}, path={self.path})"