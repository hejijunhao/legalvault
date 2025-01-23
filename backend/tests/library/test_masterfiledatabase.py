# tests/library/test_masterfiledatabase.py

import pytest
from uuid import UUID, uuid4
from datetime import datetime
from sqlmodel import Session
from models.database.library.masterfiledatabase import (
    MasterFileDatabase,
    FileStatus,
    FileSource,
    DocumentType
)
from models.domain.library.operations_masterfiledatabase import MasterFileDatabaseOperations


@pytest.fixture
def test_file_data():
    return {
        "source": FileSource.ONEDRIVE,
        "external_url": "https://onedrive.live.com/test123",
        "directory": "/test/directory/",
        "import_action": "automatic_sync",
        "metadata": {
            "file_title": "Test Document",
            "file_name": "test_doc.docx",
            "authors": ["Test Author"],
            "document_type": DocumentType.CONTRACT,
            "status": FileStatus.AVAILABLE
        },
        "content_metadata": {
            "clause_types": ["General", "Termination"],
            "jurisdictions": ["UK"],
            "governing_law": "English Law"
        },
        "owner_id": uuid4(),
        "permissions": []
    }


@pytest.mark.asyncio
async def test_create_file(session: Session):
    operations = MasterFileDatabaseOperations(session)
    file_data = test_file_data()
    file = await operations.create_file(file_data)

    assert file.source == FileSource.ONEDRIVE
    assert file.external_url == "https://onedrive.live.com/test123"
    assert file.metadata["file_title"] == "Test Document"
    assert file.metadata["status"] == FileStatus.AVAILABLE


@pytest.mark.asyncio
async def test_get_file_by_id(session: Session):
    operations = MasterFileDatabaseOperations(session)
    file_data = test_file_data()
    created_file = await operations.create_file(file_data)

    retrieved_file = await operations.get_file_by_id(created_file.file_id)
    assert retrieved_file is not None
    assert retrieved_file.file_id == created_file.file_id


@pytest.mark.asyncio
async def test_update_metadata(session: Session):
    operations = MasterFileDatabaseOperations(session)
    file_data = test_file_data()
    file = await operations.create_file(file_data)

    new_metadata = {
        "file_title": "Updated Title",
        "version": "2.0"
    }
    updated_file = await operations.update_file_metadata(file.file_id, {"metadata": new_metadata})

    assert updated_file.metadata["file_title"] == "Updated Title"
    assert updated_file.metadata["version"] == "2.0"


@pytest.mark.asyncio
async def test_file_permissions(session: Session):
    operations = MasterFileDatabaseOperations(session)
    file_data = test_file_data()
    file = await operations.create_file(file_data)

    test_user_id = uuid4()
    success = await operations.update_permissions(file.file_id, test_user_id, add=True)
    assert success is True

    updated_file = await operations.get_file_by_id(file.file_id)
    assert test_user_id in updated_file.permissions


@pytest.mark.asyncio
async def test_mark_as_deleted(session: Session):
    operations = MasterFileDatabaseOperations(session)
    file_data = test_file_data()
    file = await operations.create_file(file_data)

    success = await operations.mark_file_status(file.file_id, FileStatus.DELETED)
    assert success is True

    updated_file = await operations.get_file_by_id(file.file_id)
    assert updated_file.metadata["status"] == FileStatus.DELETED
    assert "date_deleted" in updated_file.metadata


@pytest.mark.asyncio
async def test_search_files(session: Session):
    operations = MasterFileDatabaseOperations(session)
    file_data = test_file_data()
    await operations.create_file(file_data)

    results = await operations.search_files(
        owner_id=file_data["owner_id"],
        status=FileStatus.AVAILABLE,
        document_type=DocumentType.CONTRACT
    )

    assert len(results) > 0
    assert results[0].metadata["document_type"] == DocumentType.CONTRACT