# models/schemas/integrations/integration_ability.py

from uuid import UUID
from pydantic import BaseModel, Field


class IntegrationAbilityBase(BaseModel):
    """Base Integration-Ability mapping schema"""
    integration_id: UUID
    ability_id: UUID
    is_required: bool = Field(default=False)
    priority: int = Field(default=0)


class IntegrationAbilityCreate(IntegrationAbilityBase):
    """Schema for creating a new integration-ability mapping"""
    pass


class IntegrationAbilityUpdate(BaseModel):
    """Schema for updating an existing integration-ability mapping"""
    is_required: bool = Field(...)
    priority: int = Field(...)


class IntegrationAbilityRead(IntegrationAbilityBase):
    """Schema for reading integration-ability mapping"""
    integration_name: str
    ability_name: str

    class Config:
        from_attributes = True