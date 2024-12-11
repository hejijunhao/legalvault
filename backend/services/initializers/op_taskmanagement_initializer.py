# backend/services/initializers/op_taskmanagement_initializer.py
from typing import Dict
from sqlmodel import Session
from logging import getLogger

from backend.models.database.ability_taskmanagement import TaskManagementAbility
from backend.models.domain.operations_taskmanagement import TASK_OPERATIONS, TaskOperation

logger = getLogger(__name__)


class TaskManagementInitializer:
    def __init__(self, session: Session):
        self.session = session

    def _create_operation(self, techtree_id: int, operation: TaskOperation) -> TaskManagementAbility:
        """Creates a single operation in the database"""
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

        return TaskManagementAbility(
            techtree_id=techtree_id,
            operation_name=operation.operation_name,
            description=operation.description,
            input_schema=operation.input_schema,
            output_schema=operation.output_schema,
            workflow_steps=workflow_steps_json,
            constraints=operation.constraints,
            permissions=operation.permissions
        )

    def initialize_operations(self, techtree_id: int) -> Dict[str, int]:
        """
        Initializes all task management operations for a given tech tree

        Args:
            techtree_id: ID of the tech tree to associate operations with

        Returns:
            Dict mapping operation names to their database IDs
        """
        operation_ids = {}

        try:
            for operation in TASK_OPERATIONS.values():
                # Check if operation already exists
                existing = self.session.query(TaskManagementAbility).filter_by(
                    techtree_id=techtree_id,
                    operation_name=operation.operation_name
                ).first()

                if existing:
                    logger.info(f"Operation {operation.operation_name} already exists")
                    operation_ids[operation.operation_name] = existing.id
                    continue

                # Create new operation
                db_operation = self._create_operation(techtree_id, operation)
                self.session.add(db_operation)
                self.session.flush()  # Get ID without committing
                operation_ids[operation.operation_name] = db_operation.id
                logger.info(f"Created operation {operation.operation_name}")

            self.session.commit()
            return operation_ids

        except Exception as e:
            self.session.rollback()
            logger.error(f"Error initializing operations: {str(e)}")
            raise

    def update_operation(self, operation_name: str, updates: Dict) -> bool:
        """
        Updates an existing operation with new configuration

        Args:
            operation_name: Name of the operation to update
            updates: Dictionary of fields to update

        Returns:
            bool indicating success
        """
        try:
            operation = self.session.query(TaskManagementAbility).filter_by(
                operation_name=operation_name
            ).first()

            if not operation:
                logger.warning(f"Operation {operation_name} not found")
                return False

            for field, value in updates.items():
                if hasattr(operation, field):
                    setattr(operation, field, value)

            self.session.commit()
            logger.info(f"Updated operation {operation_name}")
            return True

        except Exception as e:
            self.session.rollback()
            logger.error(f"Error updating operation {operation_name}: {str(e)}")
            raise

    def get_operation(self, operation_name: str) -> Optional[TaskManagementAbility]:
        """
        Retrieves an operation by name

        Args:
            operation_name: Name of the operation to retrieve

        Returns:
            TaskManagementAbility if found, None otherwise
        """
        return self.session.query(TaskManagementAbility).filter_by(
            operation_name=operation_name
        ).first()