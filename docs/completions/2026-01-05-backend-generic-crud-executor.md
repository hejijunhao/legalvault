# Backend Generic CRUD Executor - P2 Completion

**Date:** 2026-01-05
**Status:** Completed
**Priority:** P2

## Summary

Created a generic `BaseExecutor` class that encapsulates common CRUD operations with proper transaction handling. This provides a foundation for reducing boilerplate in entity-specific executors.

## Before

Each executor duplicated the same patterns:

```python
# Repeated in every executor (client, task, project, notebook, reminder, etc.)
class TaskExecutor:
    def __init__(self, session: Session):
        self.session = session

    async def create_task(self, data, user_id):
        try:
            task = Task(**data)
            self.session.add(task)
            await self.session.commit()
            await self.session.refresh(task)
            return TaskDomain(**task.dict())
        except Exception as e:
            await self.session.rollback()
            raise HTTPException(status_code=400, detail=str(e))

    async def get_task(self, task_id):
        task = await self.session.get(Task, task_id)
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")
        return TaskDomain(**task.dict())

    # ... same pattern repeated for update, delete, list
```

**Lines per executor:** ~150-300 lines
**Duplicated code:** ~60% boilerplate

## After

```python
from services.executors.base_executor import BaseExecutor

class TaskExecutor(BaseExecutor[Task, TaskDomain]):
    def __init__(self, session: Session):
        super().__init__(session, Task, "task_id", TaskDomain)

    async def complete_task(self, task_id: UUID, user_id: UUID) -> TaskDomain:
        """Only custom operations need implementation."""
        task = await self.get_or_404(task_id)
        task.status = TaskStatus.COMPLETED
        task.completed_at = datetime.utcnow()
        await self._commit_and_refresh(task)
        return self._to_domain(task)
```

**Lines per executor:** ~50-100 lines (for custom operations only)
**Potential reduction:** 60-75% boilerplate eliminated

## Created File

**`services/executors/base_executor.py`** (310 lines)

### Features

#### Core CRUD Operations
- `create(data, user_id, **extra)` - Create with automatic audit fields
- `get(entity_id)` - Get by ID (returns None if not found)
- `get_or_404(entity_id)` - Get by ID or raise 404
- `update(entity_id, data, user_id)` - Update with audit tracking
- `delete(entity_id)` - Delete with rollback on failure
- `list(filters, order_by, limit, offset)` - List with filtering and pagination
- `count(filters)` - Count with optional filtering

#### Helper Methods for Subclasses
- `_commit_and_refresh(entity)` - Commit transaction and refresh entity
- `_rollback()` - Rollback current transaction
- `_to_domain(entity)` - Convert to domain model
- `_to_domain_list(entities)` - Convert list to domain models
- `_execute_in_transaction(operation)` - Execute with auto transaction handling

#### Type Safety
- Generic types: `BaseExecutor[ModelT, DomainT]`
- Full type hints for all methods
- `SimpleCRUDExecutor` alias for entities without domain models

## Usage Examples

### With Domain Model

```python
from services.executors.base_executor import BaseExecutor
from models.database.workspace.client import Client
from models.domain.workspace.client import ClientDomain

class ClientExecutor(BaseExecutor[Client, ClientDomain]):
    def __init__(self, session: Session):
        super().__init__(
            session=session,
            model_class=Client,
            id_field="client_id",
            domain_class=ClientDomain
        )

    async def create_client(self, data: ClientCreate, user_id: UUID) -> ClientDomain:
        entity = await self.create(data.dict(), user_id)
        return self._to_domain(entity)

    async def deactivate_client(self, client_id: UUID, user_id: UUID) -> ClientDomain:
        # Custom operation
        client = await self.get_or_404(client_id)
        client.status = ClientStatus.INACTIVE
        await self._commit_and_refresh(client)
        return self._to_domain(client)
```

### Without Domain Model

```python
from services.executors.base_executor import SimpleCRUDExecutor
from models.database.library.collection import Collection

class CollectionExecutor(SimpleCRUDExecutor[Collection]):
    def __init__(self, session: Session):
        super().__init__(session, Collection, "collection_id")

    # Only custom operations need to be implemented
    # create, get, update, delete, list are available from base class
```

### With Filters and Pagination

```python
executor = TaskExecutor(session)

# List with filters
tasks = await executor.list(
    filters={"project_id": project_id, "status": TaskStatus.TODO},
    order_by=[Task.due_date.asc()],
    limit=20,
    offset=0
)

# Count matching entities
count = await executor.count(filters={"project_id": project_id})
```

## Verification

```bash
python3 -m py_compile services/executors/base_executor.py  # OK
```

## Impact

| Metric | Before | After | Potential Reduction |
|--------|--------|-------|---------------------|
| Lines per executor | 150-300 | 50-100 | 60-75% |
| Duplicated transaction handling | 12+ locations | 1 | 92% |
| Error handling patterns | 12+ locations | 1 | 92% |

## Migration Path

1. **Phase 1** (Optional): Import base class alongside existing executors
2. **Phase 2**: Refactor simple executors (Reminder, Notebook) to extend `BaseExecutor`
3. **Phase 3**: Refactor complex executors (Client, Task) keeping only custom methods
4. **Phase 4**: Remove duplicated code from refactored executors

### Example Migration

```python
# Before (notebook_executor.py - ~120 lines)
class NotebookExecutor:
    async def create_notebook(self, data, user_id): ...
    async def update_notebook(self, id, data, user_id): ...
    async def delete_notebook(self, id): ...
    async def get_notebook(self, id): ...
    async def _get_notebook(self, id): ...

# After (~40 lines)
class NotebookExecutor(BaseExecutor[Notebook, NotebookDomain]):
    def __init__(self, session):
        super().__init__(session, Notebook, "notebook_id", NotebookDomain)

    async def archive_notebook(self, id, user_id):
        # Only custom operations needed
        notebook = await self.get_or_404(id)
        notebook.is_archived = True
        await self._commit_and_refresh(notebook)
        return self._to_domain(notebook)
```

## Next Steps

1. **Refactor simplest executors** (reminder, notebook) as proof of concept
2. **Add unit tests** for BaseExecutor
3. **Update documentation** with migration guide
4. **Gradually migrate** remaining executors
