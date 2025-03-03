# api/routes/__init__.py

from fastapi import APIRouter
from .research import router as research_router

router = APIRouter()

router.include_router(research_router)