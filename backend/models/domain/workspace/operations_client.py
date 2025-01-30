# models/domain/workspace/operations_client.py

from enum import Enum
from typing import List


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
    VIEW_SENSITIVE = "client:view_sensitive"  # For tax ID, registration numbers etc.
    MANAGE_TENANT_RULES = "client:manage_tenant_rules"


# Map operations to required permissions
OPERATION_PERMISSIONS = {
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


def validate_operation_constraints(operation: ClientOperation, user_permissions: List[str]) -> bool:
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


def get_required_permissions(operation: ClientOperation) -> List[str]:
    """
    Gets list of required permissions for an operation.

    Args:
        operation: The operation to check

    Returns:
        List[str]: List of required permission strings
    """
    return [perm.value for perm in OPERATION_PERMISSIONS[operation]]


def check_sensitive_data_access(user_permissions: List[str]) -> bool:
    """
    Checks if user has permission to access sensitive client data.

    Args:
        user_permissions: List of permission strings the user has

    Returns:
        bool: True if user can access sensitive data, False otherwise
    """
    return ClientPermission.VIEW_SENSITIVE.value in user_permissions