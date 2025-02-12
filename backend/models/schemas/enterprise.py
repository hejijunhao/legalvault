# models/schemas/enterprise.py

from pydantic import BaseModel
from uuid import UUID

class EnterpriseCreate(BaseModel):
    name: str
    domain: str
    subscription_tier: str = "standard"

class EnterpriseResponse(BaseModel):
    id: UUID
    name: str
    domain: str
    subscription_tier: str