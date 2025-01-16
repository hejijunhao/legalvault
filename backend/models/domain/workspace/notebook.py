# backend/models/domain/workspace/notebook.py

from datetime import datetime
from typing import List, Optional
from uuid import UUID
from fastapi import HTTPException


class NotebookStateError(Exception):
    """Custom exception for invalid notebook state transitions"""
    pass


class NotebookDomain:
    """
    Domain model for Notebook entities. Handles business logic, state management,
    and behavior for notebooks in the LegalVault system.
    """

    def __init__(
            self,
            notebook_id: UUID,
            project_id: UUID,
            created_by: UUID,
            modified_by: UUID,
            content: str = "",
            title: Optional[str] = None,
            tags: List[str] = None,
            is_archived: bool = False,
            last_modified_content: Optional[datetime] = None,
            created_at: Optional[datetime] = None,
            updated_at: Optional[datetime] = None
    ):
        self.notebook_id = notebook_id
        self.project_id = project_id
        self.created_by = created_by
        self.modified_by = modified_by
        self.content = content
        self.title = title
        self.tags = tags or []
        self.is_archived = is_archived
        self.last_modified_content = last_modified_content or datetime.utcnow()
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at or datetime.utcnow()

    def _validate_active_state(self) -> None:
        """Validates if notebook is in an active state for modifications"""
        if self.is_archived:
            raise NotebookStateError("Cannot modify an archived notebook")

    def _update_modification_metadata(self, modified_by: UUID) -> None:
        """Updates modification metadata"""
        self.modified_by = modified_by
        self.updated_at = datetime.utcnow()

    def update_content(self, new_content: str, modified_by: UUID) -> None:
        """
        Updates notebook content.

        Args:
            new_content: New content to be set
            modified_by: UUID of the user making the modification

        Raises:
            NotebookStateError: If notebook is archived
        """
        self._validate_active_state()
        self.content = new_content
        self.last_modified_content = datetime.utcnow()
        self._update_modification_metadata(modified_by)

    def update_title(self, new_title: str, modified_by: UUID) -> None:
        """
        Updates notebook title.

        Args:
            new_title: New title to be set
            modified_by: UUID of the user making the modification

        Raises:
            NotebookStateError: If notebook is archived
        """
        self._validate_active_state()
        self.title = new_title.strip() if new_title else None
        self._update_modification_metadata(modified_by)

    def add_tags(self, new_tags: List[str], modified_by: UUID) -> None:
        """
        Adds new tags to the notebook.

        Args:
            new_tags: List of tags to add
            modified_by: UUID of the user making the modification

        Raises:
            NotebookStateError: If notebook is archived
        """
        self._validate_active_state()
        # Filter out empty or whitespace-only tags
        valid_tags = [tag.strip() for tag in new_tags if tag and tag.strip()]
        if valid_tags:
            self.tags = list(set(self.tags + valid_tags))
            self._update_modification_metadata(modified_by)

    def remove_tags(self, tags_to_remove: List[str], modified_by: UUID) -> None:
        """
        Removes specified tags from the notebook.

        Args:
            tags_to_remove: List of tags to remove
            modified_by: UUID of the user making the modification

        Raises:
            NotebookStateError: If notebook is archived
        """
        self._validate_active_state()
        initial_tag_count = len(self.tags)
        self.tags = [tag for tag in self.tags if tag not in tags_to_remove]
        if len(self.tags) != initial_tag_count:
            self._update_modification_metadata(modified_by)

    def archive(self, modified_by: UUID) -> None:
        """
        Archives the notebook.

        Args:
            modified_by: UUID of the user making the modification

        Raises:
            NotebookStateError: If notebook is already archived
        """
        if self.is_archived:
            raise NotebookStateError("Notebook is already archived")
        self.is_archived = True
        self._update_modification_metadata(modified_by)

    def unarchive(self, modified_by: UUID) -> None:
        """
        Unarchives the notebook.

        Args:
            modified_by: UUID of the user making the modification

        Raises:
            NotebookStateError: If notebook is not archived
        """
        if not self.is_archived:
            raise NotebookStateError("Notebook is not archived")
        self.is_archived = False
        self._update_modification_metadata(modified_by)

    def dict(self) -> dict:
        """Converts domain model to dictionary representation"""
        return {
            'notebook_id': self.notebook_id,
            'project_id': self.project_id,
            'created_by': self.created_by,
            'modified_by': self.modified_by,
            'content': self.content,
            'title': self.title,
            'tags': self.tags,
            'is_archived': self.is_archived,
            'last_modified_content': self.last_modified_content,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }