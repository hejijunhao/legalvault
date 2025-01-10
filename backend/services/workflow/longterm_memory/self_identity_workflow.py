# services/workflow/longterm_memory/self_identity_workflow.py

from models.domain.longterm_memory.operations_self_identity import (
    SelfIdentityOperationInput,
    SelfIdentityOperationOutput
)
from services.executors.longterm_memory.self_identity_executor import SelfIdentityExecutor


class SelfIdentityWorkflow:
    """Workflow manager for self-identity operations."""

    def __init__(self):
        self.executor = SelfIdentityExecutor()

    async def process_operation(
        self,
        operation_input: SelfIdentityOperationInput
    ) -> SelfIdentityOperationOutput:
        """Process self-identity operation through workflow."""
        # Validate operation input
        if operation_input.operation.requires_prompt and not operation_input.prompt:
            return SelfIdentityOperationOutput(
                success=False,
                error="Prompt required for this operation"
            )

        # Execute operation
        return await self.executor.execute(operation_input)