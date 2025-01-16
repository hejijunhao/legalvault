# backend/services/executors/workspace/notebook_executor.py

from datetime import datetime
from typing import List, Optional
from uuid import UUID

from sqlmodel import Session, select
from fastapi import HTTPException

from models.database.workspace.notebook import Notebook
from models.domain.workspace.notebook import NotebookDomain, NotebookStateError
from models.schemas.workspace.notebook import NotebookCreate, NotebookUpdate, NotebookContentUpdate


class NotebookExecutor:
    """
    Executes notebook-related operations and handles database interactions.
    """

    def __init__(self, session: Session):
        self.session = session

    async def create_notebook(
            self,
            project_id: UUID,
            data: NotebookCreate,
            user_id: UUID
    ) -> NotebookDomain:
        """Creates a new notebook for a project."""
        async with self.session.begin():
            try:
                # Check if project already has a notebook
                existing = await self.get_project_notebook(project_id)
                if existing:
                    raise HTTPException(
                        status_code=400,
                        detail="Project already has a notebook"
                    )

                notebook = Notebook(
                    project_id=project_id,
                    title=data.title,
                    content=data.content,
                    tags=data.tags,
                    created_by=user_id,
                    modified_by=user_id
                )

                self.session.add(notebook)
                await self.session.commit()
                await self.session.refresh(notebook)

                return NotebookDomain(**notebook.dict())
            except Exception as e:
                await self.session.rollback()
                raise HTTPException(status_code=400, detail=str(e))

    async def update_notebook(
            self,
            notebook_id: UUID,
            data: NotebookUpdate,
            user_id: UUID
    ) -> NotebookDomain:
        """Updates notebook properties."""
        async with self.session.begin():
            try:
                notebook = await self._get_notebook(notebook_id)

                # Create domain model for business logic
                domain_notebook = NotebookDomain(**notebook.dict())

                # Update only provided fields
                update_data = data.dict(exclude_unset=True)
                if 'title' in update_data:
                    domain_notebook.update_title(update_data['title'], user_id)
                if 'tags' in update_data:
                    # Clear existing tags and add new ones
                    domain_notebook.tags = []
                    domain_notebook.add_tags(update_data['tags'], user_id)

                # Update database model with domain model changes
                for key, value in domain_notebook.dict().items():
                    setattr(notebook, key, value)

                await self.session.commit()
                await self.session.refresh(notebook)

                return NotebookDomain(**notebook.dict())
            except Exception as e:
                await self.session.rollback()
                raise HTTPException(status_code=400, detail=str(e))

    async def update_content(
            self,
            notebook_id: UUID,
            data: NotebookContentUpdate,
            user_id: UUID
    ) -> NotebookDomain:
        """Updates notebook content."""
        async with self.session.begin():
            try:
                notebook = await self._get_notebook(notebook_id)

                domain_notebook = NotebookDomain(**notebook.dict())
                domain_notebook.update_content(data.content, user_id)

                # Update database model
                notebook.content = domain_notebook.content
                notebook.last_modified_content = domain_notebook.last_modified_content
                notebook.modified_by = user_id
                notebook.updated_at = datetime.utcnow()

                await self.session.commit()
                await self.session.refresh(notebook)

                return NotebookDomain(**notebook.dict())
            except Exception as e:
                await self.session.rollback()
                raise HTTPException(status_code=400, detail=str(e))

    async def archive_notebook(
            self,
            notebook_id: UUID,
            user_id: UUID
    ) -> NotebookDomain:
        """Archives a notebook."""
        async with self.session.begin():
            try:
                notebook = await self._get_notebook(notebook_id)

                domain_notebook = NotebookDomain(**notebook.dict())
                domain_notebook.archive(user_id)

                notebook.is_archived = True
                notebook.modified_by = user_id
                notebook.updated_at = datetime.utcnow()

                await self.session.commit()
                await self.session.refresh(notebook)

                return NotebookDomain(**notebook.dict())
            except Exception as e:
                await self.session.rollback()
                raise HTTPException(status_code=400, detail=str(e))

    async def unarchive_notebook(
            self,
            notebook_id: UUID,
            user_id: UUID
    ) -> NotebookDomain:
        """Unarchives a notebook."""
        async with self.session.begin():
            try:
                notebook = await self._get_notebook(notebook_id)

                domain_notebook = NotebookDomain(**notebook.dict())
                domain_notebook.unarchive(user_id)

                notebook.is_archived = False
                notebook.modified_by = user_id
                notebook.updated_at = datetime.utcnow()

                await self.session.commit()
                await self.session.refresh(notebook)

                return NotebookDomain(**notebook.dict())
            except Exception as e:
                await self.session.rollback()
                raise HTTPException(status_code=400, detail=str(e))

    async def get_notebook(self, notebook_id: UUID) -> NotebookDomain:
        """Retrieves a notebook by ID."""
        notebook = await self._get_notebook(notebook_id)
        return NotebookDomain(**notebook.dict())

    async def get_project_notebook(self, project_id: UUID) -> Optional[NotebookDomain]:
        """Retrieves a notebook by project ID."""
        try:
            query = select(Notebook).where(Notebook.project_id == project_id)
            result = await self.session.execute(query)
            notebook = result.scalar_one_or_none()

            if notebook:
                return NotebookDomain(**notebook.dict())
            return None
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))

    async def _get_notebook(self, notebook_id: UUID) -> Notebook:
        """Helper method to get notebook by ID."""
        notebook = await self.session.get(Notebook, notebook_id)
        if not notebook:
            raise HTTPException(status_code=404, detail="Notebook not found")
        return notebook