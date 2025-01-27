# backend/models/domain/ability_taskmanagement.py
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, Optional


@dataclass
class TaskManagementAbilityDomain:
    id: Optional[int]
    ability_id: int
    operation_name: str
    description: str
    enabled: bool = True
    input_schema: Dict = dict()
    output_schema: Dict = dict()
    workflow_steps: Dict = dict()
    constraints: Dict = dict()
    permissions: Dict = dict()
    created_at: datetime = datetime.utcnow()
    updated_at: datetime = datetime.utcnow()

    def validate_operation(self) -> bool:
        return True

    def execute_workflow(self) -> Dict:
        return {"status": "success"}

    def update_schema(self, input_schema: Optional[Dict] = None, output_schema: Optional[Dict] = None) -> None:
        if input_schema is not None:
            self.input_schema = input_schema
            self.updated_at = datetime.utcnow()
        if output_schema is not None:
            self.output_schema = output_schema
            self.updated_at = datetime.utcnow()
