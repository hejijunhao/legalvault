# services/workflow/workspace/client_workflow.py

from typing import List, Optional
from uuid import UUID
from fastapi import HTTPException, Depends
from sqlmodel import Session

from core.database import get_session
from models.database.workspace.client import ClientStatus, LegalEntityType
from models.domain.workspace.operations_client import (
    ClientOperation,
    validate_operation_constraints,
    check_sensitive_data_access
)
from models.schemas.workspace.client import (
    ClientCreate,
    ClientUpdate,
    ClientProfileUpdate,
    ClientTagsUpdate,
    ClientResponse,
    ClientListResponse
)
from services.executors.workspace.client_executor import ClientExecutor
from services.workflow.workflow_tracker import WorkflowTracker


class ClientWorkflowError(Exception):
    """Custom exception for workflow-specific errors"""
    pass


class ClientWorkflow:
    """
    Orchestrates client-related workflows, handling operation validation,
    execution tracking, and coordination between services.
    """

    def __init__(
            self,
            session: Session = Depends(get_session),
            tracker: Optional[WorkflowTracker] = None
    ):
        self.session = session
        self.executor = ClientExecutor(session)
        self.tracker = tracker or WorkflowTracker()

    async def _handle_workflow_error(
            self,
            workflow_id: Optional[str],
            error: Exception,
            operation: ClientOperation
    ) -> None:
        """Handles workflow errors consistently"""
        if workflow_id:
            await self.tracker.fail_workflow(
                workflow_id,
                error_message=str(error),
                metadata={"operation": operation.value}
            )

        if isinstance(error, HTTPException):
            raise error
        else:
            raise HTTPException(status_code=500, detail="Internal workflow error")

    async def create_client(
            self, data: ClientCreate, user_id: UUID, user_permissions: List[str]
    ) -> ClientResponse:
        """Workflow for client creation."""
        if not validate_operation_constraints(ClientOperation.CREATE_CLIENT, user_permissions):
            raise HTTPException(status_code=403, detail="Insufficient permissions")

        workflow_id = None
        try:
            workflow_id = await self.tracker.start_workflow(
                operation=ClientOperation.CREATE_CLIENT,
                user_id=user_id,
                metadata={"client_name": data.name}
            )

            client = await self.executor.create_client(data, user_id)

            await self.tracker.complete_workflow(
                workflow_id,
                metadata={"client_id": str(client.client_id)}
            )

            return ClientResponse(**client.dict())

        except Exception as e:
            await self._handle_workflow_error(workflow_id, e, ClientOperation.CREATE_CLIENT)

    async def update_client(
            self,
            client_id: UUID,
            data: ClientUpdate,
            user_id: UUID,
            user_permissions: List[str]
    ) -> ClientResponse:
        """Workflow for client updates."""
        if not validate_operation_constraints(ClientOperation.UPDATE_CLIENT, user_permissions):
            raise HTTPException(status_code=403, detail="Insufficient permissions")

        # Check additional permissions based on update type
        if any([data.tax_id, data.registration_number]) and not check_sensitive_data_access(user_permissions):
            raise HTTPException(status_code=403, detail="Insufficient permissions for sensitive data")

        workflow_id = None
        try:
            workflow_id = await self.tracker.start_workflow(
                operation=ClientOperation.UPDATE_CLIENT,
                user_id=user_id,
                metadata={"client_id": str(client_id)}
            )

            client = await self.executor.update_client(client_id, data, user_id)

            await self.tracker.complete_workflow(workflow_id)

            return ClientResponse(**client.dict())

        except Exception as e:
            await self._handle_workflow_error(workflow_id, e, ClientOperation.UPDATE_CLIENT)

    async def update_profile(
            self,
            client_id: UUID,
            data: ClientProfileUpdate,
            user_id: UUID,
            user_permissions: List[str]
    ) -> ClientResponse:
        """Workflow for updating client profile."""
        if not validate_operation_constraints(ClientOperation.UPDATE_PROFILE, user_permissions):
            raise HTTPException(status_code=403, detail="Insufficient permissions")

        workflow_id = None
        try:
            workflow_id = await self.tracker.start_workflow(
                operation=ClientOperation.UPDATE_PROFILE,
                user_id=user_id,
                metadata={"client_id": str(client_id)}
            )

            client = await self.executor.update_profile(client_id, data, user_id)

            await self.tracker.complete_workflow(workflow_id)

            return ClientResponse(**client.dict())

        except Exception as e:
            await self._handle_workflow_error(workflow_id, e, ClientOperation.UPDATE_PROFILE)

    async def update_tags(
            self,
            client_id: UUID,
            data: ClientTagsUpdate,
            user_id: UUID,
            user_permissions: List[str]
    ) -> ClientResponse:
        """Workflow for updating client tags."""
        if not validate_operation_constraints(ClientOperation.MANAGE_TAGS, user_permissions):
            raise HTTPException(status_code=403, detail="Insufficient permissions")

        workflow_id = None
        try:
            workflow_id = await self.tracker.start_workflow(
                operation=ClientOperation.MANAGE_TAGS,
                user_id=user_id,
                metadata={"client_id": str(client_id)}
            )

            client = await self.executor.update_tags(client_id, data, user_id)

            await self.tracker.complete_workflow(workflow_id)

            return ClientResponse(**client.dict())

        except Exception as e:
            await self._handle_workflow_error(workflow_id, e, ClientOperation.MANAGE_TAGS)

    async def deactivate_client(
            self,
            client_id: UUID,
            user_id: UUID,
            user_permissions: List[str]
    ) -> ClientResponse:
        """Workflow for deactivating a client."""
        if not validate_operation_constraints(ClientOperation.DEACTIVATE_CLIENT, user_permissions):
            raise HTTPException(status_code=403, detail="Insufficient permissions")

        workflow_id = None
        try:
            workflow_id = await self.tracker.start_workflow(
                operation=ClientOperation.DEACTIVATE_CLIENT,
                user_id=user_id,
                metadata={"client_id": str(client_id)}
            )

            client = await self.executor.deactivate_client(client_id, user_id)

            await self.tracker.complete_workflow(workflow_id)

            return ClientResponse(**client.dict())

        except Exception as e:
            await self._handle_workflow_error(workflow_id, e, ClientOperation.DEACTIVATE_CLIENT)

    async def reactivate_client(
            self,
            client_id: UUID,
            user_id: UUID,
            user_permissions: List[str]
    ) -> ClientResponse:
        """Workflow for reactivating a client."""
        if not validate_operation_constraints(ClientOperation.REACTIVATE_CLIENT, user_permissions):
            raise HTTPException(status_code=403, detail="Insufficient permissions")

        workflow_id = None
        try:
            workflow_id = await self.tracker.start_workflow(
                operation=ClientOperation.REACTIVATE_CLIENT,
                user_id=user_id,
                metadata={"client_id": str(client_id)}
            )

            client = await self.executor.reactivate_client(client_id, user_id)

            await self.tracker.complete_workflow(workflow_id)

            return ClientResponse(**client.dict())

        except Exception as e:
            await self._handle_workflow_error(workflow_id, e, ClientOperation.REACTIVATE_CLIENT)

    async def delete_client(
            self,
            client_id: UUID,
            user_id: UUID,
            user_permissions: List[str]
    ) -> None:
        """Workflow for deleting a client."""
        if not validate_operation_constraints(ClientOperation.DELETE_CLIENT, user_permissions):
            raise HTTPException(status_code=403, detail="Insufficient permissions")

        workflow_id = None
        try:
            workflow_id = await self.tracker.start_workflow(
                operation=ClientOperation.DELETE_CLIENT,
                user_id=user_id,
                metadata={"client_id": str(client_id)}
            )

            await self.executor.delete_client(client_id)
            await self.tracker.complete_workflow(workflow_id)

        except Exception as e:
            await self._handle_workflow_error(workflow_id, e, ClientOperation.DELETE_CLIENT)

    async def get_client(
            self,
            client_id: UUID,
            user_id: UUID,
            user_permissions: List[str]
    ) -> ClientResponse:
        """Retrieves client details."""
        if not validate_operation_constraints(ClientOperation.GET_CLIENT, user_permissions):
            raise HTTPException(status_code=403, detail="Insufficient permissions")

        try:
            client = await self.executor.get_client(client_id)
            return ClientResponse(**client.dict())

        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error retrieving client: {str(e)}"
            )

    async def list_clients(
            self,
            user_id: UUID,
            user_permissions: List[str],
            status: Optional[ClientStatus] = None,
            legal_entity_type: Optional[LegalEntityType] = None,
            tags: Optional[List[str]] = None
    ) -> List[ClientListResponse]:
        """Lists clients with optional filters."""
        if not validate_operation_constraints(ClientOperation.LIST_CLIENTS, user_permissions):
            raise HTTPException(status_code=403, detail="Insufficient permissions")

        try:
            clients = await self.executor.list_clients(
                status=status,
                legal_entity_type=legal_entity_type,
                tags=tags
            )
            return [ClientListResponse(**client.dict()) for client in clients]

        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error listing clients: {str(e)}"
            )

    async def search_clients(
            self,
            search_term: str,
            user_id: UUID,
            user_permissions: List[str],
            limit: int = 10
    ) -> List[ClientListResponse]:
        """Searches for clients."""
        if not validate_operation_constraints(ClientOperation.LIST_CLIENTS, user_permissions):
            raise HTTPException(status_code=403, detail="Insufficient permissions")

        try:
            clients = await self.executor.search_clients(
                search_term=search_term,
                limit=limit
            )
            return [ClientListResponse(**client.dict()) for client in clients]

        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error searching clients: {str(e)}"
            )