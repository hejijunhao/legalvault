# tests/services/test_auth_webhooks.py

import pytest
import json
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from services.executors.auth.auth_webhooks import process_auth_webhook

@pytest.mark.asyncio
async def test_process_auth_webhook_success(test_db_session):
    """Test processing a valid auth webhook for email update."""
    test_user_id = UUID("00000000-0000-0000-0000-000000000001")
    test_email = "old_email@example.com"
    new_email = "new_email@example.com"
    
    await test_db_session.execute(
        """
        INSERT INTO vault.users (id, auth_user_id, email, created_at, updated_at)
        VALUES (:id, :auth_user_id, :email, NOW(), NOW())
        """,
        {"id": test_user_id, "auth_user_id": test_user_id, "email": test_email}
    )
    await test_db_session.commit()
    
    payload = {
        "type": "user.updated",
        "record": {
            "id": str(test_user_id),
            "email": new_email
        }
    }
    
    result = await process_auth_webhook(payload, test_db_session)
    query_result = await test_db_session.execute(
        "SELECT email FROM vault.users WHERE auth_user_id = :auth_user_id",
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

@pytest.mark.asyncio
async def test_process_auth_webhook_missing_fields(test_db_session):
    """Test processing a webhook with missing required fields."""
    # Missing email field
    payload = {
        "type": "user.updated",
        "record": {
            "id": "00000000-0000-0000-0000-000000000001"
            # email field missing
        }
    }
    result = await process_auth_webhook(payload, test_db_session)
    assert result is False
    
    # Missing id field
    payload = {
        "type": "user.updated",
        "record": {
            # id field missing
            "email": "new@example.com"
        }
    }
    result = await process_auth_webhook(payload, test_db_session)
    assert result is False

@pytest.mark.asyncio
async def test_process_auth_webhook_invalid_uuid(test_db_session):
    """Test processing a webhook with invalid UUID format."""
    payload = {
        "type": "user.updated",
        "record": {
            "id": "not-a-valid-uuid",
            "email": "new@example.com"
        }
    }
    result = await process_auth_webhook(payload, test_db_session)
    assert result is False

@pytest.mark.asyncio
async def test_process_auth_webhook_invalid_email(test_db_session):
    """Test processing a webhook with invalid email format."""
    test_user_id = UUID("00000000-0000-0000-0000-000000000001")
    
    await test_db_session.execute(
        """
        INSERT INTO vault.users (id, auth_user_id, email, created_at, updated_at)
        VALUES (:id, :auth_user_id, :email, NOW(), NOW())
        """,
        {"id": test_user_id, "auth_user_id": test_user_id, "email": "old@example.com"}
    )
    await test_db_session.commit()
    
    payload = {
        "type": "user.updated",
        "record": {
            "id": str(test_user_id),
            "email": "invalid-email"
        }
    }
    
    result = await process_auth_webhook(payload, test_db_session)
    assert result is False

@pytest.mark.asyncio
async def test_process_auth_webhook_no_user(test_db_session):
    """Test processing a webhook for a non-existent user."""
    payload = {
        "type": "user.updated",
        "record": {
            "id": "00000000-0000-0000-0000-000000000099",
            "email": "new_email@example.com"
        }
    }
    result = await process_auth_webhook(payload, test_db_session)
    assert result is False