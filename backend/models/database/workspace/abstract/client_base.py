# models/database/workspace/abstract/client_base.py

from abc import ABC
from datetime import datetime
from sqlalchemy import Enum as SQLAEnum
from typing import Optional
from sqlalchemy import text, String, DateTime
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlmodel import Field, SQLModel, Column

# Enum and Mixin imports
from models.enums.workspace_enums import LegalEntityType, ClientStatus
from models.database.mixins.timestamp_mixin import TimestampMixin
from models.database.mixins.user_tracking_mixin import UserAuditMixin


class ClientBase(SQLModel, ABC, TimestampMixin, UserAuditMixin):
    """
    Abstract base class representing a client in the LegalVault system.
    Serves as a template for tenant-specific client implementations.
    Contains core properties, contact information, and business details.
    """
    __abstract__ = True

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

    legal_entity_type: LegalEntityType = Field(
        sa_column=Column(SQLAEnum(LegalEntityType), nullable=False, default=LegalEntityType.CORPORATION),
        description="Type of legal entity"
    )

    status: ClientStatus = Field(
        sa_column=Column(SQLAEnum(ClientStatus), nullable=False, default=ClientStatus.ACTIVE),
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
    address: dict = Field(
        sa_column=Column(
            JSONB,
            nullable=False,
            default_factory=dict
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

    client_profile: dict = Field(
        sa_column=Column(JSONB(astext_type=String()), nullable=False),
        default_factory=dict,
        description="Client profile and summary information"
    )


    # Relationships defined in Concrete Classes (client_blueprint and client)


    # Functions and database operations defined in /domain layer

    def __repr__(self) -> str:
        """String representation of the ClientBase"""
        return (
            f"{self.__class__.__name__}(id={self.client_id}, "
            f"name='{self.name}', status='{self.status}')"
        )

