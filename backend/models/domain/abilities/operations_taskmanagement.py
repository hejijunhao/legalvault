# backend/models/domain/operations_taskmanagement.py
from dataclasses import dataclass
from typing import Dict, List, Optional


@dataclass
class WorkflowStep:
    name: str
    type: str
    description: str
    config: Optional[Dict] = None


@dataclass
class TaskOperation:
    operation_name: str
    description: str
    workflow_steps: List[WorkflowStep]
    input_schema: Dict
    output_schema: Dict
    constraints: Dict
    permissions: Dict


TASK_OPERATIONS = {
    "CREATE_TASK": TaskOperation(
        operation_name="CREATE_TASK",
        description="Creates a new task in the system",
        workflow_steps=[
            WorkflowStep(
                name="validate_input",
                type="validation",
                description="Validates the incoming task data"
            ),
            WorkflowStep(
                name="extract_metadata",
                type="processing",
                description="Extracts and processes task metadata"
            ),
            WorkflowStep(
                name="store_task",
                type="database",
                description="Stores the task in the database"
            ),
            WorkflowStep(
                name="notify_user",
                type="notification",
                description="Notifies relevant users about task creation"
            )
        ],
        input_schema={
            "type": "object",
            "properties": {
                "title": {"type": "string", "minLength": 1, "maxLength": 200},
                "description": {"type": "string"},
                "due_date": {"type": "string", "format": "date-time"},
                "priority": {"type": "string", "enum": ["low", "medium", "high"]}
            },
            "required": ["title", "description"]
        },
        output_schema={
            "type": "object",
            "properties": {
                "task_id": {"type": "integer"},
                "status": {"type": "string"},
                "created_at": {"type": "string", "format": "date-time"}
            }
        },
        constraints={
            "max_title_length": 200,
            "rate_limit": 100,
            "allowed_priorities": ["low", "medium", "high"]
        },
        permissions={
            "required_roles": ["user", "admin"],
            "required_scopes": ["task:write"]
        }
    ),
    "GET_TASK": TaskOperation(
        operation_name="GET_TASK",
        description="Retrieves a specific task by ID",
        workflow_steps=[
            WorkflowStep(
                name="validate_input",
                type="validation",
                description="Validates the task ID"
            ),
            WorkflowStep(
                name="check_permissions",
                type="authorization",
                description="Verifies user has permission to view task"
            ),
            WorkflowStep(
                name="fetch_task",
                type="database",
                description="Retrieves task from database"
            )
        ],
        input_schema={
            "type": "object",
            "properties": {
                "task_id": {"type": "integer"}
            },
            "required": ["task_id"]
        },
        output_schema={
            "type": "object",
            "properties": {
                "task_id": {"type": "integer"},
                "title": {"type": "string"},
                "description": {"type": "string"},
                "status": {"type": "string"},
                "created_at": {"type": "string", "format": "date-time"}
            }
        },
        constraints={
            "rate_limit": 1000
        },
        permissions={
            "required_roles": ["user", "admin"],
            "required_scopes": ["task:read"]
        }
    ),
    "LIST_TASKS": TaskOperation(
        operation_name="LIST_TASKS",
        description="Retrieves a list of tasks with optional filtering",
        workflow_steps=[
            WorkflowStep(
                name="validate_filters",
                type="validation",
                description="Validates the filter parameters"
            ),
            WorkflowStep(
                name="apply_filters",
                type="processing",
                description="Applies filters to task query"
            ),
            WorkflowStep(
                name="fetch_tasks",
                type="database",
                description="Retrieves filtered tasks from database"
            )
        ],
        input_schema={
            "type": "object",
            "properties": {
                "status": {"type": "string", "enum": ["pending", "in_progress", "completed"]},
                "priority": {"type": "string", "enum": ["low", "medium", "high"]},
                "page": {"type": "integer", "minimum": 1},
                "page_size": {"type": "integer", "minimum": 1, "maximum": 100}
            }
        },
        output_schema={
            "type": "object",
            "properties": {
                "tasks": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "task_id": {"type": "integer"},
                            "title": {"type": "string"},
                            "status": {"type": "string"},
                            "priority": {"type": "string"}
                        }
                    }
                },
                "total": {"type": "integer"},
                "page": {"type": "integer"}
            }
        },
        constraints={
            "max_page_size": 100,
            "rate_limit": 1000
        },
        permissions={
            "required_roles": ["user", "admin"],
            "required_scopes": ["task:read"]
        }
    )
}