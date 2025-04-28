# api/routes/paralegal.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from models.schemas.paralegal import (
    VirtualParalegalCreate,
    VirtualParalegalUpdate,
    VirtualParalegalResponse,
)
from models.domain.paralegal_operations import (
    ParalegalOperations,
    ParalegalNotFoundError,
    ParalegalCreateError,
    ParalegalUpdateError,
)
from core.database import get_db
from core.auth import get_current_user
from models.database.user import User
from uuid import UUID
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/paralegals", tags=["Virtual Paralegals"])

@router.get("/me", response_model=VirtualParalegalResponse)
async def get_my_paralegal(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
):
    """Get the current user's Virtual Paralegal."""
    if not current_user.virtual_paralegal_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No Virtual Paralegal assigned"
        )
    
    paralegal_ops = ParalegalOperations(session)
    try:
        return await paralegal_ops.get_paralegal(current_user.virtual_paralegal_id)
    except ParalegalNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Virtual Paralegal not found"
        )
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.post("", response_model=VirtualParalegalResponse)
async def create_paralegal(
    data: VirtualParalegalCreate,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
):
    """Create a new Virtual Paralegal and assign it to the current user."""
    if current_user.virtual_paralegal_id:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User already has a Virtual Paralegal assigned"
        )
    
    paralegal_ops = ParalegalOperations(session)
    try:
        paralegal = await paralegal_ops.create_paralegal(data)
        
        # Update user's virtual_paralegal_id
        current_user.virtual_paralegal_id = paralegal.id
        session.add(current_user)
        await session.commit()
        
        return paralegal
    except ParalegalCreateError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.patch("/me", response_model=VirtualParalegalResponse)
async def update_my_paralegal(
    data: VirtualParalegalUpdate,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
):
    """Update the current user's Virtual Paralegal."""
    if not current_user.virtual_paralegal_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No Virtual Paralegal assigned"
        )
    
    paralegal_ops = ParalegalOperations(session)
    try:
        return await paralegal_ops.update_paralegal(current_user.virtual_paralegal_id, data)
    except ParalegalNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Virtual Paralegal not found"
        )
    except ParalegalUpdateError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )