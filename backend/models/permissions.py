# models/permissions.py
"""
Centralized permission system for LegalVault.

This module consolidates all operation and permission enums from the workspace
domain, providing a single source of truth for permission validation.

Usage:
    from models.permissions import (
        ClientOperation, ClientPermission,
        validate_operation_constraints,
        get_required_permissions
    )

    # Validate if user can perform operation
    if validate_operation_constraints(
        ClientOperation.CREATE_CLIENT,
        CLIENT_OPERATION_PERMISSIONS,
        user_permissions
    ):
        # Proceed with operation
        pass
"""

from enum import Enum
from typing import Dict, List, TypeVar

# Type variable for generic operation enums
OperationType = TypeVar('OperationType', bound=Enum)
PermissionType = TypeVar('PermissionType', bound=Enum)


# =============================================================================
# CLIENT OPERATIONS & PERMISSIONS
# =============================================================================

class ClientOperation(str, Enum):
    """Enumeration of available client operations"""
    CREATE_CLIENT = "create_client"
    UPDATE_CLIENT = "update_client"
    GET_CLIENT = "get_client"
    LIST_CLIENTS = "list_clients"
    UPDATE_CORE_DETAILS = "update_core_details"
    UPDATE_CONTACT_INFO = "update_contact_info"
    UPDATE_BUSINESS_INFO = "update_business_info"
    UPDATE_PROFILE = "update_profile"
    UPDATE_PREFERENCES = "update_preferences"
    MANAGE_TAGS = "manage_tags"
    DEACTIVATE_CLIENT = "deactivate_client"
    REACTIVATE_CLIENT = "reactivate_client"
    DELETE_CLIENT = "delete_client"

    # Tenant operations
    VALIDATE_TENANT_RULES = "validate_tenant_rules"
    GET_TENANT_PREFERENCES = "get_tenant_preferences"

    # Relationship operations
    ADD_CONTACT = "add_contact"
    REMOVE_CONTACT = "remove_contact"
    ADD_DOCUMENT = "add_document"
    REMOVE_DOCUMENT = "remove_document"
    ADD_PROJECT = "add_project"
    REMOVE_PROJECT = "remove_project"
    ADD_USER = "add_user"
    REMOVE_USER = "remove_user"


class ClientPermission(str, Enum):
    """Enumeration of client-related permissions"""
    CREATE = "client:create"
    READ = "client:read"
    UPDATE = "client:update"
    DELETE = "client:delete"
    MANAGE_CORE = "client:manage_core"
    MANAGE_CONTACT = "client:manage_contact"
    MANAGE_BUSINESS = "client:manage_business"
    MANAGE_PROFILE = "client:manage_profile"
    MANAGE_PREFERENCES = "client:manage_preferences"
    MANAGE_TAGS = "client:manage_tags"
    MANAGE_STATUS = "client:manage_status"
    MANAGE_RELATIONSHIPS = "client:manage_relationships"
    VIEW_SENSITIVE = "client:view_sensitive"
    MANAGE_TENANT_RULES = "client:manage_tenant_rules"


CLIENT_OPERATION_PERMISSIONS: Dict[ClientOperation, List[ClientPermission]] = {
    # Core operations
    ClientOperation.CREATE_CLIENT: [ClientPermission.CREATE],
    ClientOperation.UPDATE_CLIENT: [ClientPermission.UPDATE],
    ClientOperation.GET_CLIENT: [ClientPermission.READ],
    ClientOperation.LIST_CLIENTS: [ClientPermission.READ],
    ClientOperation.DELETE_CLIENT: [ClientPermission.DELETE],

    # Tenant-specific operations
    ClientOperation.VALIDATE_TENANT_RULES: [
        ClientPermission.READ,
        ClientPermission.MANAGE_TENANT_RULES
    ],
    ClientOperation.GET_TENANT_PREFERENCES: [
        ClientPermission.READ,
        ClientPermission.MANAGE_TENANT_RULES
    ],

    # Detailed update operations
    ClientOperation.UPDATE_CORE_DETAILS: [
        ClientPermission.UPDATE,
        ClientPermission.MANAGE_CORE
    ],
    ClientOperation.UPDATE_CONTACT_INFO: [
        ClientPermission.UPDATE,
        ClientPermission.MANAGE_CONTACT
    ],
    ClientOperation.UPDATE_BUSINESS_INFO: [
        ClientPermission.UPDATE,
        ClientPermission.MANAGE_BUSINESS,
        ClientPermission.VIEW_SENSITIVE
    ],
    ClientOperation.UPDATE_PROFILE: [
        ClientPermission.UPDATE,
        ClientPermission.MANAGE_PROFILE
    ],
    ClientOperation.UPDATE_PREFERENCES: [
        ClientPermission.UPDATE,
        ClientPermission.MANAGE_PREFERENCES
    ],
    ClientOperation.MANAGE_TAGS: [
        ClientPermission.UPDATE,
        ClientPermission.MANAGE_TAGS
    ],

    # Status management
    ClientOperation.DEACTIVATE_CLIENT: [
        ClientPermission.UPDATE,
        ClientPermission.MANAGE_STATUS
    ],
    ClientOperation.REACTIVATE_CLIENT: [
        ClientPermission.UPDATE,
        ClientPermission.MANAGE_STATUS
    ],

    # Relationship management operations
    ClientOperation.ADD_CONTACT: [
        ClientPermission.UPDATE,
        ClientPermission.MANAGE_RELATIONSHIPS
    ],
    ClientOperation.REMOVE_CONTACT: [
        ClientPermission.UPDATE,
        ClientPermission.MANAGE_RELATIONSHIPS
    ],
    ClientOperation.ADD_DOCUMENT: [
        ClientPermission.UPDATE,
        ClientPermission.MANAGE_RELATIONSHIPS
    ],
    ClientOperation.REMOVE_DOCUMENT: [
        ClientPermission.UPDATE,
        ClientPermission.MANAGE_RELATIONSHIPS
    ],
    ClientOperation.ADD_PROJECT: [
        ClientPermission.UPDATE,
        ClientPermission.MANAGE_RELATIONSHIPS
    ],
    ClientOperation.REMOVE_PROJECT: [
        ClientPermission.UPDATE,
        ClientPermission.MANAGE_RELATIONSHIPS
    ],
    ClientOperation.ADD_USER: [
        ClientPermission.UPDATE,
        ClientPermission.MANAGE_RELATIONSHIPS
    ],
    ClientOperation.REMOVE_USER: [
        ClientPermission.UPDATE,
        ClientPermission.MANAGE_RELATIONSHIPS
    ],
}


# =============================================================================
# PROJECT OPERATIONS & PERMISSIONS
# =============================================================================

class ProjectOperation(str, Enum):
    """Enumeration of available project operations"""
    CREATE_PROJECT = "create_project"
    UPDATE_PROJECT = "update_project"
    GET_PROJECT = "get_project"
    LIST_PROJECTS = "list_projects"
    UPDATE_STATUS = "update_status"
    UPDATE_KNOWLEDGE = "update_knowledge"
    UPDATE_SUMMARY = "update_summary"
    ARCHIVE_PROJECT = "archive_project"
    ADD_TAGS = "add_tags"
    REMOVE_TAGS = "remove_tags"
    UPDATE_CONFIDENTIALITY = "update_confidentiality"


class ProjectPermission(str, Enum):
    """Enumeration of project-related permissions"""
    CREATE = "project:create"
    READ = "project:read"
    UPDATE = "project:update"
    DELETE = "project:delete"
    ARCHIVE = "project:archive"
    MANAGE_CONFIDENTIALITY = "project:manage_confidentiality"


PROJECT_OPERATION_PERMISSIONS: Dict[ProjectOperation, List[ProjectPermission]] = {
    ProjectOperation.CREATE_PROJECT: [ProjectPermission.CREATE],
    ProjectOperation.UPDATE_PROJECT: [ProjectPermission.UPDATE],
    ProjectOperation.GET_PROJECT: [ProjectPermission.READ],
    ProjectOperation.LIST_PROJECTS: [ProjectPermission.READ],
    ProjectOperation.UPDATE_STATUS: [ProjectPermission.UPDATE],
    ProjectOperation.UPDATE_KNOWLEDGE: [ProjectPermission.UPDATE],
    ProjectOperation.UPDATE_SUMMARY: [ProjectPermission.UPDATE],
    ProjectOperation.ARCHIVE_PROJECT: [ProjectPermission.ARCHIVE],
    ProjectOperation.ADD_TAGS: [ProjectPermission.UPDATE],
    ProjectOperation.REMOVE_TAGS: [ProjectPermission.UPDATE],
    ProjectOperation.UPDATE_CONFIDENTIALITY: [ProjectPermission.MANAGE_CONFIDENTIALITY],
}


# =============================================================================
# TASK OPERATIONS & PERMISSIONS
# =============================================================================

class TaskOperation(str, Enum):
    """Enumeration of available task operations"""
    CREATE_TASK = "create_task"
    UPDATE_TASK = "update_task"
    GET_TASK = "get_task"
    LIST_TASKS = "list_tasks"
    LIST_PROJECT_TASKS = "list_project_tasks"
    COMPLETE_TASK = "complete_task"
    REOPEN_TASK = "reopen_task"
    DELETE_TASK = "delete_task"
    REASSIGN_TASK = "reassign_task"
    UPDATE_DUE_DATE = "update_due_date"


class TaskPermission(str, Enum):
    """Enumeration of task-related permissions"""
    CREATE = "task:create"
    READ = "task:read"
    UPDATE = "task:update"
    DELETE = "task:delete"
    COMPLETE = "task:complete"
    REOPEN = "task:reopen"
    REASSIGN = "task:reassign"
    MANAGE_DATES = "task:manage_dates"


TASK_OPERATION_PERMISSIONS: Dict[TaskOperation, List[TaskPermission]] = {
    TaskOperation.CREATE_TASK: [TaskPermission.CREATE],
    TaskOperation.UPDATE_TASK: [TaskPermission.UPDATE],
    TaskOperation.GET_TASK: [TaskPermission.READ],
    TaskOperation.LIST_TASKS: [TaskPermission.READ],
    TaskOperation.LIST_PROJECT_TASKS: [TaskPermission.READ],
    TaskOperation.COMPLETE_TASK: [TaskPermission.COMPLETE],
    TaskOperation.REOPEN_TASK: [TaskPermission.REOPEN],
    TaskOperation.DELETE_TASK: [TaskPermission.DELETE],
    TaskOperation.REASSIGN_TASK: [TaskPermission.UPDATE, TaskPermission.REASSIGN],
    TaskOperation.UPDATE_DUE_DATE: [TaskPermission.UPDATE, TaskPermission.MANAGE_DATES],
}


# =============================================================================
# NOTEBOOK OPERATIONS & PERMISSIONS
# =============================================================================

class NotebookOperation(str, Enum):
    """Enumeration of available notebook operations"""
    CREATE_NOTEBOOK = "create_notebook"
    GET_NOTEBOOK = "get_notebook"
    UPDATE_CONTENT = "update_content"
    UPDATE_TITLE = "update_title"
    ADD_TAGS = "add_tags"
    REMOVE_TAGS = "remove_tags"
    ARCHIVE_NOTEBOOK = "archive_notebook"
    UNARCHIVE_NOTEBOOK = "unarchive_notebook"
    LIST_PROJECT_NOTEBOOKS = "list_project_notebooks"


class NotebookPermission(str, Enum):
    """Enumeration of notebook-related permissions"""
    CREATE = "notebook:create"
    READ = "notebook:read"
    UPDATE = "notebook:update"
    ARCHIVE = "notebook:archive"
    UNARCHIVE = "notebook:unarchive"
    MANAGE_TAGS = "notebook:manage_tags"


NOTEBOOK_OPERATION_PERMISSIONS: Dict[NotebookOperation, List[NotebookPermission]] = {
    NotebookOperation.CREATE_NOTEBOOK: [NotebookPermission.CREATE],
    NotebookOperation.GET_NOTEBOOK: [NotebookPermission.READ],
    NotebookOperation.UPDATE_CONTENT: [NotebookPermission.UPDATE],
    NotebookOperation.UPDATE_TITLE: [NotebookPermission.UPDATE],
    NotebookOperation.ADD_TAGS: [NotebookPermission.MANAGE_TAGS],
    NotebookOperation.REMOVE_TAGS: [NotebookPermission.MANAGE_TAGS],
    NotebookOperation.ARCHIVE_NOTEBOOK: [NotebookPermission.ARCHIVE],
    NotebookOperation.UNARCHIVE_NOTEBOOK: [NotebookPermission.UNARCHIVE],
    NotebookOperation.LIST_PROJECT_NOTEBOOKS: [NotebookPermission.READ],
}


# =============================================================================
# REMINDER OPERATIONS & PERMISSIONS
# =============================================================================

class ReminderOperation(str, Enum):
    """Enumeration of available reminder operations"""
    CREATE_REMINDER = "create_reminder"
    UPDATE_REMINDER = "update_reminder"
    GET_REMINDER = "get_reminder"
    LIST_REMINDERS = "list_reminders"
    LIST_PROJECT_REMINDERS = "list_project_reminders"
    COMPLETE_REMINDER = "complete_reminder"
    DELETE_REMINDER = "delete_reminder"
    UPDATE_DUE_DATE = "update_due_date"


class ReminderPermission(str, Enum):
    """Enumeration of reminder-related permissions"""
    CREATE = "reminder:create"
    READ = "reminder:read"
    UPDATE = "reminder:update"
    DELETE = "reminder:delete"
    COMPLETE = "reminder:complete"
    MANAGE_DATES = "reminder:manage_dates"


REMINDER_OPERATION_PERMISSIONS: Dict[ReminderOperation, List[ReminderPermission]] = {
    ReminderOperation.CREATE_REMINDER: [ReminderPermission.CREATE],
    ReminderOperation.UPDATE_REMINDER: [ReminderPermission.UPDATE],
    ReminderOperation.GET_REMINDER: [ReminderPermission.READ],
    ReminderOperation.LIST_REMINDERS: [ReminderPermission.READ],
    ReminderOperation.LIST_PROJECT_REMINDERS: [ReminderPermission.READ],
    ReminderOperation.COMPLETE_REMINDER: [ReminderPermission.COMPLETE],
    ReminderOperation.DELETE_REMINDER: [ReminderPermission.DELETE],
    ReminderOperation.UPDATE_DUE_DATE: [ReminderPermission.MANAGE_DATES],
}


# =============================================================================
# GENERIC PERMISSION VALIDATION FUNCTIONS
# =============================================================================

def validate_operation_constraints(
    operation: Enum,
    permission_mapping: Dict[Enum, List[Enum]],
    user_permissions: List[str]
) -> bool:
    """
    Validates if an operation can be performed based on user permissions.

    This is a generic validator that works with any Operation/Permission enum pair.

    Args:
        operation: The operation to be performed (e.g., ClientOperation.CREATE_CLIENT)
        permission_mapping: The mapping dict for this entity type
                           (e.g., CLIENT_OPERATION_PERMISSIONS)
        user_permissions: List of permission strings the user has

    Returns:
        bool: True if user has all required permissions, False otherwise

    Example:
        >>> validate_operation_constraints(
        ...     ClientOperation.CREATE_CLIENT,
        ...     CLIENT_OPERATION_PERMISSIONS,
        ...     ["client:create", "client:read"]
        ... )
        True
    """
    required_permissions = permission_mapping.get(operation, [])
    return all(perm.value in user_permissions for perm in required_permissions)


def get_required_permissions(
    operation: Enum,
    permission_mapping: Dict[Enum, List[Enum]]
) -> List[str]:
    """
    Gets list of required permissions for an operation.

    Args:
        operation: The operation to check
        permission_mapping: The mapping dict for this entity type

    Returns:
        List[str]: List of required permission strings

    Example:
        >>> get_required_permissions(
        ...     TaskOperation.REASSIGN_TASK,
        ...     TASK_OPERATION_PERMISSIONS
        ... )
        ['task:update', 'task:reassign']
    """
    permissions = permission_mapping.get(operation, [])
    return [perm.value for perm in permissions]


# =============================================================================
# ENTITY-SPECIFIC HELPER FUNCTIONS
# =============================================================================

def check_sensitive_data_access(user_permissions: List[str]) -> bool:
    """
    Checks if user has permission to access sensitive client data.

    Args:
        user_permissions: List of permission strings the user has

    Returns:
        bool: True if user can access sensitive data, False otherwise
    """
    return ClientPermission.VIEW_SENSITIVE.value in user_permissions


# =============================================================================
# CONVENIENCE WRAPPERS (for backwards compatibility)
# =============================================================================

def validate_client_operation(
    operation: ClientOperation,
    user_permissions: List[str]
) -> bool:
    """Validate a client operation against user permissions."""
    return validate_operation_constraints(
        operation, CLIENT_OPERATION_PERMISSIONS, user_permissions
    )


def validate_project_operation(
    operation: ProjectOperation,
    user_permissions: List[str]
) -> bool:
    """Validate a project operation against user permissions."""
    return validate_operation_constraints(
        operation, PROJECT_OPERATION_PERMISSIONS, user_permissions
    )


def validate_task_operation(
    operation: TaskOperation,
    user_permissions: List[str]
) -> bool:
    """Validate a task operation against user permissions."""
    return validate_operation_constraints(
        operation, TASK_OPERATION_PERMISSIONS, user_permissions
    )


def validate_notebook_operation(
    operation: NotebookOperation,
    user_permissions: List[str]
) -> bool:
    """Validate a notebook operation against user permissions."""
    return validate_operation_constraints(
        operation, NOTEBOOK_OPERATION_PERMISSIONS, user_permissions
    )


def validate_reminder_operation(
    operation: ReminderOperation,
    user_permissions: List[str]
) -> bool:
    """Validate a reminder operation against user permissions."""
    return validate_operation_constraints(
        operation, REMINDER_OPERATION_PERMISSIONS, user_permissions
    )
