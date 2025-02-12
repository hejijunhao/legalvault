# models/database/library/masterfiledatabase.py

from datetime import datetime
from typing import Dict, List, Optional, Any
from uuid import UUID, uuid4
from enum import Enum
from sqlmodel import Field, SQLModel
from sqlalchemy import Column, Index, CheckConstraint, ForeignKey
from pydantic import validator
from sqlalchemy.dialects.postgresql import UUID as SQLAlchemyUUID, JSONB
from abc import ABC


class FileStatus(str, Enum):
    AVAILABLE = "available"
    HIDDEN = "hidden"
    DELETED = "deleted"
    PROCESSING = "processing"


class FileSource(str, Enum):
    ONEDRIVE = "onedrive"
    EMAIL = "email"
    OUTLOOK = "outlook"
    SHAREPOINT = "sharepoint"
    TEAMS = "teams"
    MANUAL_UPLOAD = "manual_upload"
    GENERATED = "generated"  # For AI-generated documents
    SCANNED = "scanned"  # For physically scanned documents


class DocumentType(str, Enum):
    CONTRACT = "contract"
    MEMO = "memo"
    CORRESPONDENCE = "correspondence"
    PLEADING = "pleading"
    COURT_ORDER = "court_order"
    LEGAL_OPINION = "legal_opinion"
    RESEARCH = "research"
    MINUTES = "minutes"
    POLICY = "policy"
    TEMPLATE = "template"
    FORM = "form"
    LEGISLATION = "legislation"
    REGULATION = "regulation"
    CASE_LAW = "case_law"
    SUBMISSION = "submission"
    AFFIDAVIT = "affidavit"
    INVOICE = "invoice"
    CLAUSE_BANK = "clause_bank"
    OTHER = "other"


class MasterFileDatabaseBase(SQLModel, ABC):
    """
    Abstract base class representing a master file record in the LegalVault system.
    Serves as a template for tenant-specific master file implementations.
    Contains comprehensive file metadata, content details, and relationships.
    """
    __abstract__ = True

    __table_args__ = (
        Index("ix_masterfile_file_status", "file_attributes", postgresql_using='gin'),
        Index("ix_masterfile_document_type", "file_attributes", postgresql_using='gin'),
        Index("ix_masterfile_owner_source", "owner_id", "source"),
        Index("ix_masterfile_owner_status", "owner_id", "file_attributes"),
        CheckConstraint("file_attributes::jsonb ? 'status'", name="check_file_status"),
        CheckConstraint("file_attributes::jsonb ? 'document_type'", name="check_document_type")
    )

    model_config = {
        "arbitrary_types_allowed": True,
        "json_schema_extra": {
            "example": {
                "source": "onedrive",
                "external_url": "https://onedrive.live.com/123456789",
                "directory": "/client_files/2024/",
                "import_action": "automatic_sync",
                "file_attributes": {
                    "file_title": "Service Agreement - Client A",
                    "file_name": "service_agreement_client_a_v1.docx",
                    "document_type": "contract",
                    "status": "available"
                }
            }
        }
    }

    # Core Properties
    file_id: UUID = Field(
        default_factory=uuid4,
        primary_key=True,
        nullable=False,
        index=True,
        sa_type=SQLAlchemyUUID
    )

    source: FileSource = Field(index=True)
    external_url: str
    directory: str
    import_action: str

    file_attributes: Dict[str, Any] = Field(
        default_factory=lambda: {
            "file_title": None,
            "file_name": None,
            "authors": [],
            "date_added": None,
            "date_modified": None,
            "date_hidden": None,
            "date_deleted": None,
            "document_type": None,
            "file_type": None,
            "executive_summary": None,
            "version": None,
            "languages": [],
            "status": FileStatus.AVAILABLE,
            "tags": []
        },
        sa_column=Column(JSONB)
    )

    content_details: Dict[str, Any] = Field(
        default_factory=lambda: {
            "clause_types": [],
            "key_concepts": [],
            "jurisdictions": [],
            "governing_law": None,
            "file_structure": None
        },
        sa_column=Column(JSONB)
    )

    # Relationships with cascade behavior
    client_id: Optional[UUID] = Field(
        default=None,
        sa_column=Column(
            "client_id",
            SQLAlchemyUUID,
            ForeignKey("{schema}.clients.client_id", ondelete="SET NULL"),
            nullable=True
        )
    )

    project_id: Optional[UUID] = Field(
        default=None,
        sa_column=Column(
            "project_id",
            SQLAlchemyUUID,
            ForeignKey("{schema}.projects.project_id", ondelete="SET NULL"),
            nullable=True
        )
    )

    owner_id: UUID = Field(
        sa_column=Column(
            "owner_id",
            SQLAlchemyUUID,
            ForeignKey("vault.users.id", ondelete="CASCADE"),
            nullable=False
        )
    )

    permissions: List[UUID] = Field(
        default_factory=list,
        sa_column=Column(JSONB)
    )

    # Timestamps
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        nullable=False,
        sa_column_kwargs={"server_default": "now()"},
        description="Timestamp when the record was created"
    )
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        nullable=False,
        sa_column_kwargs={"server_default": "now()", "onupdate": "now()"},
        description="Timestamp when the record was last updated"
    )

    @validator("file_attributes")
    def validate_file_attributes(cls, v):
        """Validate file attributes structure and content."""
        if not isinstance(v.get("status"), (FileStatus, str)) or \
                v.get("status") not in [e.value for e in FileStatus]:
            raise ValueError("Invalid status in file attributes")

        if v.get("document_type") and \
                v.get("document_type") not in [e.value for e in DocumentType]:
            raise ValueError("Invalid document type in file attributes")

        if not isinstance(v.get("authors", []), list):
            raise ValueError("Authors must be a list")

        if not isinstance(v.get("languages", []), list):
            raise ValueError("Languages must be a list")

        if not isinstance(v.get("tags", []), list):
            raise ValueError("Tags must be a list")

        return v

    @validator("content_details")
    def validate_content_details(cls, v):
        """Validate content details structure and content."""
        if not isinstance(v.get("clause_types", []), list):
            raise ValueError("Clause types must be a list")

        if not isinstance(v.get("key_concepts", []), list):
            raise ValueError("Key concepts must be a list")

        if not isinstance(v.get("jurisdictions", []), list):
            raise ValueError("Jurisdictions must be a list")

        return v

    def __repr__(self) -> str:
        """String representation of the Master File"""
        return f"MasterFile(id={self.file_id}, source={self.source})"


class MasterFileDatabaseBlueprint(MasterFileDatabaseBase):
    """
    Concrete implementation of MasterFileDatabaseBase for the public schema blueprint.
    Serves as a reference for tenant-specific implementations.
    """
    __tablename__ = "master_file_database_blueprint"
    __table_args__ = (
        Index("ix_masterfile_file_status", "file_attributes", postgresql_using='gin'),
        Index("ix_masterfile_document_type", "file_attributes", postgresql_using='gin'),
        Index("ix_masterfile_owner_source", "owner_id", "source"),
        Index("ix_masterfile_owner_status", "owner_id", "file_attributes"),
        CheckConstraint("file_attributes::jsonb ? 'status'", name="check_file_status"),
        CheckConstraint("file_attributes::jsonb ? 'document_type'", name="check_document_type"),
        {'schema': 'public'}
    )


class MasterFileDatabase(MasterFileDatabaseBase):
    """
    Concrete implementation of MasterFileDatabaseBase for enterprise schemas.
    """
    __tablename__ = "master_file_database"