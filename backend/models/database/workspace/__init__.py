# models/database/workspace/__init__.py

from .client import Client, ClientBase, LegalEntityType, ClientStatus
from .contact import Contact, ContactBase, ContactType, ContactStatus
from .contact_client import ContactClient, ContactClientBase, ContactRole
from .contact_project import ContactProject, ContactProjectBase, ProjectRole
from .notebook import Notebook, NotebookBase
from .project import (
    Project, ProjectBase, ProjectStatus, 
    ConfidentialityLevel, ProjectKnowledge
)
from .project_client import ProjectClient, ProjectClientBase, ClientProjectRole
from .reminder import Reminder, ReminderBase, ReminderStatus
from .task import Task, TaskBase, TaskStatus

__all__ = [
    'Client', 'ClientBase', 'LegalEntityType', 'ClientStatus',
    'Contact', 'ContactBase', 'ContactType', 'ContactStatus',
    'ContactClient', 'ContactClientBase', 'ContactRole',
    'ContactProject', 'ContactProjectBase', 'ProjectRole',
    'Notebook', 'NotebookBase',
    'Project', 'ProjectBase', 'ProjectStatus', 'ConfidentialityLevel', 'ProjectKnowledge',
    'ProjectClient', 'ProjectClientBase', 'ClientProjectRole',
    'Reminder', 'ReminderBase', 'ReminderStatus',
    'Task', 'TaskBase', 'TaskStatus',
]

