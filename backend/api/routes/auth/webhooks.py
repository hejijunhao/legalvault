# api/routes/auth/webhooks.py

import os
import logging
from fastapi import APIRouter, Depends, Request, HTTPException, Header
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, Any, Optional

from core.database import get_session
from services.executors.auth.auth_webhooks import process_auth_webhook

logger = logging.getLogger(__name__)

# Get webhook secret from environment variables
WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET")
if not WEBHOOK_SECRET:
    logger.warning("WEBHOOK_SECRET environment variable not set. Webhook validation will be disabled.")

router = APIRouter()

@router.post("/auth/webhooks")
async def auth_webhook(
    request: Request,
    x_webhook_secret: Optional[str] = Header(None, alias="X-Webhook-Secret"),
    session: AsyncSession = Depends(get_session)
):
    """
    Webhook endpoint for Supabase Auth notifications.
    
    This endpoint receives notifications when user data changes in Supabase Auth,
    particularly email updates, and synchronizes those changes to vault.users.
    
    The webhook is secured with a secret token that must be provided in the
    X-Webhook-Secret header and match the WEBHOOK_SECRET environment variable.
    """
    # Validate webhook secret if configured
    if WEBHOOK_SECRET and x_webhook_secret != WEBHOOK_SECRET:
        logger.warning("Invalid webhook secret received")
        raise HTTPException(status_code=401, detail="Invalid webhook secret")
        
    # Parse request body
    try:
        payload = await request.json()
    except Exception as e:
        logger.error(f"Error parsing webhook payload: {str(e)}")
        raise HTTPException(status_code=400, detail="Invalid JSON payload")
        
    # Process the webhook
    success = await process_auth_webhook(payload, session)
    
    if not success:
        # Return 200 even on processing errors to prevent Supabase from retrying
        # We'll handle retries internally and log failures
        logger.warning(f"Webhook processing failed for payload {payload} but returning 200 to prevent retries")
        return {"status": "acknowledged", "success": False}
        
    logger.debug(f"Successfully processed webhook payload: {payload}")
    return {"status": "success", "success": True}