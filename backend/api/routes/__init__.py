# api/routes/__init__.py

from fastapi import APIRouter
from .research import router as research_router
from .auth.auth import router as auth_router

router = APIRouter()

router.include_router(research_router)
router.include_router(auth_router)