# services/executors/longterm_memory/self_identity_executor.py

from typing import Optional, Dict
from models.domain.longterm_memory.operations_self_identity import (
    SelfIdentityOperation,
    SelfIdentityOperationInput,
    SelfIdentityOperationOutput
)
from models.database.longterm_memory.self_identity import SelfIdentity
from core.database import get_session
from sqlmodel import select


class SelfIdentityExecutor:
    """Executor for self-identity operations."""

    def __init__(self):
        self.session = next(get_session())

    async def execute(
            self,
            operation_input: SelfIdentityOperationInput
    ) -> SelfIdentityOperationOutput:
        """Execute self-identity operation based on input."""
        try:
            if operation_input.operation == SelfIdentityOperation.GET:
                return await self._get_self_identity(operation_input.vp_id)
            elif operation_input.operation == SelfIdentityOperation.CREATE:
                return await self._create_self_identity(
                    operation_input.vp_id,
                    operation_input.prompt
                )
            elif operation_input.operation == SelfIdentityOperation.UPDATE:
                return await self._update_self_identity(
                    operation_input.vp_id,
                    operation_input.prompt
                )
            elif operation_input.operation == SelfIdentityOperation.DELETE:
                return await self._delete_self_identity(operation_input.vp_id)

        except Exception as e:
            return SelfIdentityOperationOutput(
                success=False,
                error=str(e)
            )

    async def _get_self_identity(self, vp_id: int) -> SelfIdentityOperationOutput:
        """Get self-identity for a specific VP."""
        query = select(SelfIdentity).where(SelfIdentity.vp_id == vp_id)
        result = self.session.exec(query).first()
        if not result:
            return SelfIdentityOperationOutput(
                success=False,
                error="Self-identity not found"
            )
        return SelfIdentityOperationOutput(
            success=True,
            data=result.dict()
        )

    async def _create_self_identity(
            self,
            vp_id: int,
            prompt: str
    ) -> SelfIdentityOperationOutput:
        """Create new self-identity."""
        self_identity = SelfIdentity(vp_id=vp_id, prompt=prompt)
        self.session.add(self_identity)
        self.session.commit()
        self.session.refresh(self_identity)
        return SelfIdentityOperationOutput(
            success=True,
            data=self_identity.dict()
        )

    async def _update_self_identity(
            self,
            vp_id: int,
            prompt: str
    ) -> SelfIdentityOperationOutput:
        """Update existing self-identity."""
        query = select(SelfIdentity).where(SelfIdentity.vp_id == vp_id)
        result = self.session.exec(query).first()
        if not result:
            return SelfIdentityOperationOutput(
                success=False,
                error="Self-identity not found"
            )
        result.prompt = prompt
        self.session.commit()
        self.session.refresh(result)
        return SelfIdentityOperationOutput(
            success=True,
            data=result.dict()
        )

    async def _delete_self_identity(self, vp_id: int) -> SelfIdentityOperationOutput:
        """Delete self-identity."""
        query = select(SelfIdentity).where(SelfIdentity.vp_id == vp_id)
        result = self.session.exec(query).first()
        if not result:
            return SelfIdentityOperationOutput(
                success=False,
                error="Self-identity not found"
            )
        self.session.delete(result)
        self.session.commit()
        return SelfIdentityOperationOutput(success=True)