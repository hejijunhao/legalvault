# models/database/workspace/__init__.py

from .client import ClientBlueprint, ClientBase, LegalEntityType, ClientStatus
from .contact import ContactBlueprint, ContactBase, ContactType, ContactStatus
from .contact_client import ContactClientBlueprint, ContactClientBase, ContactRole
from .contact_project import ContactProjectBlueprint, ContactProjectBase, ProjectRole
from .notebook import NotebookBlueprint, NotebookBase
from .project import (
    ProjectBlueprint, ProjectBase, ProjectStatus,
    ConfidentialityLevel, ProjectKnowledge
)
from .project_client import ProjectClientBlueprint, ProjectClientBase, ClientProjectRole
from .reminder import ReminderBlueprint, ReminderBase, ReminderStatus
from .task import TaskBlueprint, TaskBase, TaskStatus

__all__ = [
    'ClientBase', 'LegalEntityType', 'ClientStatus',
    'ContactBlueprint', 'ContactBase', 'ContactType', 'ContactStatus',
    'ContactClientBlueprint', 'ContactClientBase', 'ContactRole',
    'ContactProjectBlueprint', 'ContactProjectBase', 'ProjectRole',
    'NotebookBlueprint', 'NotebookBase',
    'ProjectBlueprint', 'ProjectBase', 'ProjectStatus', 'ConfidentialityLevel', 'ProjectKnowledge',
    'ProjectClientBlueprint', 'ProjectClientBase', 'ClientProjectRole',
    'ReminderBlueprint', 'ReminderBase', 'ReminderStatus',
    'TaskBlueprint', 'TaskBase', 'TaskStatus',
]

