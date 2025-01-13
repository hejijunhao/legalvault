# services/workflow/longterm_memory/educational_knowledge_workflow.py

from models.domain.longterm_memory.operations_educational_knowledge import (
    EducationalKnowledgeOperationInput,
    EducationalKnowledgeOperationOutput
)
from services.executors.longterm_memory.educational_knowledge_executor import EducationalKnowledgeExecutor


class EducationalKnowledgeWorkflow:
    """Workflow manager for educational knowledge operations."""

    def __init__(self):
        self.executor = EducationalKnowledgeExecutor()

    async def process_operation(
        self,
        operation_input: EducationalKnowledgeOperationInput
    ) -> EducationalKnowledgeOperationOutput:
        """Process educational knowledge operation through workflow."""
        # Validate operation input
        if operation_input.operation.requires_prompt and not operation_input.prompt:
            return EducationalKnowledgeOperationOutput(
                success=False,
                error="Prompt required for this operation"
            )

        if operation_input.operation.requires_education_type and not operation_input.education_type:
            return EducationalKnowledgeOperationOutput(
                success=False,
                error="Education type required for this operation"
            )

        # Execute operation
        return await self.executor.execute(operation_input)