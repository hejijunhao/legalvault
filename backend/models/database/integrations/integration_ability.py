# models/database/integrations/integration_ability.py

from uuid import UUID
from sqlmodel import Field, SQLModel, Relationship
from .integration import Integration
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .integration import Integration
    from models.database.abilities.ability import Ability

class IntegrationAbility(SQLModel, table=True):
    __tablename__ = "integration_abilities"

    integration_id: UUID = Field(
        foreign_key="integrations.integration_id",
        primary_key=True
    )
    ability_id: int = Field(
        foreign_key="abilities.id",
        primary_key=True
    )
    is_required: bool = Field(default=False)
    priority: int = Field(default=0)
    
    integration: Integration = Relationship(back_populates="abilities")
    ability: "Ability" = Relationship(back_populates="integrations")
