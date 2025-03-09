# tests/services/test_auth_webhooks.py

import pytest
from uuid import UUID
from sqlalchemy.sql import text
from services.executors.auth.auth_webhooks import process_auth_webhook

@pytest.mark.asyncio
async def test_process_auth_webhook_success(test_db_session):
    """Test processing a valid auth webhook for email update."""
    test_user_id = UUID("00000000-0000-0000-0000-000000000001")
    test_email = "old_email@example.com"
    new_email = "new_email@example.com"
    
    # Create test user
    await test_db_session.execute(
        text("""
        INSERT INTO vault.users (id, auth_user_id, email, created_at, updated_at)
        VALUES (:id, :auth_user_id, :email, NOW(), NOW())
        """),
        {"id": test_user_id, "auth_user_id": test_user_id, "email": test_email}
    )
    
    # Create webhook payload
    payload = {
        "type": "user.updated",
        "record": {
            "id": str(test_user_id),
            "email": new_email
        }
    }
    
    # Process webhook
    result = await process_auth_webhook(payload, test_db_session)
    
    # Verify update
    query_result = await test_db_session.execute(
        text("SELECT email FROM vault.users WHERE auth_user_id = :auth_user_id"),
        {"auth_user_id": test_user_id}
    )
    updated_email = query_result.scalar_one()
    
    assert result is True
    assert updated_email == new_email

@pytest.mark.asyncio
async def test_process_auth_webhook_invalid_event_type(test_db_session):
    """Test processing an invalid webhook event type."""
    payload = {"type": "user.created"}  # Not a user.updated event
    result = await process_auth_webhook(payload, test_db_session)
    assert result is True  # Should ignore non-user.updated events