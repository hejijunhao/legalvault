# api/routes/workspace/__init__.py
from fastapi import APIRouter
from . import project, client, notebook, reminder, task, project_client

router = APIRouter(prefix="/workspace", tags=["workspace"])

router.include_router(project.router)
router.include_router(client.router)
router.include_router(notebook.router)
router.include_router(reminder.router)
router.include_router(task.router)
router.include_router(project_client.router)