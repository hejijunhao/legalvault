# backend/scripts/users/populate_user_emails.py

"""
Populate email field in vault.users table from Supabase Auth.

This script is a one-time migration to populate the email column in vault.users
with data from Supabase Auth. It requires the Supabase service role key to access
user data from the Auth API.

Usage:
    python populate_user_emails.py
"""

import os
import sys
import time
import logging
import asyncio
from typing import Dict, Any
from uuid import UUID

# Add the project root to the path so we can import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from dotenv import load_dotenv
import httpx

from core.database import get_async_session
from core.supabase_client import get_supabase_client

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("email_migration.log")
    ]
)
logger = logging.getLogger("email_migration")

# Load environment variables
load_dotenv()

# Get Supabase service role key (this is needed to access user data)
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

if not SUPABASE_URL or not SUPABASE_SERVICE_KEY:
    logger.error("SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY must be set in environment variables")
    sys.exit(1)


async def fetch_users_from_supabase() -> Dict[str, Any]:
    """
    Fetch all users from Supabase Auth using the service role key.
    
    Returns:
        Dictionary containing the full Supabase Auth response
    """
    url = f"{SUPABASE_URL}/auth/v1/admin/users"
    headers = {
        "apikey": SUPABASE_SERVICE_KEY,
        "Authorization": f"Bearer {SUPABASE_SERVICE_KEY}"
    }
    
    max_retries = 3
    retry_delay = 5  # seconds
    
    for attempt in range(max_retries):
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url, headers=headers)
                response.raise_for_status()
                users_data = response.json()
                logger.info(f"Successfully fetched {len(users_data.get('users', []))} users from Supabase Auth")
                return users_data
        except Exception as e:
            logger.warning(f"Attempt {attempt + 1}/{max_retries} failed: {str(e)}")
            if attempt < max_retries - 1:
                logger.info(f"Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
            else:
                logger.error(f"Failed to fetch users after {max_retries} attempts")
                raise


async def get_vault_users(session: AsyncSession) -> Dict[str, Dict[str, Any]]:
    """
    Get all users from vault.users table.
    
    Args:
        session: SQLAlchemy async session
        
    Returns:
        Dictionary mapping auth_user_id to user data
    """
    query = text("""
        SELECT id, auth_user_id, email, first_name, last_name
        FROM vault.users
    """)
    
    result = await session.execute(query)
    users = result.fetchall()
    
    user_map = {}
    for user in users:
        user_map[str(user.auth_user_id)] = {
            "id": user.id,
            "auth_user_id": user.auth_user_id,
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name
        }
    
    logger.info(f"Found {len(user_map)} users in vault.users table")
    return user_map


async def update_user_email(session: AsyncSession, user_id: UUID, email: str) -> bool:
    """
    Update the email for a user in the vault.users table.
    
    Args:
        session: SQLAlchemy async session
        user_id: UUID of the user in vault.users
        email: Email address to set
        
    Returns:
        True if successful, False otherwise
    """
    try:
        query = text("""
            UPDATE vault.users
            SET email = :email
            WHERE id = :user_id
        """)
        
        await session.execute(query, {"email": email, "user_id": user_id})
        await session.commit()
        return True
    except Exception as e:
        await session.rollback()
        logger.error(f"Error updating email for user {user_id}: {str(e)}")
        return False


async def main():
    """
    Main function to populate email field in vault.users.
    """
    try:
        # Fetch users from Supabase Auth
        supabase_response = await fetch_users_from_supabase()
        supabase_users = supabase_response.get("users", [])  # Extract the 'users' list
        
        # Debug: Log the full response and first user structure
        logger.debug(f"Full Supabase response: {supabase_response}")
        if supabase_users:
            logger.debug(f"Sample user structure: {supabase_users[0]}")
        
        # Create a dictionary of auth_user_id -> email for easy lookup
        auth_emails = {}
        for user in supabase_users:
            if "email" in user and user["email"]:
                auth_emails[user["id"]] = user["email"]
            else:
                logger.warning(f"User {user.get('id', 'unknown')} has no email in Supabase Auth")
        
        logger.info(f"Found {len(auth_emails)} users with emails in Supabase Auth")
        
        # Get users from vault.users
        async with get_async_session() as session:
            vault_users = await get_vault_users(session)
            
            # Update emails in vault.users
            updated_count = 0
            skipped_count = 0
            error_count = 0
            
            for auth_id, email in auth_emails.items():
                if auth_id in vault_users:
                    vault_user = vault_users[auth_id]
                    
                    # Skip if email is already set (idempotency)
                    if vault_user["email"] == email:
                        logger.debug(f"Skipping user {vault_user['id']} - email already set")
                        skipped_count += 1
                        continue
                    
                    # Update email
                    success = await update_user_email(session, vault_user["id"], email)
                    if success:
                        logger.info(f"Updated user {vault_user['id']} with email {email}")
                        updated_count += 1
                    else:
                        error_count += 1
                else:
                    logger.warning(f"Auth user {auth_id} not found in vault.users table")
            
            logger.info(f"Migration complete: {updated_count} updated, {skipped_count} skipped, {error_count} errors")
    
    except Exception as e:
        logger.error(f"Migration failed: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())