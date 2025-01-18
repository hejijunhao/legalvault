# models/domain/workspace/operations_reminder.py

from enum import Enum
from typing import List


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


# Map operations to required permissions
OPERATION_PERMISSIONS = {
    ReminderOperation.CREATE_REMINDER: [ReminderPermission.CREATE],
    ReminderOperation.UPDATE_REMINDER: [ReminderPermission.UPDATE],
    ReminderOperation.GET_REMINDER: [ReminderPermission.READ],
    ReminderOperation.LIST_REMINDERS: [ReminderPermission.READ],
    ReminderOperation.LIST_PROJECT_REMINDERS: [ReminderPermission.READ],
    ReminderOperation.COMPLETE_REMINDER: [ReminderPermission.COMPLETE],
    ReminderOperation.DELETE_REMINDER: [ReminderPermission.DELETE],
    ReminderOperation.UPDATE_DUE_DATE: [ReminderPermission.MANAGE_DATES],
}


def validate_operation_constraints(operation: ReminderOperation, user_permissions: List[str]) -> bool:
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


def get_required_permissions(operation: ReminderOperation) -> List[str]:
    """
    Gets list of required permissions for an operation.

    Args:
        operation: The operation to check

    Returns:
        List[str]: List of required permission strings
    """
    return [perm.value for perm in OPERATION_PERMISSIONS[operation]]