#backend/services/initializers/ability_receive_email.py
from typing import Dict, Optional
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy import select
from logging import getLogger

from backend.models.database.ability_receive_email import ReceiveEmailAbility
from backend.models.domain.operations_ability_receive_email import EMAIL_OPERATIONS, EmailOperation

logger = getLogger(__name__)

class ReceiveEmailInitializer:
    def __init__(self, session: AsyncSession):
        self.session = session

    def _create_operation(self, ability_id: int, operation: EmailOperation) -> ReceiveEmailAbility:
        workflow_steps_json = {
            "workflow_steps": [
                {
                    "name": step.name,
                    "type": step.type,
                    "description": step.description,
                    **({"config": step.config} if step.config else {})
                }
                for step in operation.workflow_steps
            ]
        }

        return ReceiveEmailAbility(
            ability_id=ability_id,
            operation_name=operation.operation_name,
            description=operation.description,
            input_schema=operation.input_schema,
            output_schema=operation.output_schema,
            workflow_steps=workflow_steps_json,
            constraints=operation.constraints,
            permissions=operation.permissions
        )

    async def initialize_operations(self, ability_id: int) -> Dict[str, int]:
        operation_ids = {}
        try:
            for operation in EMAIL_OPERATIONS.values():
                stmt = select(ReceiveEmailAbility).where(
                    ReceiveEmailAbility.ability_id == ability_id,
                    ReceiveEmailAbility.operation_name == operation.operation_name
                )
                result = await self.session.execute(stmt)
                existing = result.scalar_one_or_none()

                if existing:
                    logger.info(f"Operation {operation.operation_name} already exists")
                    operation_ids[operation.operation_name] = existing.id
                    continue

                db_operation = self._create_operation(ability_id, operation)
                self.session.add(db_operation)
                await self.session.flush()
                operation_ids[operation.operation_name] = db_operation.id
                logger.info(f"Created operation {operation.operation_name}")

            await self.session.commit()
            return operation_ids
        except Exception as e:
            await self.session.rollback()
            logger.error(f"Error initializing email operations: {str(e)}")
            raise

    async def update_operation(self, operation_name: str, updates: Dict) -> bool:
        try:
            stmt = select(ReceiveEmailAbility).where(
                ReceiveEmailAbility.operation_name == operation_name
            )
            result = await self.session.execute(stmt)
            operation = result.scalar_one_or_none()

            if not operation:
                logger.warning(f"Operation {operation_name} not found")
                return False

            for field, value in updates.items():
                if hasattr(operation, field):
                    setattr(operation, field, value)

            await self.session.commit()
            logger.info(f"Updated operation {operation_name}")
            return True
        except Exception as e:
            await self.session.rollback()
            logger.error(f"Error updating operation {operation_name}: {str(e)}")
            raise

    async def get_operation(self, operation_name: str) -> Optional[ReceiveEmailAbility]:
        stmt = select(ReceiveEmailAbility).where(
            ReceiveEmailAbility.operation_name == operation_name
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
