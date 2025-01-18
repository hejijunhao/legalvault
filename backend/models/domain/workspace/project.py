# models/domain/workspace/project.py

from datetime import datetime
from typing import List, Optional, Dict, Any
from uuid import UUID
from fastapi import HTTPException

# Database Model Imports
from models.database.workspace.project import ProjectStatus, ConfidentialityLevel, ProjectKnowledge
from models.database.workspace.reminder import ReminderStatus

# Domain Model Imports
from models.domain.workspace.reminder import ReminderDomain
from models.domain.workspace.notebook import NotebookDomain


class ProjectStateError(Exception):
    """Custom exception for invalid project state transitions"""
    pass


class ProjectDomain:
    """
    Domain model for Project entities. Handles business logic, state management,
    and behavior for projects in the LegalVault system.
    """

    def __init__(
            self,
            project_id: UUID,
            name: str,
            status: ProjectStatus,
            created_by: UUID,
            modified_by: UUID,
            practice_area: Optional[str] = None,
            confidentiality: ConfidentialityLevel = ConfidentialityLevel.CONFIDENTIAL,
            start_date: Optional[datetime] = None,
            tags: List[str] = None,
            knowledge: Optional[ProjectKnowledge] = None,
            summary: Optional[str] = None,
            summary_updated_at: Optional[datetime] = None,
            created_at: Optional[datetime] = None,
            updated_at: Optional[datetime] = None,
            notebook_id: Optional[UUID] = None,
            notebook_status: Optional[Dict[str, Any]] = None,
            reminders: Optional[List[ReminderDomain]] = None
    ):
        self.project_id = project_id
        self.name = name
        self.status = status
        self.created_by = created_by
        self.modified_by = modified_by
        self.practice_area = practice_area
        self.confidentiality = confidentiality
        self.start_date = start_date
        self.tags = tags or []
        self.knowledge = knowledge
        self.summary = summary
        self.summary_updated_at = summary_updated_at
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at or datetime.utcnow()
        self.notebook_id = notebook_id
        self.notebook_status = notebook_status or {}
        self.reminders = reminders or []

    def _validate_active_state(self) -> None:
        """Validates if project is in an active state for modifications"""
        if self.status == ProjectStatus.ARCHIVED:
            raise ProjectStateError("Cannot modify an archived project")

    def _update_modification_metadata(self, modified_by: UUID) -> None:
        """Updates modification metadata"""
        self.modified_by = modified_by
        self.updated_at = datetime.utcnow()

    def update_status(self, new_status: ProjectStatus, modified_by: UUID) -> None:
        """
        Updates project status with state transition validation.

        Raises:
            ProjectStateError: If the state transition is invalid
        """
        if new_status == self.status:
            return

        # Validate state transitions
        if new_status == ProjectStatus.ARCHIVED:
            if not self.can_be_archived():
                raise ProjectStateError("Project must be completed before archiving")
        elif new_status == ProjectStatus.COMPLETED:
            if not self.can_be_completed():
                raise ProjectStateError("Project must meet completion requirements")
        elif new_status == ProjectStatus.ACTIVE and self.status == ProjectStatus.ARCHIVED:
            raise ProjectStateError("Cannot reactivate an archived project")

        self.status = new_status
        self._update_modification_metadata(modified_by)

    def update_knowledge(self, new_knowledge: ProjectKnowledge, modified_by: UUID) -> None:
        """
        Updates project knowledge content.

        Raises:
            ProjectStateError: If project is archived
        """
        self._validate_active_state()
        self.knowledge = new_knowledge
        self._update_modification_metadata(modified_by)

    def update_summary(self, new_summary: str, modified_by: UUID) -> None:
        """
        Updates project summary.

        Raises:
            ProjectStateError: If project is archived
        """
        self._validate_active_state()
        self.summary = new_summary
        self.summary_updated_at = datetime.utcnow()
        self._update_modification_metadata(modified_by)

    def update_notebook_status(self, notebook_id: UUID, status: Dict[str, Any], modified_by: UUID) -> None:
        """
        Updates notebook status information.

        Args:
            notebook_id: UUID of the associated notebook
            status: Dictionary containing notebook status information
            modified_by: UUID of the user making the modification

        Raises:
            ProjectStateError: If project is archived
        """
        self._validate_active_state()
        self.notebook_id = notebook_id
        self.notebook_status = status
        self._update_modification_metadata(modified_by)

    def add_tags(self, new_tags: List[str], modified_by: UUID) -> None:
        """
        Adds new tags to the project.

        Raises:
            ProjectStateError: If project is archived
        """
        self._validate_active_state()
        valid_tags = [tag.strip() for tag in new_tags if tag and tag.strip()]
        if valid_tags:
            self.tags = list(set(self.tags + valid_tags))
            self._update_modification_metadata(modified_by)

    def remove_tags(self, tags_to_remove: List[str], modified_by: UUID) -> None:
        """
        Removes specified tags from the project.

        Raises:
            ProjectStateError: If project is archived
        """
        self._validate_active_state()
        initial_tag_count = len(self.tags)
        self.tags = [tag for tag in self.tags if tag not in tags_to_remove]
        if len(self.tags) != initial_tag_count:
            self._update_modification_metadata(modified_by)

    def update_confidentiality(self, new_level: ConfidentialityLevel, modified_by: UUID) -> None:
        """
        Updates project confidentiality level.

        Raises:
            ProjectStateError: If project is archived
        """
        self._validate_active_state()
        if new_level != self.confidentiality:
            self.confidentiality = new_level
            self._update_modification_metadata(modified_by)

    def can_be_archived(self) -> bool:
        """Checks if project meets conditions for archival"""
        return (
                self.status == ProjectStatus.COMPLETED and
                self.knowledge is not None and
                self.summary is not None and
                bool(self.notebook_status.get('is_archived', False))  # Ensure notebook is archived
        )

    def can_be_completed(self) -> bool:
        """Checks if project meets conditions for completion"""
        return (
                self.status == ProjectStatus.ACTIVE and
                self.knowledge is not None and  # Must have knowledge content
                bool(self.tags) and  # Must have at least one tag
                self.notebook_id is not None  # Must have an associated notebook
        )

    # Reminder Class References
    def get_pending_reminders(self) -> List[ReminderDomain]:
        """Returns all pending reminders for the project"""
        return [
            reminder for reminder in self.reminders
            if reminder.status == ReminderStatus.PENDING
        ]

    def get_overdue_reminders(self) -> List[ReminderDomain]:
        """Returns all overdue reminders for the project"""
        return [
            reminder for reminder in self.reminders
            if reminder.is_overdue()
        ]

    def dict(self) -> dict:
        """Converts domain model to dictionary representation"""
        return {
            'project_id': self.project_id,
            'name': self.name,
            'status': self.status,
            'created_by': self.created_by,
            'modified_by': self.modified_by,
            'practice_area': self.practice_area,
            'confidentiality': self.confidentiality,
            'start_date': self.start_date,
            'tags': self.tags,
            'knowledge': self.knowledge,
            'summary': self.summary,
            'summary_updated_at': self.summary_updated_at,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
            'notebook_id': self.notebook_id,
            'notebook_status': self.notebook_status,
            'reminders': [reminder.dict() for reminder in self.reminders] if self.reminders else []
        }