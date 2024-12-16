#models/domain/operations_ability_receive_email.py
from dataclasses import dataclass
from typing import Dict, List, Optional

@dataclass
class WorkflowStep:
    name: str
    type: str
    description: str
    config: Optional[Dict] = None

@dataclass
class EmailOperation:
    operation_name: str
    description: str
    workflow_steps: List[WorkflowStep]
    input_schema: Dict
    output_schema: Dict
    constraints: Dict
    permissions: Dict

EMAIL_OPERATIONS = {
    "RECEIVE_INBOUND_EMAIL": EmailOperation(
        operation_name="RECEIVE_INBOUND_EMAIL",
        description="Receives an incoming email and stores it for processing",
        workflow_steps=[
            WorkflowStep(name="validate_input", type="validation", description="Validates the incoming email data"),
            WorkflowStep(name="store_email", type="database", description="Stores the email in the database")
        ],
        input_schema={
            "type": "object",
            "properties": {
                "raw_email": {"type": "string", "minLength": 1},
                "metadata": {"type": "object"}
            },
            "required": ["raw_email"]
        },
        output_schema={
            "type": "object",
            "properties": {
                "email_id": {"type": "integer"},
                "status": {"type": "string"}
            }
        },
        constraints={
            "rate_limit": 500
        },
        permissions={
            "required_roles": ["user", "admin"],
            "required_scopes": ["email:receive"]
        }
    ),
    "ROUTE_EMAIL_TO_MAIN_ABILITY": EmailOperation(
        operation_name="ROUTE_EMAIL_TO_MAIN_ABILITY",
        description="Routes a stored email to the main Ability class for further processing",
        workflow_steps=[
            WorkflowStep(name="validate_email_id", type="validation", description="Checks if email_id is valid"),
            WorkflowStep(name="route_to_main", type="integration", description="Sends the email to main ability workflow")
        ],
        input_schema={
            "type": "object",
            "properties": {
                "email_id": {"type": "integer"}
            },
            "required": ["email_id"]
        },
        output_schema={
            "type": "object",
            "properties": {
                "routed": {"type": "boolean"},
                "status": {"type": "string"}
            }
        },
        constraints={
            "rate_limit": 1000
        },
        permissions={
            "required_roles": ["user", "admin"],
            "required_scopes": ["email:route"]
        }
    )
}
