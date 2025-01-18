# models/domain/workspace/operations_task.py

from enum import Enum
from typing import List


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


# Map operations to required permissions
OPERATION_PERMISSIONS = {
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


def validate_operation_constraints(operation: TaskOperation, user_permissions: List[str]) -> bool:
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


def get_required_permissions(operation: TaskOperation) -> List[str]:
    """
    Gets list of required permissions for an operation.

    Args:
        operation: The operation to check

    Returns:
        List[str]: List of required permission strings
    """
    return [perm.value for perm in OPERATION_PERMISSIONS[operation]]