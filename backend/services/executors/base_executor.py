# services/executors/base_executor.py
"""
Generic CRUD executor base class for SQLModel entities.

Provides common CRUD operations with transaction handling, reducing boilerplate
in entity-specific executors.

Usage:
    from services.executors.base_executor import BaseExecutor

    class TaskExecutor(BaseExecutor[Task, TaskDomain]):
        def __init__(self, session: Session):
            super().__init__(session, Task, "task_id")

        async def complete_task(self, task_id: UUID, user_id: UUID) -> TaskDomain:
            # Custom operation using base methods
            task = await self._get_or_404(task_id)
            task.status = TaskStatus.COMPLETED
            task.completed_at = datetime.utcnow()
            await self._commit_and_refresh(task)
            return self._to_domain(task)
"""

from datetime import datetime
from typing import (
    TypeVar,
    Generic,
    List,
    Optional,
    Dict,
    Any,
    Type,
    Callable,
    Awaitable,
)
from uuid import UUID

from sqlmodel import Session, select, SQLModel
from sqlalchemy import Column
from fastapi import HTTPException


# Type variables for generic executor
ModelT = TypeVar("ModelT", bound=SQLModel)  # Database model type
DomainT = TypeVar("DomainT")  # Domain model type (optional)


class BaseExecutor(Generic[ModelT, DomainT]):
    """
    Generic base class for entity executors.

    Provides common CRUD operations with proper transaction handling
    and error management.

    Type Parameters:
        ModelT: The SQLModel database model class
        DomainT: The domain model class (can be same as ModelT if no domain layer)
    """

    def __init__(
        self,
        session: Session,
        model_class: Type[ModelT],
        id_field: str = "id",
        domain_class: Optional[Type[DomainT]] = None,
    ):
        """
        Initialize the executor.

        Args:
            session: SQLModel async session
            model_class: The database model class
            id_field: Name of the primary key field (default: "id")
            domain_class: Optional domain class for conversion
        """
        self.session = session
        self.model_class = model_class
        self.id_field = id_field
        self.domain_class = domain_class
        self._model_name = model_class.__name__

    # =========================================================================
    # Core CRUD Operations
    # =========================================================================

    async def create(
        self,
        data: Dict[str, Any],
        user_id: Optional[UUID] = None,
        **extra_fields: Any,
    ) -> ModelT:
        """
        Create a new entity.

        Args:
            data: Dictionary of field values
            user_id: Optional user ID for created_by/modified_by
            **extra_fields: Additional fields to set

        Returns:
            The created entity

        Raises:
            HTTPException: If creation fails
        """
        try:
            # Merge data with extra fields
            all_data = {**data, **extra_fields}

            # Add audit fields if user_id provided
            if user_id:
                if hasattr(self.model_class, "created_by"):
                    all_data["created_by"] = user_id
                if hasattr(self.model_class, "modified_by"):
                    all_data["modified_by"] = user_id

            entity = self.model_class(**all_data)
            self.session.add(entity)
            await self.session.commit()
            await self.session.refresh(entity)

            return entity
        except Exception as e:
            await self.session.rollback()
            raise HTTPException(
                status_code=400,
                detail=f"Failed to create {self._model_name}: {str(e)}",
            )

    async def get(self, entity_id: UUID) -> Optional[ModelT]:
        """
        Get entity by ID.

        Args:
            entity_id: The entity's primary key value

        Returns:
            The entity or None if not found
        """
        return await self.session.get(self.model_class, entity_id)

    async def get_or_404(self, entity_id: UUID) -> ModelT:
        """
        Get entity by ID or raise 404.

        Args:
            entity_id: The entity's primary key value

        Returns:
            The entity

        Raises:
            HTTPException: 404 if entity not found
        """
        entity = await self.get(entity_id)
        if not entity:
            raise HTTPException(
                status_code=404, detail=f"{self._model_name} not found"
            )
        return entity

    async def update(
        self,
        entity_id: UUID,
        data: Dict[str, Any],
        user_id: Optional[UUID] = None,
    ) -> ModelT:
        """
        Update an entity.

        Args:
            entity_id: The entity's primary key value
            data: Dictionary of fields to update (None values are skipped)
            user_id: Optional user ID for modified_by

        Returns:
            The updated entity

        Raises:
            HTTPException: If entity not found or update fails
        """
        try:
            entity = await self.get_or_404(entity_id)

            # Update fields
            for field, value in data.items():
                if value is not None and hasattr(entity, field):
                    setattr(entity, field, value)

            # Update audit fields
            if user_id and hasattr(entity, "modified_by"):
                entity.modified_by = user_id
            if hasattr(entity, "updated_at"):
                entity.updated_at = datetime.utcnow()

            await self.session.commit()
            await self.session.refresh(entity)

            return entity
        except HTTPException:
            raise
        except Exception as e:
            await self.session.rollback()
            raise HTTPException(
                status_code=400,
                detail=f"Failed to update {self._model_name}: {str(e)}",
            )

    async def delete(self, entity_id: UUID) -> None:
        """
        Delete an entity.

        Args:
            entity_id: The entity's primary key value

        Raises:
            HTTPException: If entity not found or delete fails
        """
        try:
            entity = await self.get_or_404(entity_id)
            await self.session.delete(entity)
            await self.session.commit()
        except HTTPException:
            raise
        except Exception as e:
            await self.session.rollback()
            raise HTTPException(
                status_code=400,
                detail=f"Failed to delete {self._model_name}: {str(e)}",
            )

    async def list(
        self,
        filters: Optional[Dict[str, Any]] = None,
        order_by: Optional[List[Any]] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> List[ModelT]:
        """
        List entities with optional filtering.

        Args:
            filters: Dictionary of field->value filters (exact match)
            order_by: List of columns to order by
            limit: Maximum results to return
            offset: Number of results to skip

        Returns:
            List of matching entities
        """
        try:
            query = select(self.model_class)

            # Apply filters
            if filters:
                for field, value in filters.items():
                    if value is not None and hasattr(self.model_class, field):
                        query = query.where(
                            getattr(self.model_class, field) == value
                        )

            # Apply ordering
            if order_by:
                query = query.order_by(*order_by)

            # Apply pagination
            query = query.offset(offset).limit(limit)

            result = await self.session.execute(query)
            return list(result.scalars().all())
        except Exception as e:
            raise HTTPException(
                status_code=400,
                detail=f"Failed to list {self._model_name}s: {str(e)}",
            )

    async def count(self, filters: Optional[Dict[str, Any]] = None) -> int:
        """
        Count entities with optional filtering.

        Args:
            filters: Dictionary of field->value filters

        Returns:
            Number of matching entities
        """
        from sqlalchemy import func

        try:
            query = select(func.count()).select_from(self.model_class)

            if filters:
                for field, value in filters.items():
                    if value is not None and hasattr(self.model_class, field):
                        query = query.where(
                            getattr(self.model_class, field) == value
                        )

            result = await self.session.execute(query)
            return result.scalar() or 0
        except Exception as e:
            raise HTTPException(
                status_code=400,
                detail=f"Failed to count {self._model_name}s: {str(e)}",
            )

    # =========================================================================
    # Helper Methods for Subclasses
    # =========================================================================

    async def _commit_and_refresh(self, entity: ModelT) -> ModelT:
        """
        Commit current transaction and refresh entity.

        Args:
            entity: The entity to refresh

        Returns:
            The refreshed entity

        Raises:
            HTTPException: If commit fails
        """
        try:
            await self.session.commit()
            await self.session.refresh(entity)
            return entity
        except Exception as e:
            await self.session.rollback()
            raise HTTPException(
                status_code=400,
                detail=f"Transaction failed: {str(e)}",
            )

    async def _rollback(self) -> None:
        """Rollback current transaction."""
        await self.session.rollback()

    def _to_domain(self, entity: ModelT) -> DomainT:
        """
        Convert database model to domain model.

        Args:
            entity: The database entity

        Returns:
            The domain model instance

        Raises:
            ValueError: If no domain class configured
        """
        if self.domain_class is None:
            # If no domain class, return entity as-is (type: ignore needed)
            return entity  # type: ignore
        return self.domain_class(**entity.dict())

    def _to_domain_list(self, entities: List[ModelT]) -> List[DomainT]:
        """
        Convert list of database models to domain models.

        Args:
            entities: List of database entities

        Returns:
            List of domain model instances
        """
        return [self._to_domain(e) for e in entities]

    async def _execute_in_transaction(
        self,
        operation: Callable[[], Awaitable[ModelT]],
    ) -> ModelT:
        """
        Execute an operation with automatic transaction handling.

        Args:
            operation: Async function to execute

        Returns:
            Result of the operation

        Raises:
            HTTPException: If operation fails
        """
        try:
            result = await operation()
            await self.session.commit()
            await self.session.refresh(result)
            return result
        except HTTPException:
            await self.session.rollback()
            raise
        except Exception as e:
            await self.session.rollback()
            raise HTTPException(
                status_code=400,
                detail=f"Operation failed: {str(e)}",
            )


# Convenience type alias for executors without domain models
class SimpleCRUDExecutor(BaseExecutor[ModelT, ModelT]):
    """
    Simplified executor for entities without a separate domain model.

    Usage:
        class ReminderExecutor(SimpleCRUDExecutor[Reminder]):
            def __init__(self, session: Session):
                super().__init__(session, Reminder, "reminder_id")
    """

    def __init__(
        self,
        session: Session,
        model_class: Type[ModelT],
        id_field: str = "id",
    ):
        super().__init__(session, model_class, id_field, domain_class=None)
