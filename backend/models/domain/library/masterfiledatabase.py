# models/domain/library/masterfiledatabase.py

from datetime import datetime
from typing import Dict, List, Optional, Any
from uuid import UUID
from pydantic import validator, root_validator

from models.database.library.masterfiledatabase import FileStatus, FileSource, DocumentType, MasterFileDatabase


class MasterFile:
    def __init__(self, db_model: Optional[MasterFileDatabase] = None):
        self.db_model = db_model or MasterFileDatabase()
        self._validate_state()

    def _validate_state(self) -> None:
        """Validates file state and required dates."""
        status = self.db_model.file_attributes.get("status")
        if status == FileStatus.DELETED and not self.db_model.file_attributes.get("date_deleted"):
            raise ValueError("Deleted files must have a deletion date")
        if status == FileStatus.HIDDEN and not self.db_model.file_attributes.get("date_hidden"):
            raise ValueError("Hidden files must have a hidden date")

    def _validate_external_url(self) -> None:
        """Validates external URL format based on source."""
        if self.db_model.source == FileSource.ONEDRIVE and not self.db_model.external_url.startswith(
                ('https://onedrive.live.com', 'https://1drv.ms')):
            raise ValueError("Invalid OneDrive URL format")
        if self.db_model.source == FileSource.SHAREPOINT and not self.db_model.external_url.startswith(
                'https://sharepoint'):
            raise ValueError("Invalid SharePoint URL format")

    def hide_file(self) -> None:
        if self.is_deleted:
            raise ValueError("Cannot hide deleted files")
        self.db_model.file_attributes["status"] = FileStatus.HIDDEN
        self.db_model.file_attributes["date_hidden"] = datetime.utcnow()

    def unhide_file(self) -> None:
        if not self.is_hidden:
            raise ValueError("Can only unhide hidden files")
        self.db_model.file_attributes["status"] = FileStatus.AVAILABLE
        self.db_model.file_attributes["date_hidden"] = None

    def delete_file(self) -> None:
        if self.is_deleted:
            raise ValueError("File is already deleted")
        self.db_model.file_attributes["status"] = FileStatus.DELETED
        self.db_model.file_attributes["date_deleted"] = datetime.utcnow()

    def update_metadata(self, metadata: Dict[str, Any]) -> None:
        if self.is_deleted:
            raise ValueError("Cannot update deleted files")

        if 'document_type' in metadata:
            if metadata['document_type'] not in [e.value for e in DocumentType]:
                raise ValueError(f"Invalid document type: {metadata['document_type']}")

        for key, value in metadata.items():
            if key in self.db_model.file_attributes:
                self.db_model.file_attributes[key] = value

        self.db_model.file_attributes['date_modified'] = datetime.utcnow()
        self.db_model.updated_at = datetime.utcnow()

    def update_content_details(self, details: Dict[str, Any]) -> None:
        if self.is_deleted:
            raise ValueError("Cannot update deleted files")

        required_fields = {'clause_types', 'key_concepts', 'jurisdictions'}
        if not all(isinstance(details.get(field, []), list) for field in required_fields):
            raise ValueError("Invalid content details format")

        for key, value in details.items():
            if key in self.db_model.content_details:
                self.db_model.content_details[key] = value
        self.db_model.updated_at = datetime.utcnow()

    def update_permissions(self, user_id: UUID, add: bool = True) -> None:
        if self.is_deleted:
            raise ValueError("Cannot update permissions of deleted files")
        if user_id == self.db_model.owner_id:
            raise ValueError("Cannot modify permissions for file owner")

        if add:
            if user_id in self.db_model.permissions:
                raise ValueError("User already has permission")
            self.db_model.permissions.append(user_id)
        else:
            if user_id not in self.db_model.permissions:
                raise ValueError("User does not have permission")
            self.db_model.permissions.remove(user_id)

        self.db_model.updated_at = datetime.utcnow()

    def change_owner(self, new_owner_id: UUID) -> None:
        if self.is_deleted:
            raise ValueError("Cannot change owner of deleted files")
        self.db_model.owner_id = new_owner_id
        self.db_model.updated_at = datetime.utcnow()

    def start_processing(self) -> None:
        if not self.is_available:
            raise ValueError("Can only process available files")
        self.db_model.file_attributes["status"] = FileStatus.PROCESSING

    def finish_processing(self) -> None:
        if not self.is_processing:
            raise ValueError("Can only finish processing files that are being processed")
        self.db_model.file_attributes["status"] = FileStatus.AVAILABLE

    def get_file_status(self) -> Dict[str, Any]:
        return {
            'current_status': self.db_model.file_attributes.get('status'),
            'last_modified': self.db_model.file_attributes.get('date_modified'),
            'creation_date': self.db_model.created_at.isoformat(),
            'is_deleted': self.is_deleted,
            'is_hidden': self.is_hidden,
            'has_permissions': len(self.db_model.permissions) > 0
        }

    @property
    def is_available(self) -> bool:
        return self.db_model.file_attributes["status"] == FileStatus.AVAILABLE

    @property
    def is_hidden(self) -> bool:
        return self.db_model.file_attributes["status"] == FileStatus.HIDDEN

    @property
    def is_deleted(self) -> bool:
        return self.db_model.file_attributes["status"] == FileStatus.DELETED

    @property
    def is_processing(self) -> bool:
        return self.db_model.file_attributes["status"] == FileStatus.PROCESSING

    @property
    def is_accessible_by_user(self) -> callable:
        def _check_access(user_id: UUID) -> bool:
            return user_id == self.db_model.owner_id or user_id in self.db_model.permissions

        return _check_access