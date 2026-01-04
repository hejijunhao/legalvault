# backend/services/executors/workspace/notebook_executor.py

from datetime import datetime
from typing import List, Optional
from uuid import UUID

from sqlmodel import Session, select
from fastapi import HTTPException

from models.database.workspace.notebook import Notebook
from models.domain.workspace.notebook import NotebookDomain, NotebookStateError
from models.schemas.workspace.notebook import NotebookCreate, NotebookUpdate, NotebookContentUpdate
from services.executors.base_executor import BaseExecutor


class NotebookExecutor(BaseExecutor[Notebook, NotebookDomain]):
    """
    Executes notebook-related operations and handles database interactions.
    Extends BaseExecutor for common CRUD operations.
    """

    def __init__(self, session: Session):
        super().__init__(session, Notebook, "notebook_id", NotebookDomain)

    async def create_notebook(
        self, project_id: UUID, data: NotebookCreate, user_id: UUID
    ) -> NotebookDomain:
        """Creates a new notebook for a project."""
        # Check if project already has a notebook
        existing = await self.get_project_notebook(project_id)
        if existing:
            raise HTTPException(
                status_code=400, detail="Project already has a notebook"
            )

        notebook = await self.create(
            {
                "project_id": project_id,
                "title": data.title,
                "content": data.content,
                "tags": data.tags,
            },
            user_id=user_id,
        )
        return self._to_domain(notebook)

    async def update_notebook(
        self, notebook_id: UUID, data: NotebookUpdate, user_id: UUID
    ) -> NotebookDomain:
        """Updates notebook properties."""
        notebook = await self.get_or_404(notebook_id)

        # Create domain model for business logic
        domain_notebook = NotebookDomain(**notebook.dict())

        # Update only provided fields
        update_data = data.dict(exclude_unset=True)
        if "title" in update_data:
            domain_notebook.update_title(update_data["title"], user_id)
        if "tags" in update_data:
            # Clear existing tags and add new ones
            domain_notebook.tags = []
            domain_notebook.add_tags(update_data["tags"], user_id)

        # Update database model with domain model changes
        for key, value in domain_notebook.dict().items():
            setattr(notebook, key, value)

        await self._commit_and_refresh(notebook)
        return self._to_domain(notebook)

    async def update_content(
        self, notebook_id: UUID, data: NotebookContentUpdate, user_id: UUID
    ) -> NotebookDomain:
        """Updates notebook content."""
        notebook = await self.get_or_404(notebook_id)

        domain_notebook = NotebookDomain(**notebook.dict())
        domain_notebook.update_content(data.content, user_id)

        # Update database model
        notebook.content = domain_notebook.content
        notebook.last_modified_content = domain_notebook.last_modified_content
        notebook.modified_by = user_id
        notebook.updated_at = datetime.utcnow()

        await self._commit_and_refresh(notebook)
        return self._to_domain(notebook)

    async def archive_notebook(self, notebook_id: UUID, user_id: UUID) -> NotebookDomain:
        """Archives a notebook."""
        notebook = await self.get_or_404(notebook_id)

        domain_notebook = NotebookDomain(**notebook.dict())
        domain_notebook.archive(user_id)

        notebook.is_archived = True
        notebook.modified_by = user_id
        notebook.updated_at = datetime.utcnow()

        await self._commit_and_refresh(notebook)
        return self._to_domain(notebook)

    async def unarchive_notebook(
        self, notebook_id: UUID, user_id: UUID
    ) -> NotebookDomain:
        """Unarchives a notebook."""
        notebook = await self.get_or_404(notebook_id)

        domain_notebook = NotebookDomain(**notebook.dict())
        domain_notebook.unarchive(user_id)

        notebook.is_archived = False
        notebook.modified_by = user_id
        notebook.updated_at = datetime.utcnow()

        await self._commit_and_refresh(notebook)
        return self._to_domain(notebook)

    async def get_notebook(self, notebook_id: UUID) -> NotebookDomain:
        """Retrieves a notebook by ID."""
        notebook = await self.get_or_404(notebook_id)
        return self._to_domain(notebook)

    async def get_project_notebook(self, project_id: UUID) -> Optional[NotebookDomain]:
        """Retrieves a notebook by project ID."""
        notebooks = await self.list(filters={"project_id": project_id}, limit=1)
        if notebooks:
            return self._to_domain(notebooks[0])
        return None
