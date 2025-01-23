# services/workflow/library/masterfiledatabase_workflow.py

from typing import List, Dict, Any, Optional
from uuid import UUID
from fastapi import BackgroundTasks
from sqlmodel import Session

from models.domain.library.operations_masterfiledatabase import MasterFileOperations
# from core.database import get_session
# from core.logging import logger

# Importing FileProcessor and VectorProcessor classes here
# from services.executors.library.file_processor import FileProcessor
# from services.executors.library.vector_processor import VectorProcessor


class MasterFileWorkflow:
    def __init__(self, session: Session):
        self.session = session
        self.ops = MasterFileOperations(session)
        self.file_processor = FileProcessor()
        self.vector_processor = VectorProcessor()

    async def process_new_file(self, file_id: UUID, background_tasks: BackgroundTasks) -> None:
        domain_file = await self.ops.get_file(file_id)
        if not domain_file:
            return

        background_tasks.add_task(self._process_file_async, file_id)

    async def _process_file_async(self, file_id: UUID) -> None:
        try:
            domain_file = await self.ops.update_file_status(file_id, "start_processing")
            if not domain_file:
                return

            # Extract metadata and content
            metadata = await self.file_processor.extract_metadata(domain_file.db_model.external_url)
            content = await self.file_processor.extract_content(domain_file.db_model.external_url)

            # Generate embeddings
            embeddings = await self.vector_processor.create_embeddings(content)

            # Update file with processed data
            await self.ops.update_metadata(file_id, metadata)
            await self.ops.update_content_details(file_id, {
                "embeddings": embeddings,
                "content_processed": True
            })

            await self.ops.update_file_status(file_id, "finish_processing")

        except Exception as e:
            logger.error(f"Error processing file {file_id}: {str(e)}")
            await self.ops.update_file_status(file_id, "available")

    async def handle_file_update(self, file_id: UUID, background_tasks: BackgroundTasks) -> None:
        background_tasks.add_task(self._handle_update_async, file_id)

    async def _handle_update_async(self, file_id: UUID) -> None:
        try:
            domain_file = await self.ops.update_file_status(file_id, "start_processing")
            if not domain_file:
                return

            # Re-process file content and update vectors
            content = await self.file_processor.extract_content(domain_file.db_model.external_url)
            new_embeddings = await self.vector_processor.create_embeddings(content)

            await self.vector_processor.update_vectors(file_id, new_embeddings)
            await self.ops.update_file_status(file_id, "finish_processing")

        except Exception as e:
            logger.error(f"Error handling file update {file_id}: {str(e)}")
            await self.ops.update_file_status(file_id, "available")

    async def batch_process_files(self, file_ids: List[UUID], background_tasks: BackgroundTasks) -> None:
        for file_id in file_ids:
            background_tasks.add_task(self._process_file_async, file_id)