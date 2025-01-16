# backend/models/domain/workspace/operations_notebook.py

from enum import Enum
from typing import List


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


# Map operations to required permissions
OPERATION_PERMISSIONS = {
    NotebookOperation.CREATE_NOTEBOOK: [NotebookPermission.CREATE],
    NotebookOperation.GET_NOTEBOOK: [NotebookPermission.READ],
    NotebookOperation.UPDATE_CONTENT: [NotebookPermission.UPDATE],
    NotebookOperation.UPDATE_TITLE: [NotebookPermission.UPDATE],
    NotebookOperation.ADD_TAGS: [NotebookPermission.MANAGE_TAGS],
    NotebookOperation.REMOVE_TAGS: [NotebookPermission.MANAGE_TAGS],
    NotebookOperation.ARCHIVE_NOTEBOOK: [NotebookPermission.ARCHIVE],
    NotebookOperation.UNARCHIVE_NOTEBOOK: [NotebookPermission.UNARCHIVE],
    NotebookOperation.LIST_PROJECT_NOTEBOOKS: [NotebookPermission.READ]
}


def validate_operation_constraints(operation: NotebookOperation, user_permissions: List[str]) -> bool:
    """
    Validates if an operation can be performed based on user permissions.

    Args:
        operation: The operation to be performed
        user_permissions: List of permission strings the user has

    Returns:
        bool: True if user has required permissions, False otherwise
    """
    required_permissions = OPERATION_PERMISSIONS[operation]
    return all(perm.value in user_permissions for perm in required_permissions)


def get_required_permissions(operation: NotebookOperation) -> List[str]:
    """
    Gets list of required permissions for an operation.

    Args:
        operation: The operation to check

    Returns:
        List[str]: List of required permission strings
    """
    return [perm.value for perm in OPERATION_PERMISSIONS[operation]]