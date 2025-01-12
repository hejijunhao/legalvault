# services/workflow/longterm_memory/global_knowledge_workflow.py

from models.domain.longterm_memory.operations_global_knowledge import (
    GlobalKnowledgeOperationInput,
    GlobalKnowledgeOperationOutput
)
from services.executors.longterm_memory.global_knowledge_executor import GlobalKnowledgeExecutor


class GlobalKnowledgeWorkflow:
    """Workflow manager for global knowledge operations."""

    def __init__(self):
        self.executor = GlobalKnowledgeExecutor()

    async def process_operation(
        self,
        operation_input: GlobalKnowledgeOperationInput
    ) -> GlobalKnowledgeOperationOutput:
        """Process global knowledge operation through workflow."""
        # Validate operation input
        if operation_input.operation.requires_prompt and not operation_input.prompt:
            return GlobalKnowledgeOperationOutput(
                success=False,
                error="Prompt required for this operation"
            )

        if operation_input.operation.requires_knowledge_type and not operation_input.knowledge_type:
            return GlobalKnowledgeOperationOutput(
                success=False,
                error="Knowledge type required for this operation"
            )

        # Execute operation
        return await self.executor.execute(operation_input)