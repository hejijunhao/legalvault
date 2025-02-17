# tests/models/test_client.py

import pytest
from uuid import UUID
from datetime import datetime
from models.database.workspace.client import (
    ClientBlueprint,
    LegalEntityType,
    ClientStatus,
    ClientProfile,
    ClientPreferences
)


def test_client_blueprint_creation():
    """Test basic ClientBlueprint instantiation"""
    client = ClientBlueprint(
        name="Test Corp",
        legal_entity_type=LegalEntityType.CORPORATION.value,
        status=ClientStatus.ACTIVE.value,
        domicile="Test Location",
        primary_email="test@example.com",
        primary_phone="1234567890",
        address={"street": "123 Test St"},
        client_join_date=datetime.utcnow(),
        industry="Technology",
        created_by=UUID("12345678-1234-5678-1234-567812345678"),
        modified_by=UUID("12345678-1234-5678-1234-567812345678")
    )

    assert client.name == "Test Corp"
    assert client.legal_entity_type == LegalEntityType.CORPORATION
    assert client.status == ClientStatus.ACTIVE
    assert isinstance(client.client_id, UUID)
    assert isinstance(client.created_at, datetime)
    assert isinstance(client.client_profile, ClientProfile)
    assert isinstance(client.preferences, ClientPreferences)
    assert client.tags == []


def test_client_blueprint_db_operations(session):
    """Test database operations with ClientBlueprint"""
    # Create a client
    client = ClientBlueprint(
        name="Test Corp DB",
        legal_entity_type=LegalEntityType.CORPORATION,
        status=ClientStatus.ACTIVE,
        domicile="Test Location",
        primary_email="test@example.com",
        primary_phone="1234567890",
        address={"street": "123 Test St"},
        client_join_date=datetime.utcnow(),
        industry="Technology",
        created_by=UUID("12345678-1234-5678-1234-567812345678"),
        modified_by=UUID("12345678-1234-5678-1234-567812345678")
    )

    # Add to database
    session.add(client)
    session.commit()
    session.refresh(client)

    # Query and verify
    db_client = session.query(ClientBlueprint).filter(ClientBlueprint.name == "Test Corp DB").first()
    assert db_client is not None
    assert db_client.name == "Test Corp DB"
    assert db_client.legal_entity_type == LegalEntityType.CORPORATION
    assert isinstance(db_client.client_id, UUID)

    # Test JSONB fields
    assert isinstance(db_client.address, dict)
    assert db_client.address["street"] == "123 Test St"
    assert isinstance(db_client.client_profile, ClientProfile)
    assert isinstance(db_client.preferences, ClientPreferences)


def test_client_blueprint_enum_validation():
    """Test enum validation"""
    with pytest.raises(ValueError):
        ClientBlueprint(
            name="Test Corp",
            legal_entity_type="invalid_type",  # This should raise an error
            status=ClientStatus.ACTIVE,
            domicile="Test Location",
            primary_email="test@example.com",
            primary_phone="1234567890",
            address={"street": "123 Test St"},
            client_join_date=datetime.utcnow(),
            industry="Technology",
            created_by=UUID("12345678-1234-5678-1234-567812345678"),
            modified_by=UUID("12345678-1234-5678-1234-567812345678")
        )
