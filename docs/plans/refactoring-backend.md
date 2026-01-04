# Backend Refactoring Proposals

## Executive Summary

The backend has ~26,870 lines across 330 files with significant over-engineering. The model layer alone contains 153 files (~12,027 lines) with redundant representations across database, domain, schema, DTO, and enum layers.

**Key Findings:**
- Each entity exists in 3-5 representations (database → domain → schema → DTO)
- 16 operation files contain nearly identical permission validation code (~800 lines duplicated)
- Workflow → Executor pattern adds overhead for simple CRUD operations
- Estimated 65% of code is boilerplate/translation logic

## 1. Model Layer Redundancy

### 1.1 Current State: Multiple Representations

For a single entity like `Client`:

```
models/
├── database/workspace/client.py (267 lines) - SQLAlchemy ORM
├── database/workspace/abstract/client_base.py - Abstract base
├── database/workspace/blueprint/client_blueprint.py - Blueprint
├── domain/workspace/client.py (331 lines) - Domain model
├── domain/workspace/operations_client.py (186 lines) - Operations + permissions
├── schemas/workspace/client.py (257 lines) - Pydantic schemas
└── (No DTO for workspace - inconsistent with research module)

Total: ~1,040 lines for one entity
Effective business logic: ~150 lines (14%)
```

### 1.2 Proposal: Unified Model Pattern

Collapse to 2 layers: **Database Model** (with embedded validation) + **API Schemas**

```python
# models/workspace/client.py (~350 lines total)
from sqlmodel import SQLModel, Field
from pydantic import BaseModel
from enum import Enum
from uuid import UUID

# Enums (kept with model)
class LegalEntityType(str, Enum):
    INDIVIDUAL = "individual"
    CORPORATION = "corporation"
    PARTNERSHIP = "partnership"
    LLC = "llc"

class ClientStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    ARCHIVED = "archived"

# Database model with business logic
class Client(SQLModel, table=True):
    __tablename__ = "clients"
    __table_args__ = {'schema': 'public'}

    client_id: UUID = Field(primary_key=True, default_factory=uuid4)
    name: str = Field(..., max_length=255)
    legal_entity_type: LegalEntityType
    status: ClientStatus = Field(default=ClientStatus.ACTIVE)
    # ... other fields

    # Business logic methods (moved from domain model)
    def can_be_modified(self) -> bool:
        return self.status == ClientStatus.ACTIVE

    def deactivate(self, modified_by: UUID) -> None:
        if not self.can_be_modified():
            raise ClientError("Already inactive")
        self.status = ClientStatus.INACTIVE
        self.modified_by = modified_by
        self.updated_at = datetime.utcnow()

# API Schemas (for request/response validation)
class ClientCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    legal_entity_type: LegalEntityType
    # ... create-specific fields

class ClientUpdate(BaseModel):
    name: Optional[str] = None
    # ... update-specific fields

class ClientResponse(BaseModel):
    client_id: UUID
    name: str
    status: ClientStatus
    # ... response fields

    class Config:
        from_attributes = True
```

**Benefits:**
- From 1,040 lines → 350 lines (66% reduction)
- Single source of truth for entity structure
- Business logic stays with data
- Eliminates conversion boilerplate

### 1.3 Implementation Steps

1. Start with simple entities (e.g., `Notebook`, `Reminder`)
2. Merge database + domain for entities with minimal business logic
3. Keep schemas for API validation (but simplify)
4. Remove empty domain models entirely

---

## 2. Permission System Consolidation

### 2.1 Current State: Scattered Operations Files

16 separate files with nearly identical code:

```python
# models/domain/workspace/operations_client.py
class ClientOperation(str, Enum):
    CREATE_CLIENT = "create_client"
    UPDATE_CLIENT = "update_client"
    DELETE_CLIENT = "delete_client"
    # ...

class ClientPermission(str, Enum):
    CREATE = "client:create"
    UPDATE = "client:update"
    # ...

OPERATION_PERMISSIONS = {
    ClientOperation.CREATE_CLIENT: [ClientPermission.CREATE],
    # ...
}

def validate_operation_constraints(operation: ClientOperation, user_permissions: List[str]) -> bool:
    required_permissions = OPERATION_PERMISSIONS[operation]
    return all(perm.value in user_permissions for perm in required_permissions)

# Same pattern repeated in:
# - operations_task.py (120 lines)
# - operations_project.py (73 lines)
# - operations_reminder.py (120 lines)
# - operations_notebook.py (140 lines)
# - ... 11 more files
```

### 2.2 Proposal: Centralized Permission System

```python
# models/permissions.py (~150 lines total)
from enum import Enum
from typing import Dict, List, Set

class Permission(str, Enum):
    """Universal permission enum"""
    # Standard CRUD
    CREATE = "create"
    READ = "read"
    UPDATE = "update"
    DELETE = "delete"
    LIST = "list"

    # Special operations
    ARCHIVE = "archive"
    REASSIGN = "reassign"
    MANAGE_STATUS = "manage_status"
    MANAGE_SENSITIVE = "manage_sensitive"
    MANAGE_MEMBERS = "manage_members"

class ResourceType(str, Enum):
    """All resource types in the system"""
    CLIENT = "client"
    PROJECT = "project"
    TASK = "task"
    REMINDER = "reminder"
    NOTEBOOK = "notebook"
    CONTACT = "contact"
    PARALEGAL = "paralegal"
    # ... etc

# Centralized permission mapping
RESOURCE_PERMISSIONS: Dict[ResourceType, Dict[str, Set[Permission]]] = {
    ResourceType.CLIENT: {
        "create": {Permission.CREATE},
        "read": {Permission.READ},
        "update": {Permission.UPDATE},
        "delete": {Permission.DELETE},
        "update_sensitive": {Permission.UPDATE, Permission.MANAGE_SENSITIVE},
        "archive": {Permission.ARCHIVE},
    },
    ResourceType.TASK: {
        "create": {Permission.CREATE},
        "read": {Permission.READ},
        "update": {Permission.UPDATE},
        "complete": {Permission.UPDATE, Permission.MANAGE_STATUS},
        "reassign": {Permission.UPDATE, Permission.REASSIGN},
        "delete": {Permission.DELETE},
    },
    # ... other resources
}

def check_permission(
    resource: ResourceType,
    operation: str,
    user_permissions: List[str]
) -> bool:
    """
    Check if user can perform operation on resource.

    Args:
        resource: The resource type (client, task, etc.)
        operation: The operation name (create, update, etc.)
        user_permissions: List of permission strings the user has

    Returns:
        True if user has all required permissions
    """
    required = RESOURCE_PERMISSIONS.get(resource, {}).get(operation, set())
    user_perm_set = set(user_permissions)

    # Check if user has all required permissions for this resource
    for perm in required:
        resource_perm = f"{resource.value}:{perm.value}"
        if resource_perm not in user_perm_set:
            return False
    return True

def get_required_permissions(resource: ResourceType, operation: str) -> List[str]:
    """Get list of required permissions for an operation."""
    required = RESOURCE_PERMISSIONS.get(resource, {}).get(operation, set())
    return [f"{resource.value}:{perm.value}" for perm in required]
```

**Usage in routes:**
```python
# api/routes/workspace/client.py
from models.permissions import check_permission, ResourceType

@router.post("/")
async def create_client(
    data: ClientCreate,
    permissions: List[str] = Depends(get_user_permissions),
    ...
):
    if not check_permission(ResourceType.CLIENT, "create", permissions):
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    # ... rest of handler
```

**Benefits:**
- From 800 lines → 150 lines (81% reduction)
- Single place to audit all permissions
- Consistent permission format
- Easy to add new resources/operations

---

## 3. Service Layer Simplification

### 3.1 Current State: Executor → Workflow → API Chain

Each operation requires 3 layers:

```
API Route (15 lines)
    ↓
Workflow (40 lines - permission check, tracking, error handling)
    ↓
Executor (35 lines - actual DB logic)
    ↓
Database Model

Total: ~90 lines per CRUD operation
```

### 3.2 Proposal: Generic CRUD Executor

```python
# services/base_executor.py (~150 lines)
from typing import TypeVar, Generic, List, Optional, Type, Dict, Any
from sqlmodel import Session, select
from fastapi import HTTPException
from uuid import UUID

T = TypeVar('T')  # Database model type

class BaseExecutor(Generic[T]):
    """Generic CRUD executor for SQLModel entities."""

    def __init__(self, session: Session, model: Type[T]):
        self.session = session
        self.model = model

    async def create(self, data: Dict[str, Any], **extra_fields) -> T:
        """Create a new entity."""
        try:
            obj = self.model(**data, **extra_fields)
            self.session.add(obj)
            await self.session.commit()
            await self.session.refresh(obj)
            return obj
        except Exception as e:
            await self.session.rollback()
            raise HTTPException(status_code=400, detail=str(e))

    async def get(self, entity_id: UUID, id_field: str = "id") -> T:
        """Get entity by ID."""
        statement = select(self.model).where(
            getattr(self.model, id_field) == entity_id
        )
        result = await self.session.execute(statement)
        obj = result.scalar_one_or_none()
        if not obj:
            raise HTTPException(status_code=404, detail=f"{self.model.__name__} not found")
        return obj

    async def update(self, entity_id: UUID, data: Dict[str, Any], id_field: str = "id") -> T:
        """Update an entity."""
        obj = await self.get(entity_id, id_field)

        for key, value in data.items():
            if value is not None:
                setattr(obj, key, value)

        await self.session.commit()
        await self.session.refresh(obj)
        return obj

    async def delete(self, entity_id: UUID, id_field: str = "id") -> None:
        """Delete an entity."""
        obj = await self.get(entity_id, id_field)
        await self.session.delete(obj)
        await self.session.commit()

    async def list(
        self,
        filters: Optional[Dict[str, Any]] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[T]:
        """List entities with optional filtering."""
        statement = select(self.model)

        if filters:
            for key, value in filters.items():
                if value is not None:
                    statement = statement.where(
                        getattr(self.model, key) == value
                    )

        statement = statement.offset(offset).limit(limit)
        result = await self.session.execute(statement)
        return list(result.scalars().all())

# Specialized executor with custom logic
class ClientExecutor(BaseExecutor[Client]):
    """Client-specific operations."""

    def __init__(self, session: Session):
        super().__init__(session, Client)

    async def archive(self, client_id: UUID, modified_by: UUID) -> Client:
        """Archive a client (custom operation)."""
        client = await self.get(client_id, "client_id")
        client.archive(modified_by)  # Uses model's business logic
        await self.session.commit()
        await self.session.refresh(client)
        return client
```

### 3.3 Simplified Route Pattern

```python
# api/routes/workspace/client.py (simplified)
from services.base_executor import ClientExecutor
from models.permissions import check_permission, ResourceType

router = APIRouter(prefix="/clients", tags=["clients"])

@router.post("/", response_model=ClientResponse)
async def create_client(
    data: ClientCreate,
    user_id: UUID = Depends(get_current_user_id),
    permissions: List[str] = Depends(get_user_permissions),
    session: AsyncSession = Depends(get_db)
):
    if not check_permission(ResourceType.CLIENT, "create", permissions):
        raise HTTPException(403, "Insufficient permissions")

    executor = ClientExecutor(session)
    client = await executor.create(data.model_dump(), created_by=user_id)
    return ClientResponse.model_validate(client)

@router.get("/{client_id}", response_model=ClientResponse)
async def get_client(
    client_id: UUID,
    permissions: List[str] = Depends(get_user_permissions),
    session: AsyncSession = Depends(get_db)
):
    if not check_permission(ResourceType.CLIENT, "read", permissions):
        raise HTTPException(403, "Insufficient permissions")

    executor = ClientExecutor(session)
    return await executor.get(client_id, "client_id")
```

**Benefits:**
- Eliminates workflow layer for simple CRUD
- 80% reduction in executor boilerplate
- Consistent patterns across all entities
- Keep workflows only for complex multi-step operations

---

## 4. Workflow Layer Assessment

### 4.1 When to Keep Workflows

Keep the workflow pattern for:
- Multi-step operations (e.g., `ResearchSearchWorkflow`)
- Operations requiring external API calls
- Operations with complex rollback requirements
- Operations that span multiple entities

### 4.2 When to Remove Workflows

Remove workflow layer when:
- Single database operation
- No external dependencies
- Permission check is the only "orchestration"

### 4.3 Proposed Workflow Consolidation

Keep only these workflows:
- `ResearchSearchWorkflow` - External API integration
- `IntegrationWorkflow` - OAuth flows
- `AbilityWorkflow` - Complex AI operations

Remove these (move logic to executors/routes):
- All workspace workflows (client, project, task, etc.)
- All longterm_memory workflows (simple CRUD)
- All library workflows (simple CRUD)

---

## 5. Enum Consolidation

### 5.1 Current State

Enums scattered across:
- Database models (18 inline enums)
- Domain operations (16 operation enums)
- Enums directory (2 files, underutilized)

### 5.2 Proposal: Centralized Enums

```python
# models/enums/__init__.py
from .workspace import (
    ClientStatus,
    LegalEntityType,
    ProjectStatus,
    TaskStatus,
    TaskPriority,
    ReminderStatus,
)
from .research import (
    QueryCategory,
    QueryStatus,
    QueryType,
)
from .permissions import (
    Permission,
    ResourceType,
)

# models/enums/workspace.py
class ClientStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    ARCHIVED = "archived"

class LegalEntityType(str, Enum):
    INDIVIDUAL = "individual"
    CORPORATION = "corporation"
    PARTNERSHIP = "partnership"
    LLC = "llc"
    TRUST = "trust"
    GOVERNMENT = "government"
    OTHER = "other"

# ... all workspace enums in one file
```

---

## 6. Summary: Line Count Comparison

| Layer | Current | Proposed | Reduction |
|-------|---------|----------|-----------|
| Database models | 3,000 | 3,000 | 0% |
| Domain models | 3,500 | 500 | 86% |
| Schemas | 2,500 | 1,500 | 40% |
| Operations/Permissions | 1,800 | 200 | 89% |
| DTOs | 200 | 0 | 100% |
| Executors | 2,000 | 500 | 75% |
| Workflows | 5,200 | 1,500 | 71% |
| Routes | 3,800 | 2,500 | 34% |
| **Total** | **~22,000** | **~9,700** | **56%** |

## 7. Migration Strategy

### Phase 1: Non-Breaking Changes
1. Create `models/permissions.py`
2. Create `services/base_executor.py`
3. Add tests for new abstractions

### Phase 2: Migrate Simple Entities
1. Start with `Reminder`, `Notebook` (simplest)
2. Collapse their domain + database models
3. Remove their workflow files
4. Update routes to use base executor

### Phase 3: Migrate Complex Entities
1. Migrate `Client`, `Project`, `Task`
2. Keep entity-specific business logic in model
3. Create specialized executors only when needed

### Phase 4: Cleanup
1. Remove empty/unused files
2. Update imports across codebase
3. Update documentation
4. Final review and testing
