# api/routes/profile_pictures.py
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from core.database import get_session
from models.database.profile_picture import VPProfilePicture
from models.database.virtual_paralegal import VirtualParalegal
from models.schemas.profile_picture import VPProfilePictureRead, ProfilePictureUpdate, VPProfileResponse

router = APIRouter(prefix="/vp", tags=["virtual_paralegal"])

@router.get("/profile-pictures", response_model=List[VPProfilePictureRead])
async def get_profile_pictures(
    session: Session = Depends(get_session)
):
    """Get all available profile pictures"""
    statement = select(VPProfilePicture).where(
        VPProfilePicture.is_active == True
    ).order_by(VPProfilePicture.display_order)
    
    pictures = session.exec(statement).all()
    return pictures

@router.put("/{vp_id}/profile-picture", response_model=VPProfileResponse)
async def update_profile_picture(
    vp_id: int,
    update: ProfilePictureUpdate,
    session: Session = Depends(get_session)
):
    """Update a VP's profile picture"""
    # Check if profile picture exists and is active
    picture = session.get(VPProfilePicture, update.profile_picture_id)
    if not picture or not picture.is_active:
        raise HTTPException(
            status_code=404,
            detail="Profile picture not found or inactive"
        )
    
    # Get and update VP
    vp = session.get(VirtualParalegal, vp_id)
    if not vp:
        raise HTTPException(
            status_code=404,
            detail="Virtual Paralegal not found"
        )
    
    vp.profile_picture_id = update.profile_picture_id
    session.add(vp)
    session.commit()
    session.refresh(vp)
    
    return VPProfileResponse(
        message="Profile picture updated successfully",
        profile_picture_id=vp.profile_picture_id
    )