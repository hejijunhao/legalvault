# tests/test_models.py
import pytest
from backend.models.database import Ability, TaskManagementAbility, ReceiveEmailAbility


def test_model_imports():
    """Test that models can be imported without circular dependency errors"""
    # If this test runs without ImportError, our circular dependency is resolved
    assert Ability
    assert TaskManagementAbility
    assert ReceiveEmailAbility


def test_model_relationships():
    """Test that relationship definitions are correct"""
    ability = Ability(
        name="test_ability",
        description="test description"
    )

    task_ability = TaskManagementAbility(
        ability_id=1,
        operation_name="TEST_OP",
        description="test operation",
        input_schema={},
        output_schema={},
        workflow_steps={},
        constraints={},
        permissions={}
    )

    email_ability = ReceiveEmailAbility(
        ability_id=1,
        operation_name="TEST_EMAIL",
        description="test email operation",
        input_schema={},
        output_schema={},
        workflow_steps={},
        constraints={},
        permissions={}
    )

    # Test relationship access (this should not raise any AttributeError)
    ability.task_management_abilities
    ability.receive_email_abilities
    task_ability.ability
    email_ability.ability