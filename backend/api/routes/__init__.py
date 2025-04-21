# api/routes/__init__.py

from fastapi import APIRouter
from .research.search import router as search_router
from .research.search_message import router as search_message_router
from .auth.auth import router as auth_router
from .user import router as user_router 

api_router = APIRouter()  # Renamed to api_router for consistency

api_router.include_router(search_router)
api_router.include_router(search_message_router)
api_router.include_router(auth_router)
api_router.include_router(user_router)  