# models/domain/workspace/project_client.py
from datetime import datetime
from uuid import UUID
from models.schemas.project_client import ProjectClientCreate, ProjectClientUpdate

class ProjectClient:
    def __init__(
        self,
        project_id: UUID,
        client_id: UUID,
        role: str,
        created_at: datetime,
        updated_at: datetime,
        created_by: UUID | None
    ):
        self.project_id = project_id
        self.client_id = client_id
        self.role = role
        self.created_at = created_at
        self.updated_at = updated_at
        self.created_by = created_by