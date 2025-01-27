# api/routes/__init__.py
from fastapi import APIRouter
from . import behaviour, profile_pictures
from .abilities import ability_receive_email, taskmanagement
from .workspace import router as workspace_router
from .longterm_memory import router as memory_router

router = APIRouter()

router.include_router(workspace_router)
router.include_router(memory_router)
router.include_router(behaviour.router)
router.include_router(ability_receive_email.router)
router.include_router(taskmanagement.router)
router.include_router(profile_pictures.router)