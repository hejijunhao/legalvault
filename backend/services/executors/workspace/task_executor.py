# services/executors/workspace/task_executor.py

from datetime import datetime
from typing import List, Optional
from uuid import UUID

from sqlmodel import Session, select
from fastapi import HTTPException

from models.database.workspace.task import Task, TaskStatus
from models.domain.workspace.task import TaskDomain
from models.schemas.workspace.task import TaskCreate, TaskUpdate


class TaskExecutor:
    """
    Executes task-related operations and handles database interactions.
    """

    def __init__(self, session: Session):
        self.session = session

    async def create_task(self, data: TaskCreate, user_id: UUID) -> TaskDomain:
        """Creates a new task."""
        try:
            task = Task(
                project_id=data.project_id,
                title=data.title,
                description=data.description,
                status=TaskStatus.TODO,
                due_date=data.due_date,
                assigned_to=data.assigned_to,
                created_by=user_id,
                modified_by=user_id
            )

            self.session.add(task)
            await self.session.commit()
            await self.session.refresh(task)

            return TaskDomain(**task.dict())
        except Exception as e:
            await self.session.rollback()
            raise HTTPException(status_code=400, detail=str(e))

    async def update_task(
            self, task_id: UUID, data: TaskUpdate, user_id: UUID
    ) -> TaskDomain:
        """Updates task details."""
        try:
            task = await self._get_task(task_id)

            # Create domain model for business logic
            domain_task = TaskDomain(**task.dict())

            # Update fields through domain model
            if data.title is not None or data.description is not None:
                domain_task.update_details(data.title, data.description, user_id)

            if data.assigned_to is not None:
                domain_task.reassign(data.assigned_to, user_id)

            if data.due_date is not None:
                domain_task.update_due_date(data.due_date, user_id)

            if data.status is not None:
                if data.status == TaskStatus.COMPLETED:
                    domain_task.complete(user_id)
                elif data.status == TaskStatus.TODO:
                    domain_task.reopen(user_id)

            # Update database model
            for field, value in data.dict(exclude_unset=True).items():
                setattr(task, field, value)

            task.modified_by = user_id
            task.updated_at = datetime.utcnow()

            await self.session.commit()
            await self.session.refresh(task)

            return TaskDomain(**task.dict())
        except Exception as e:
            await self.session.rollback()
            raise HTTPException(status_code=400, detail=str(e))

    async def complete_task(self, task_id: UUID, user_id: UUID) -> TaskDomain:
        """Marks a task as completed."""
        try:
            task = await self._get_task(task_id)

            # Create domain model for business logic
            domain_task = TaskDomain(**task.dict())
            domain_task.complete(user_id)

            # Update database model
            task.status = TaskStatus.COMPLETED
            task.completed_at = datetime.utcnow()
            task.modified_by = user_id
            task.updated_at = datetime.utcnow()

            await self.session.commit()
            await self.session.refresh(task)

            return TaskDomain(**task.dict())
        except Exception as e:
            await self.session.rollback()
            raise HTTPException(status_code=400, detail=str(e))

    async def reopen_task(self, task_id: UUID, user_id: UUID) -> TaskDomain:
        """Reopens a completed task."""
        try:
            task = await self._get_task(task_id)

            # Create domain model for business logic
            domain_task = TaskDomain(**task.dict())
            domain_task.reopen(user_id)

            # Update database model
            task.status = TaskStatus.TODO
            task.completed_at = None
            task.modified_by = user_id
            task.updated_at = datetime.utcnow()

            await self.session.commit()
            await self.session.refresh(task)

            return TaskDomain(**task.dict())
        except Exception as e:
            await self.session.rollback()
            raise HTTPException(status_code=400, detail=str(e))

    async def delete_task(self, task_id: UUID) -> None:
        """Deletes a task."""
        try:
            task = await self._get_task(task_id)
            await self.session.delete(task)
            await self.session.commit()
        except Exception as e:
            await self.session.rollback()
            raise HTTPException(status_code=400, detail=str(e))

    async def get_task(self, task_id: UUID) -> TaskDomain:
        """Retrieves a task by ID."""
        task = await self._get_task(task_id)
        return TaskDomain(**task.dict())

    async def get_project_tasks(
            self,
            project_id: UUID,
            status: Optional[TaskStatus] = None
    ) -> List[TaskDomain]:
        """Retrieves all tasks for a specific project."""
        try:
            query = select(Task).where(Task.project_id == project_id)

            if status:
                query = query.where(Task.status == status)

            # Order by due date and status
            query = query.order_by(Task.due_date.asc(), Task.status)

            result = await self.session.execute(query)
            tasks = result.scalars().all()

            return [TaskDomain(**task.dict()) for task in tasks]
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))

    async def _get_task(self, task_id: UUID) -> Task:
        """Helper method to get task by ID."""
        task = await self.session.get(Task, task_id)
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")
        return task