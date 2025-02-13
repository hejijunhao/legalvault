# tests/models/test_client.py

import pytest
from datetime import datetime
from models.database.workspace.client import (
    ClientBlueprint,
    Client,
    LegalEntityType,
    ClientStatus
)

def test_client_blueprint_basic():
    """Test basic ClientBlueprint instantiation"""
    client = ClientBlueprint(
        name="Test Corp",
        legal_entity_type=LegalEntityType.CORPORATION,
        status=ClientStatus.ACTIVE
    )
    
    assert client.name == "Test Corp"
    assert client.legal_entity_type == LegalEntityType.CORPORATION
    assert client.status == ClientStatus.ACTIVE
    assert isinstance(client.created_at, datetime)