# models/database/workspace/client.py

from enum import Enum
from datetime import datetime
import uuid
from sqlmodel import Field, SQLModel
from sqlalchemy import Column, String, DateTime, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import declared_attr

# 1. Define the enums
class LegalEntityType(str, Enum):
    CORPORATION = "corporation"
    LLC = "llc"
    INDIVIDUAL = "individual"

class ClientStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"

# 2. Create an abstract base class with declared_attr fields
class ClientBase(SQLModel):
    __abstract__ = True

    # Add class-level annotations
    client_id: uuid.UUID
    name: str
    legal_entity_type: LegalEntityType
    status: ClientStatus
    created_at: datetime

    @declared_attr
    def client_id(cls) -> uuid.UUID:
        return Field(
            default_factory=uuid.uuid4,
            sa_column=Column(
                UUID(as_uuid=True),
                primary_key=True,
                server_default=text("gen_random_uuid()"),
                nullable=False
            )
        )

    @declared_attr
    def name(cls) -> str:
        return Field(
            sa_column=Column(String(255), nullable=False)
        )

    @declared_attr
    def legal_entity_type(cls) -> LegalEntityType:
        return Field(
            sa_column=Column(String(50), nullable=False)
        )

    @declared_attr
    def status(cls) -> ClientStatus:
        return Field(
            default=ClientStatus.ACTIVE,
            sa_column=Column(String(50), nullable=False)
        )

    @declared_attr
    def created_at(cls) -> datetime:
        return Field(
            default_factory=datetime.utcnow,
            sa_column=Column(DateTime, nullable=False)
        )

# 3. Create the blueprint class
class ClientBlueprint(ClientBase, table=True):
    __tablename__ = "client_blueprint"
    __table_args__ = {'schema': 'public'}

# 4. Create the concrete class
class Client(ClientBase, table=True):
    __tablename__ = "clients"
