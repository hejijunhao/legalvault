# backend/main.py
from fastapi import FastAPI, Depends, HTTPException
from sqlmodel import select, Session
from typing import List
from .core.database import get_session
from .models.database.paralegal import VirtualParalegal
from backend.services.initializers.op_taskmanagement_initializer import TaskManagementInitializer
from logging import getLogger
from .api.routes import router as api_router

logger = getLogger(__name__)
app = FastAPI()

app.include_router(api_router)

@app.on_event("startup")
async def initialize_operations():
    try:
        session = next(get_session())
        initializer = TaskManagementInitializer(session)
        # TODO: Replace with proper tech tree ID retrieval
        ability_id = 1
        operation_ids = initializer.initialize_operations(ability_id)
        logger.info(f"Initialized task management operations: {operation_ids}")
    except Exception as e:
        logger.error(f"Error initializing operations: {e}")
        # Don't raise the exception - allow the app to start even if initialization fails
        # You might want to add monitoring/alerting here
    finally:
        session.close()

@app.get("/virtual-paralegals", response_model=List[VirtualParalegal])
async def list_paralegals(session: Session = Depends(get_session)):
    result = await session.execute(select(VirtualParalegal))
    return result.scalars().all()

@app.post("/virtual-paralegals", response_model=VirtualParalegal)
async def create_paralegal(
    paralegal: VirtualParalegal,
    session: Session = Depends(get_session)
):
    session.add(paralegal)
    await session.commit()
    await session.refresh(paralegal)
    return paralegal

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

# Error handling
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return {"detail": str(exc.detail), "status_code": exc.status_code}

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    logger.error(f"Unhandled exception: {str(exc)}")
    return {"detail": "Internal server error", "status_code": 500}