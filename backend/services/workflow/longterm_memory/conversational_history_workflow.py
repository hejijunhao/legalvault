# services/workflow/longterm_memory/conversational_history_workflow.py

from models.domain.longterm_memory.operations_conversational_history import (
    ConversationalHistoryOperationInput,
    ConversationalHistoryOperationOutput
)
from services.executors.longterm_memory.conversational_history_executor import (
    ConversationalHistoryExecutor
)
from typing import Optional


class ConversationalHistoryWorkflow:
    """Workflow manager for conversational history operations."""

    def __init__(self):
        self.executor = ConversationalHistoryExecutor()

    async def process_operation(
        self,
        operation_input: ConversationalHistoryOperationInput
    ) -> ConversationalHistoryOperationOutput:
        """Process conversational history operation through workflow."""
        # Validate operation input
        if operation_input.operation.requires_prompts:
            validation_error = self._validate_prompts(operation_input)
            if validation_error:
                return ConversationalHistoryOperationOutput(
                    success=False,
                    error=validation_error
                )

        # Execute operation
        return await self.executor.execute(operation_input)

    def _validate_prompts(
        self,
        operation_input: ConversationalHistoryOperationInput
    ) -> Optional[str]:
        """Validate prompts for operations that require them."""
        if operation_input.operation.value == "create":
            if not operation_input.summary or not operation_input.context:
                return "Both summary and context prompts are required for create operation"
        elif operation_input.operation.value == "update":
            if not operation_input.summary and not operation_input.context:
                return "At least one of summary or context prompt is required for update operation"
        return None