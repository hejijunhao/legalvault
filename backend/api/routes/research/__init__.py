# api/routes/research/__init__.py

from fastapi import APIRouter
from . import search

router = APIRouter(prefix="/research", tags=["research"])

router.include_router(search.router)
router.include_router(sessions.router)
