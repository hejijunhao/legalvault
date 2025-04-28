# models/domain/paralegal_operations.py

from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from models.database.paralegal import VirtualParalegal
from models.schemas.paralegal import VirtualParalegalCreate, VirtualParalegalUpdate
from typing import Optional
import logging

logger = logging.getLogger(__name__)

class ParalegalNotFoundError(Exception):
    """Raised when a Virtual Paralegal is not found."""
    pass

class ParalegalCreateError(Exception):
    """Raised when Virtual Paralegal creation fails."""
    pass

class ParalegalUpdateError(Exception):
    """Raised when Virtual Paralegal update fails."""
    pass

class ParalegalOperations:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_paralegal(self, paralegal_id: UUID) -> VirtualParalegal:
        """Get a Virtual Paralegal by ID."""
        try:
            result = await self.db.execute(
                select(VirtualParalegal).where(VirtualParalegal.id == paralegal_id)
            )
            paralegal = result.scalar_one_or_none()
            if not paralegal:
                raise ParalegalNotFoundError(f"Virtual Paralegal {paralegal_id} not found")
            return paralegal
        except Exception as e:
            logger.error(f"Error getting paralegal {paralegal_id}: {str(e)}")
            raise

    async def create_paralegal(self, data: VirtualParalegalCreate) -> VirtualParalegal:
        """Create a new Virtual Paralegal."""
        try:
            paralegal = VirtualParalegal(**data.model_dump())
            self.db.add(paralegal)
            await self.db.commit()
            await self.db.refresh(paralegal)
            return paralegal
        except Exception as e:
            logger.error(f"Error creating paralegal: {str(e)}")
            await self.db.rollback()
            raise ParalegalCreateError(f"Failed to create Virtual Paralegal: {str(e)}")

    async def update_paralegal(
        self, paralegal_id: UUID, data: VirtualParalegalUpdate
    ) -> VirtualParalegal:
        """Update a Virtual Paralegal's details."""
        try:
            # First check if paralegal exists
            paralegal = await self.get_paralegal(paralegal_id)
            
            update_data = {k: v for k, v in data.model_dump().items() if v is not None}
            if not update_data:
                return paralegal

            await self.db.execute(
                update(VirtualParalegal)
                .where(VirtualParalegal.id == paralegal_id)
                .values(**update_data)
            )
            await self.db.commit()
            return await self.get_paralegal(paralegal_id)
        except ParalegalNotFoundError:
            raise
        except Exception as e:
            logger.error(f"Error updating paralegal {paralegal_id}: {str(e)}")
            await self.db.rollback()
            raise ParalegalUpdateError(f"Failed to update Virtual Paralegal: {str(e)}")