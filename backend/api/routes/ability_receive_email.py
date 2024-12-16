#backend/api/routes/ability_receive_email.py
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session

from core.database import get_session
from services.workflow.ability_receive_email import ReceiveEmailWorkflow, WorkflowContext
from services.executors.ability_receive_email import ReceiveEmailExecutor

# TODO: Implement get_current_user or similar authentication
def get_current_user():
    # Placeholder for authentication logic
    return 1

router = APIRouter(prefix="/api/v1/inbound-email", tags=["inbound_email"])

@router.post("/receive", response_model=dict)
async def receive_inbound_email(
    email_data: dict,
    session: Session = Depends(get_session),
    current_user_id: int = Depends(get_current_user)
):
    executor = ReceiveEmailExecutor(session)
    workflow = ReceiveEmailWorkflow(executor)
    context = WorkflowContext(
        operation_name="RECEIVE_INBOUND_EMAIL",
        input_data=email_data,
        user_id=current_user_id
    )
    result = await workflow.execute_workflow(context)
    if result["status"] == "error":
        raise HTTPException(status_code=400, detail=result["error"])
    return result["data"]

@router.post("/route", response_model=dict)
async def route_email_to_main_ability(
    route_data: dict,
    session: Session = Depends(get_session),
    current_user_id: int = Depends(get_current_user)
):
    executor = ReceiveEmailExecutor(session)
    workflow = ReceiveEmailWorkflow(executor)
    context = WorkflowContext(
        operation_name="ROUTE_EMAIL_TO_MAIN_ABILITY",
        input_data=route_data,
        user_id=current_user_id
    )
    result = await workflow.execute_workflow(context)
    if result["status"] == "error":
        raise HTTPException(status_code=400, detail=result["error"])
    return result["data"]
