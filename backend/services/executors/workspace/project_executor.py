# services/executors/workspace/project_executor.py

from datetime import datetime
from typing import List, Optional, Dict, Any
from uuid import UUID

from sqlmodel import Session, select
from fastapi import HTTPException

from models.database.workspace.project import Project, ProjectStatus, ProjectKnowledge
from models.domain.workspace.project import ProjectDomain
from models.domain.workspace.reminder import ReminderDomain
from models.schemas.workspace.project import ProjectCreate, ProjectUpdate, ProjectKnowledgeUpdate, ProjectSummaryUpdate


class ProjectExecutor:
    """
    Executes project-related operations and handles database interactions.
    """

    def __init__(self, session: Session):
        self.session = session

    async def create_project(self, data: ProjectCreate, user_id: UUID) -> ProjectDomain:
        """Creates a new project."""
        try:
            project = Project(
                name=data.name,
                status=ProjectStatus.ACTIVE,
                created_by=user_id,
                modified_by=user_id,
                practice_area=data.practice_area,
                confidentiality=data.confidentiality,
                start_date=data.start_date,
                tags=data.tags
            )

            self.session.add(project)
            await self.session.commit()
            await self.session.refresh(project)

            return ProjectDomain(**project.dict())
        except Exception as e:
            await self.session.rollback()
            raise HTTPException(status_code=400, detail=str(e))

    async def update_project(
            self, project_id: UUID, data: ProjectUpdate, user_id: UUID
    ) -> ProjectDomain:
        """Updates project details."""
        try:
            project = await self._get_project(project_id)

            # Update only provided fields
            update_data = data.dict(exclude_unset=True)
            for key, value in update_data.items():
                setattr(project, key, value)

            project.modified_by = user_id
            project.updated_at = datetime.utcnow()

            await self.session.commit()
            await self.session.refresh(project)

            return ProjectDomain(**project.dict())
        except Exception as e:
            await self.session.rollback()
            raise HTTPException(status_code=400, detail=str(e))

    async def update_knowledge(
            self, project_id: UUID, data: ProjectKnowledgeUpdate, user_id: UUID
    ) -> ProjectDomain:
        """Updates project knowledge content."""
        try:
            project = await self._get_project(project_id)

            knowledge = ProjectKnowledge(
                content=data.content,
                last_updated=datetime.utcnow()
            )

            project.knowledge = knowledge
            project.modified_by = user_id
            project.updated_at = datetime.utcnow()

            await self.session.commit()
            await self.session.refresh(project)

            return ProjectDomain(**project.dict())
        except Exception as e:
            await self.session.rollback()
            raise HTTPException(status_code=400, detail=str(e))

    async def update_notebook_status(
            self,
            project_id: UUID,
            notebook_id: UUID,
            status: Dict[str, Any],
            user_id: UUID
    ) -> ProjectDomain:
        """Updates project's notebook status information."""
        try:
            project = await self._get_project(project_id)

            # Create domain model for business logic
            domain_project = ProjectDomain(**project.dict())
            domain_project.update_notebook_status(notebook_id, status, user_id)

            # Update database model
            project.notebook_id = notebook_id
            project.notebook_status = status
            project.modified_by = user_id
            project.updated_at = datetime.utcnow()

            await self.session.commit()
            await self.session.refresh(project)

            return ProjectDomain(**project.dict())
        except Exception as e:
            await self.session.rollback()
            raise HTTPException(status_code=400, detail=str(e))

    async def update_summary(
            self, project_id: UUID, data: ProjectSummaryUpdate, user_id: UUID
    ) -> ProjectDomain:
        """Updates project summary."""
        try:
            project = await self._get_project(project_id)

            project.summary = data.summary
            project.summary_updated_at = datetime.utcnow()
            project.modified_by = user_id
            project.updated_at = datetime.utcnow()

            await self.session.commit()
            await self.session.refresh(project)

            return ProjectDomain(**project.dict())
        except Exception as e:
            await self.session.rollback()
            raise HTTPException(status_code=400, detail=str(e))

    async def update_status(
            self, project_id: UUID, status: ProjectStatus, user_id: UUID
    ) -> ProjectDomain:
        """Updates project status."""
        try:
            project = await self._get_project(project_id)

            # Create domain model for business logic
            domain_project = ProjectDomain(**project.dict())

            # Validate status transition through domain model
            domain_project.update_status(status, user_id)

            # Update database model
            project.status = status
            project.modified_by = user_id
            project.updated_at = datetime.utcnow()

            await self.session.commit()
            await self.session.refresh(project)

            return ProjectDomain(**project.dict())
        except Exception as e:
            await self.session.rollback()
            raise HTTPException(status_code=400, detail=str(e))


    async def get_project(self, project_id: UUID) -> ProjectDomain:
        """Retrieves a project by ID with reminders."""
        project = await self._get_project(project_id)
        domain_project = ProjectDomain(**project.dict())

        # Load reminders if they exist
        if project.reminders:
            domain_project.reminders = [
                ReminderDomain(**reminder.dict())
                for reminder in project.reminders
            ]

        # Load tasks if they exist
        if project.tasks:
            domain_project.tasks = [
                TaskDomain(**task.dict())
                for task in project.tasks
            ]

        return domain_project

    async def list_projects(
            self,
            user_id: UUID,
            status: Optional[ProjectStatus] = None,
            practice_area: Optional[str] = None
    ) -> List[ProjectDomain]:
        """Lists projects with optional filters."""
        try:
            query = select(Project)

            if status:
                query = query.where(Project.status == status)
            if practice_area:
                query = query.where(Project.practice_area == practice_area)

            # Order by updated_at for consistency
            query = query.order_by(Project.updated_at.desc())

            result = await self.session.execute(query)
            projects = result.scalars().all()

            return [ProjectDomain(**project.dict()) for project in projects]
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))

    async def _get_project(self, project_id: UUID) -> Project:
        """Helper method to get project by ID."""
        project = await self.session.get(Project, project_id)
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        return project