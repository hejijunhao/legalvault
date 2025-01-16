# models/domain/workspace/operations_project.py

from enum import Enum
from typing import List


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


# Map operations to required permissions
OPERATION_PERMISSIONS = {
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


def validate_operation_constraints(operation: ProjectOperation, user_permissions: List[str]) -> bool:
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


def get_required_permissions(operation: ProjectOperation) -> List[str]:
    """
    Gets list of required permissions for an operation.

    Args:
        operation: The operation to check

    Returns:
        List[str]: List of required permission strings
    """
    return [perm.value for perm in OPERATION_PERMISSIONS[operation]]