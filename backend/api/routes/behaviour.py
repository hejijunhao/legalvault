# /backend/api/routes/behaviour.py

from fastapi import APIRouter, HTTPException, Depends
from typing import List
from uuid import UUID
from models.schemas.behaviour import BehaviourRead
from services.workflow.behaviour_workflow import BehaviourWorkflow
from core.database import get_supabase_client

router = APIRouter(prefix="/behaviours", tags=["behaviours"])

@router.get("/", response_model=List[BehaviourRead])
async def list_behaviours(
    status: str = None,
    workflow: BehaviourWorkflow = Depends(BehaviourWorkflow)
):
    """
    List all behaviours with optional status filter
    """
    behaviours = await workflow.list_behaviours(status)
    return behaviours

@router.get("/{behaviour_id}", response_model=BehaviourRead)
async def get_behaviour(
    behaviour_id: UUID,
    workflow: BehaviourWorkflow = Depends(BehaviourWorkflow)
):
    """
    Get a specific behaviour by ID
    """
    behaviour = await workflow.get_behaviour(behaviour_id)
    if not behaviour:
        raise HTTPException(status_code=404, detail="Behaviour not found")
    return behaviour

@router.get("/ability/{ability_id}", response_model=List[BehaviourRead])
async def get_ability_behaviours(
    ability_id: UUID,
    workflow: BehaviourWorkflow = Depends(BehaviourWorkflow)
):
    """
    Get all behaviours associated with an ability
    """
    behaviours = await workflow.get_ability_behaviours(ability_id)
    return behaviours

@router.get("/vp/{vp_id}", response_model=List[BehaviourRead])
async def get_vp_behaviours(
    vp_id: UUID,
    workflow: BehaviourWorkflow = Depends(BehaviourWorkflow)
):
    """Get all behaviours associated with a VP"""
    behaviours = await workflow.get_vp_behaviours(vp_id)
    return behaviours