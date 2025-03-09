# tests/models/test_user_email_update.py

import pytest
from uuid import UUID
import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from models.domain.user_operations import UserOperations

@pytest.mark.asyncio
async def test_update_user_email_success(test_db_session):
    """Test successfully updating a user's email in vault.users table."""
    user_ops = UserOperations(test_db_session)
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
    
    result = await user_ops.update_user_email(str(test_user_id), new_email)
    
    query_result = await test_db_session.execute(
        "SELECT email FROM vault.users WHERE auth_user_id = :auth_user_id",
        {"auth_user_id": test_user_id}
    )
    updated_email = query_result.scalar_one()
    
    assert updated_email == new_email
    assert result is not None
    assert result.email == new_email
    assert str(result.id) == str(test_user_id)

@pytest.mark.asyncio
async def test_update_user_email_invalid_format(test_db_session):
    """Test updating with an invalid email format."""
    user_ops = UserOperations(test_db_session)
    test_user_id = UUID("00000000-0000-0000-0000-000000000002")
    invalid_email = "invalid-email"
    
    await test_db_session.execute(
        """
        INSERT INTO vault.users (id, auth_user_id, email, created_at, updated_at)
        VALUES (:id, :auth_user_id, :email, NOW(), NOW())
        """,
        {"id": test_user_id, "auth_user_id": test_user_id, "email": "old@example.com"}
    )
    await test_db_session.commit()
    
    result = await user_ops.update_user_email(str(test_user_id), invalid_email)
    assert result is None

@pytest.mark.asyncio
async def test_update_user_email_duplicate(test_db_session):
    """Test updating with a duplicate email."""
    user_ops = UserOperations(test_db_session)
    user1_id = UUID("00000000-0000-0000-0000-000000000003")
    user2_id = UUID("00000000-0000-0000-0000-000000000004")
    
    await test_db_session.execute(
        """
        INSERT INTO vault.users (id, auth_user_id, email, created_at, updated_at)
        VALUES (:id, :auth_user_id, :email, NOW(), NOW())
        """,
        {"id": user1_id, "auth_user_id": user1_id, "email": "user1@example.com"}
    )
    await test_db_session.execute(
        """
        INSERT INTO vault.users (id, auth_user_id, email, created_at, updated_at)
        VALUES (:id, :auth_user_id, :email, NOW(), NOW())
        """,
        {"id": user2_id, "auth_user_id": user2_id, "email": "user2@example.com"}
    )
    await test_db_session.commit()
    
    result = await user_ops.update_user_email(str(user2_id), "user1@example.com")
    assert result is None

@pytest.mark.asyncio
async def test_update_user_email_nonexistent_user(test_db_session):
    """Test updating email for a non-existent user."""
    user_ops = UserOperations(test_db_session)
    nonexistent_user_id = "00000000-0000-0000-0000-000000000099"
    
    result = await user_ops.update_user_email(nonexistent_user_id, "new@example.com")
    assert result is None