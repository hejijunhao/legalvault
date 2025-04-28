# backend/models/database/vp_profile_picture.py

from sqlalchemy import Column, String, Text
from models.database.base import PublicBase
from models.database.mixins.timestamp_mixin import TimestampMixin

class VPProfilePicture(PublicBase, TimestampMixin):
    """Virtual Paralegal profile picture model.
    
    Stores reusable profile pictures that can be selected by virtual paralegals.
    Each profile picture represents a unique "character" that multiple VPs can use.
    
    Attributes:
        name (str): Display name for the profile picture (e.g., "Professional Woman 1")
        description (str): Optional description of the profile picture
        bucket_id (str): Storage bucket identifier, defaults to 'vp_profile_pictures'
        path (str): Path to the profile image file in storage
    """
    __tablename__ = "vp_profile_pictures"

    name: str = Column(String, nullable=False)
    description: str = Column(Text, nullable=True)
    bucket_id: str = Column(String, nullable=False, default="vp_profile_pictures")
    path: str = Column(String, nullable=False)  # Path to image in storage, e.g., "template_1.png"

    def __repr__(self) -> str:
        """Return string representation of the profile picture."""
        return f"VPProfilePicture(id={self.id}, name={self.name}, path={self.path})"