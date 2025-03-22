# services/executors/auth_webhooks.py

import logging
import asyncio
from typing import Dict, Any
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
import re

logger = logging.getLogger(__name__)

class MaxRetriesExceededError(Exception):
    """Raised when maximum retry attempts are exceeded."""
    pass

async def process_auth_webhook(payload: Dict[Any, Any], session: AsyncSession) -> bool:
    """
    Process webhook notifications from Supabase Auth.
    Updates public.users email when a user's email is changed in Supabase Auth.
    
    Args:
        payload: The webhook payload from Supabase Auth
        session: SQLAlchemy async session
        
    Returns:
        bool: True if processing was successful, False otherwise
    """
    try:
        event = payload.get('type')
        if event != 'user.updated':
            logger.info(f"Ignoring non-user-update event: {event}")
            return True
            
        user_data = payload.get('record', {})
        auth_user_id_str = user_data.get('id')
        new_email = user_data.get('email')
        
        if not auth_user_id_str or not new_email:
            logger.error(f"Missing required fields in webhook payload: {payload}")
            return False
            
        if not re.match(r"[^@]+@[^@]+\.[^@]+", new_email):
            logger.error(f"Invalid email format in webhook payload: {new_email}")
            return False
            
        try:
            auth_user_id = UUID(auth_user_id_str)
        except ValueError as e:
            logger.error(f"Invalid UUID format for auth_user_id: {auth_user_id_str}. Error: {str(e)}")
            return False
            
        logger.info(f"Processing email update for auth_user_id: {auth_user_id}, new email: {new_email}")
        
        return await update_user_email_with_retry(auth_user_id, new_email, session)
    except Exception as e:
        logger.error(f"Error processing auth webhook: {str(e)}", exc_info=True)
        return False

async def update_user_email_with_retry(auth_user_id: UUID, email: str, session: AsyncSession, 
                                      max_retries: int = 3, retry_delay: int = 2) -> bool:
    """
    Update user email in public.users table with retry logic.
    
    Args:
        auth_user_id: Supabase Auth user ID (UUID)
        email: New email address
        session: SQLAlchemy async session
        max_retries: Maximum number of retry attempts
        retry_delay: Delay between retries in seconds
        
    Returns:
        bool: True if update was successful, False otherwise
        
    Raises:
        MaxRetriesExceededError: If maximum retry attempts are exceeded
    """
    retries = 0
    
    while retries < max_retries:
        try:
            query = text("""
                SELECT id, email FROM public.users 
                WHERE auth_user_id = :auth_user_id
            """)
            result = await session.execute(query, {"auth_user_id": auth_user_id})
            user_data = result.fetchone()
            
            if not user_data:
                logger.warning(f"No public.users record found for auth_user_id {auth_user_id} with email {email}")
                return False
                
            user_id, current_email = user_data
            
            if current_email == email:
                logger.info(f"Email already up to date for user {user_id}: {email}")
                return True
                
            update_query = text("""
                UPDATE public.users
                SET email = :email, updated_at = NOW()
                WHERE id = :user_id
                RETURNING id
            """)
            result = await session.execute(update_query, {"email": email, "user_id": user_id})
            updated = result.fetchone()
            
            if not updated:
                logger.error(f"Failed to update email for user {user_id} to {email}")
                await session.rollback()
                return False
                
            await session.commit()
            logger.info(f"Successfully updated email for user {user_id} from {current_email} to {email}")
            return True
            
        except SQLAlchemyError as e:
            await session.rollback()
            retries += 1
            if retries >= max_retries:
                logger.error(f"Max retries exceeded updating email for auth_user_id {auth_user_id}: {str(e)}")
                raise MaxRetriesExceededError(f"Failed to update email after {max_retries} attempts")
            logger.warning(f"Retry {retries}/{max_retries} for auth_user_id {auth_user_id}: {str(e)}")
            await asyncio.sleep(retry_delay)