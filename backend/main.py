# backend/main.py
from fastapi import FastAPI, Depends, HTTPException
from sqlmodel import select, Session
from typing import List
from .core.database import get_session
from .models.database.paralegal import VirtualParalegal

app = FastAPI()

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