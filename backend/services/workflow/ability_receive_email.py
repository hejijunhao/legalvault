from typing import Dict, Any, Optional
from dataclasses import dataclass
from logging import getLogger

logger = getLogger(__name__)

@dataclass
class WorkflowContext:
    operation_name: str
    input_data: Dict[str, Any]
    user_id: int
    metadata: Optional[Dict] = None

class ReceiveEmailWorkflow:
    def __init__(self, executor):
        self.executor = executor

    async def execute_workflow(self, context: WorkflowContext) -> Dict[str, Any]:
        try:
            if not hasattr(self.executor, context.operation_name.lower()):
                raise ValueError(f"Unknown operation: {context.operation_name}")

            operation = getattr(self.executor, context.operation_name.lower())
            result = await operation(
                input_data=context.input_data,
                user_id=context.user_id,
                metadata=context.metadata
            )

            return {"status": "success", "data": result}
        except Exception as e:
            logger.error(f"Workflow execution failed: {str(e)}")
            return {"status": "error", "error": str(e)}

    async def validate_workflow(self, context: WorkflowContext) -> bool:
        # Add validation logic if needed (e.g., schema validation, permissions)
        return True
