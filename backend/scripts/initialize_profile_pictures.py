# scripts/initialize_profile_pictures.py
from sqlmodel import Session
from models.database.profile_picture import VPProfilePicture
from core.database import engine

def initialize_profile_pictures():
    profile_pictures = [
        {
            "name": "Professional",
            "image_url": "/images/vp/professional.png",
            "display_order": 1,
        },
        {
            "name": "Casual",
            "image_url": "/images/vp/casual.png",
            "display_order": 2,
        },
        {
            "name": "Modern",
            "image_url": "/images/vp/modern.png",
            "display_order": 3,
        },
        {
            "name": "Traditional",
            "image_url": "/images/vp/traditional.png",
            "display_order": 4,
        },
        {
            "name": "Creative",
            "image_url": "/images/vp/creative.png",
            "display_order": 5,
        },
    ]
    
    with Session(engine) as session:
        # Check if pictures already exist
        existing = session.query(VPProfilePicture).count()
        if existing == 0:
            for picture in profile_pictures:
                db_picture = VPProfilePicture(**picture)
                session.add(db_picture)
            session.commit()

if __name__ == "__main__":
    initialize_profile_pictures()