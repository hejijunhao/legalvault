# models/database/workspace/blueprint/client_blueprint.py

from abc import ABC, abstractmethod
from datetime import datetime
from enum import Enum
from typing import Optional, Dict, List
from sqlalchemy import text, String, ARRAY, UniqueConstraint, DateTime
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlmodel import Field, SQLModel, Index, Column, ForeignKey, Relationship

# Base Class Import
from models.database.workspace.abstract.client_base import ClientBase

# Relationship Import
from .project_client import ProjectClientBase
from .contact_client import ContactClientBase


class ClientBlueprint(ClientBase, table=True):
    """Blueprint class in public schema"""
    __tablename__ = "clients"

    __table_args__ = (
        UniqueConstraint("name", "legal_entity_type", name="uq_client_name_type"),
        Index("idx_client_name", "name"),
        Index("idx_client_status", "status"),
        Index("idx_client_entity_type", "legal_entity_type"),
        Index("idx_client_join_date", "client_join_date"),
        Index("idx_client_created", "created_by"),
        Index("idx_client_modified", "modified_by", "updated_at"),
        {'schema': 'public'}
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







