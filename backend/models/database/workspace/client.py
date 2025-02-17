# models/database/workspace/client.py

from abc import ABC, abstractmethod
from datetime import datetime
from enum import Enum
from typing import Optional, Dict, List
from sqlalchemy import text, String, ARRAY, UniqueConstraint, DateTime
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlmodel import Field, SQLModel, Index, Column, ForeignKey, Relationship

from .project_client import ProjectClientBase
from .contact_client import ContactClientBase

class LegalEntityType(str, Enum):
    """Legal entity types for clients"""
    INDIVIDUAL = "individual"
    SOLE_PROPRIETORSHIP = "sole_proprietorship"
    PARTNERSHIP = "partnership"
    LIMITED_PARTNERSHIP = "limited_partnership"
    CORPORATION = "corporation"
    LLC = "llc"
    LLP = "llp"
    NONPROFIT = "nonprofit"
    TRUST = "trust"
    FOUNDATION = "foundation"
    ASSOCIATION = "association"
    COOPERATIVE = "cooperative"
    JOINT_VENTURE = "joint_venture"
    STATUTORY_COMPANY = "statutory_company"
    GOVERNMENT_ENTITY = "government_entity"
    EDUCATIONAL_INSTITUTION = "educational_institution"
    RELIGIOUS_ORGANIZATION = "religious_organization"
    CHARITY = "charity"
    ESTATE = "estate"
    FOREIGN_ENTITY = "foreign_entity"
    SPECIAL_PURPOSE_VEHICLE = "special_purpose_vehicle"
    MUTUAL_FUND = "mutual_fund"
    HEDGE_FUND = "hedge_fund"
    PENSION_FUND = "pension_fund"

    @classmethod
    def values(cls):
        return [e.value for e in cls]


class ClientStatus(str, Enum):
    """Status options for clients"""
    ACTIVE = "active"
    INACTIVE = "inactive"


class ClientPreferences(SQLModel):
    """Client preferences and settings"""
    communication_preference: str = "email"
    billing_currency: str = "USD"
    language: str = "en"
    timezone: str = "UTC"


class ClientProfile(SQLModel):
    """Client profile and summary information"""
    summary: str = ""
    last_updated: datetime = Field(default_factory=datetime.utcnow)


class ClientBase(SQLModel, ABC):
    """
    Abstract base class representing a client in the LegalVault system.
    Serves as a template for tenant-specific client implementations.
    Contains core properties, contact information, and business details.
    """
    __abstract__ = True

    # Table configuration
    __table_args__ = (
        Index("idx_client_name", "name"),
        Index("idx_client_status", "status"),
        Index("idx_client_entity_type", "legal_entity_type"),
        Index("idx_client_join_date", "client_join_date"),
        Index("idx_client_created", "created_by"),
        Index("idx_client_modified", "modified_by", "updated_at")
    )

    model_config = {
        "arbitrary_types_allowed": True,
        "json_schema_extra": {
            "examples": [
                {
                    "name": "Acme Corporation",
                    "legal_entity_type": "corporation",
                    "status": "active",
                    "domicile": "Delaware, USA"
                }
            ]
        }
    }

    # Core Properties
    client_id: UUID = Field(
        sa_column=Column(
            UUID(as_uuid=True),
            primary_key=True,
            server_default=text("gen_random_uuid()"),
            nullable=False
        )
    )

    name: str = Field(
        sa_column=Column(String(255), nullable=False),
        description="Client company name"
    )

    legal_entity_type: str = Field(
        sa_column=Column(String(50), nullable=False),
        description="Type of legal entity"
    )

    status: str = Field(
        sa_column=Column(String(50), nullable=False, default=ClientStatus.ACTIVE.value),
        description="Current client status"
    )

    # Contact Information
    domicile: str = Field(
        sa_column=Column(String(255), nullable=False),
        description="Client's legal jurisdiction/location"
    )
    primary_email: str = Field(
        sa_column=Column(String(255), nullable=False),
        description="Primary contact email"
    )
    primary_phone: str = Field(
        sa_column=Column(String(50), nullable=False),
        description="Primary contact phone number"
    )
    address: Dict = Field(
        sa_column=Column(
            JSONB,
            nullable=False,
            default=dict
        ),
        description="Structured address information"
    )

    # Business Information
    client_join_date: datetime = Field(
        sa_column=Column(DateTime, nullable=False),
        description="Date when client relationship began"
    )
    industry: str = Field(
        sa_column=Column(String(255), nullable=False),
        description="Client's primary industry"
    )
    tax_id: Optional[str] = Field(
        sa_column=Column(String(50), nullable=True),
        description="Tax identification number"
    )
    registration_number: Optional[str] = Field(
        sa_column=Column(String(50), nullable=True),
        description="Business registration number"
    )
    website: Optional[str] = Field(
        sa_column=Column(String(255), nullable=True),
        description="Client's website URL"
    )

    # Rich Content
    client_profile: ClientProfile = Field(
        sa_column=Column(JSONB, nullable=False),
        default_factory=ClientProfile,
        description="Client profile and summary information"
    )

    # Preferences
    preferences: ClientPreferences = Field(
        sa_column=Column(JSONB, nullable=False),
        default_factory=ClientPreferences,
        description="Client preferences and settings"
    )

    # Tags
    tags: list[str] = Field(
        sa_column=Column(ARRAY(String), nullable=False, default=list),
        description="Client tags for categorization"
    )

    # Metadata
    created_at: datetime = Field(
        sa_column=Column(DateTime, nullable=False),
        default_factory=datetime.utcnow,
        description="Timestamp when the client was created"
    )
    updated_at: datetime = Field(
        sa_column=Column(DateTime, nullable=False),
        default_factory=datetime.utcnow,
        description="Timestamp when the client was last updated"
    )
    created_by: UUID = Field(
        sa_column=Column(
            UUID(as_uuid=True),
            ForeignKey("vault.users.id", ondelete="RESTRICT"),
            nullable=False
        ),
        description="User ID of client creator"
    )
    modified_by: UUID = Field(
        sa_column=Column(
            UUID(as_uuid=True),
            ForeignKey("vault.users.id", ondelete="RESTRICT"),
            nullable=False
        ),
        description="User ID of last modifier"
    )

    # Relationships
    project_client: Optional[List["ProjectClientBase"]] = Relationship(
        back_populates="client",
        link_model="ProjectClientBase",
        sa_relationship_kwargs={
            "lazy": "selectin",
            "cascade": "all",
            "primaryjoin": (
                "and_(foreign(ClientBase.client_id)==ProjectClientBase.client_id, "
                "ClientBase.__table__.schema==ProjectClientBase.__table__.schema)"
            ),
            "secondaryjoin": (
                "and_(ProjectClientBase.project_id==ProjectBase.project_id, "
                "ProjectClientBase.__table__.schema==ProjectBase.__table__.schema)"
            )
        }
    )

    contact_client: Optional[List["ContactClientBase"]] = Relationship(
        back_populates="client",
        link_model="ContactClientBase",
        sa_relationship_kwargs={
            "lazy": "selectin",
            "cascade": "all",
            "primaryjoin": (
                "and_(foreign(ClientBase.client_id)==ContactClientBase.client_id, "
                "ClientBase.__table__.schema==ContactClientBase.__table__.schema)"
            ),
            "secondaryjoin": (
                "and_(ContactClientBase.contact_id==ContactBase.contact_id, "
                "ContactClientBase.__table__.schema==ContactBase.__table__.schema)"
            )
        }
    )

    def __repr__(self) -> str:
        """String representation of the Client"""
        return f"{self.__class__.__name__}(id={self.client_id}, name={self.name}, status={self.status})"


class ClientBlueprint(ClientBase, table=True):
    """Blueprint class in public schema"""
    __tablename__ = "clients"
    __table_args__ = (
        *ClientBase.__table_args__,
        UniqueConstraint("name", "legal_entity_type", name="uq_client_name_type"),
        {'schema': 'public'}
    )




