# backend/tests/test_models.py

import sys
from pathlib import Path
project_root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(project_root))

import pytest
import json
from sqlalchemy import text
from core.database import get_session
from models.database.abilities import Ability, TaskManagementAbility, ReceiveEmailAbility

def test_model_imports():
    """Test that models can be imported without circular dependency errors"""
    assert Ability
    assert TaskManagementAbility
    assert ReceiveEmailAbility

def test_database_connection():
    """Test basic database connectivity"""
    with get_session() as session:
        result = session.execute(text("SELECT 1"))
        value = result.scalar()
        assert value == 1

def test_ability_model():
    """Test Ability model creation and relationships"""
    with get_session() as session:
        try:
            # Create test ability with properly serialized JSON fields
            ability = Ability(
                name="test_ability",
                description="test description",
                structure={},  # SQLModel will handle JSON serialization
                requirements={},
                meta_info={}
            )
            
            session.add(ability)
            session.flush()
            
            # Verify relationships exist
            assert hasattr(ability, 'task_management_abilities')
            assert hasattr(ability, 'receive_email_abilities')
            
            # Explicitly rollback the transaction
            session.rollback()
            
        except Exception as e:
            session.rollback()
            raise e