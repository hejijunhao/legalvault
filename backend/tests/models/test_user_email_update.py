# tests/models/test_user_email_update.py

import pytest
from uuid import UUID
from sqlalchemy.sql import text
from models.domain.user_operations import UserOperations

@pytest.mark.asyncio
async def test_update_user_email_success(test_db_session):
    """Test successful email update in vault.users"""
    user_ops = UserOperations(test_db_session)
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
    
    # Update email
    result = await user_ops.update_user_email(str(test_user_id), new_email)
    
    # Verify update
    query_result = await test_db_session.execute(
        text("SELECT email FROM vault.users WHERE auth_user_id = :auth_user_id"),
        {"auth_user_id": test_user_id}
    )
    updated_email = query_result.scalar_one()
    
    assert updated_email == new_email
    assert result is not None
    assert result.email == new_email

@pytest.mark.asyncio
async def test_update_user_email_invalid_format(test_db_session):
    """Test updating with an invalid email format."""
    user_ops = UserOperations(test_db_session)
    test_user_id = UUID("00000000-0000-0000-0000-000000000002")
    invalid_email = "invalid-email"
    
    # Create test user
    await test_db_session.execute(
        text("""
        INSERT INTO vault.users (id, auth_user_id, email, created_at, updated_at)
        VALUES (:id, :auth_user_id, :email, NOW(), NOW())
        """),
        {"id": test_user_id, "auth_user_id": test_user_id, "email": "old@example.com"}
    )
    
    # Attempt to update with invalid email
    result = await user_ops.update_user_email(str(test_user_id), invalid_email)
    assert result is None