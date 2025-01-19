# models/schemas/workspace/client.py

from datetime import datetime
from typing import Optional, Dict, List
from uuid import UUID
from pydantic import BaseModel, Field, validator, EmailStr, constr, AnyHttpUrl
from models.database.workspace.client import ClientStatus, LegalEntityType

# Type definitions for validation
NameType = constr(min_length=1, max_length=255)
PhoneType = constr(min_length=5, max_length=50)
AddressType = Dict[str, str]
TagType = constr(min_length=1, max_length=50)


class AddressSchema(BaseModel):
    """Schema for validating address structure"""
    street: str = Field(..., max_length=255)
    city: str = Field(..., max_length=100)
    state: str = Field(..., max_length=100)
    postal_code: str = Field(..., max_length=20)
    country: str = Field(..., max_length=100)


class ClientPreferencesSchema(BaseModel):
    """Schema for client preferences"""
    communication_preference: str = Field(
        default="email",
        description="Preferred communication method"
    )
    billing_currency: str = Field(
        default="USD",
        description="Preferred billing currency"
    )
    language: str = Field(
        default="en",
        description="Preferred language"
    )
    timezone: str = Field(
        default="UTC",
        description="Preferred timezone"
    )


class ClientCreate(BaseModel):
    """Schema for creating a new client"""
    name: NameType = Field(
        ...,
        description="Client name",
        example="Acme Corporation"
    )
    legal_entity_type: LegalEntityType = Field(
        ...,
        description="Type of legal entity"
    )
    domicile: str = Field(
        ...,
        max_length=255,
        description="Client's legal jurisdiction"
    )
    primary_email: EmailStr = Field(
        ...,
        description="Primary contact email"
    )
    primary_phone: PhoneType = Field(
        ...,
        description="Primary contact phone"
    )
    address: AddressSchema = Field(
        ...,
        description="Structured address information"
    )
    industry: str = Field(
        ...,
        max_length=255,
        description="Client's primary industry"
    )
    client_join_date: datetime = Field(
        default_factory=datetime.utcnow,
        description="When client relationship began"
    )
    tax_id: Optional[str] = Field(
        None,
        max_length=50,
        description="Tax identification number"
    )
    registration_number: Optional[str] = Field(
        None,
        max_length=50,
        description="Business registration number"
    )
    website: Optional[AnyHttpUrl] = Field(
        None,
        description="Client's website URL"
    )
    preferences: Optional[ClientPreferencesSchema] = None
    tags: Optional[List[TagType]] = Field(
        default_factory=list,
        description="Client categorization tags"
    )

    @validator('name')
    def validate_name(cls, v):
        if not v.strip():
            raise ValueError('Client name cannot be empty or whitespace')
        return v.strip()

    @validator('primary_phone')
    def validate_phone(cls, v):
        # Basic phone validation - can be enhanced based on requirements
        if not v.strip():
            raise ValueError('Phone number cannot be empty')
        return v.strip()

    @validator('tags')
    def validate_tags(cls, v):
        if v is None:
            return []
        return [tag.strip().lower() for tag in v if tag.strip()]


class ClientUpdate(BaseModel):
    """Schema for updating an existing client"""
    name: Optional[NameType] = None
    legal_entity_type: Optional[LegalEntityType] = None
    status: Optional[ClientStatus] = None
    domicile: Optional[str] = None
    primary_email: Optional[EmailStr] = None
    primary_phone: Optional[PhoneType] = None
    address: Optional[AddressSchema] = None
    industry: Optional[str] = None
    tax_id: Optional[str] = None
    registration_number: Optional[str] = None
    website: Optional[AnyHttpUrl] = None
    preferences: Optional[ClientPreferencesSchema] = None

    @validator('name')
    def validate_name(cls, v):
        if v is not None:
            if not v.strip():
                raise ValueError('Client name cannot be empty or whitespace')
            return v.strip()
        return v

    @validator('primary_phone')
    def validate_phone(cls, v):
        if v is not None:
            if not v.strip():
                raise ValueError('Phone number cannot be empty')
            return v.strip()
        return v


class ClientProfileUpdate(BaseModel):
    """Schema for updating client profile"""
    summary: str = Field(
        ...,
        min_length=1,
        max_length=5000,
        description="Client profile summary"
    )


class ClientTagsUpdate(BaseModel):
    """Schema for updating client tags"""
    tags: List[TagType] = Field(
        ...,
        description="Updated list of tags"
    )

    @validator('tags')
    def validate_tags(cls, v):
        return [tag.strip().lower() for tag in v if tag.strip()]


class ClientResponse(BaseModel):
    """Schema for client API responses"""
    client_id: UUID
    name: str
    legal_entity_type: LegalEntityType
    status: ClientStatus
    domicile: str
    primary_email: EmailStr
    primary_phone: str
    address: AddressSchema
    client_join_date: datetime
    industry: str
    tax_id: Optional[str]
    registration_number: Optional[str]
    website: Optional[AnyHttpUrl]
    client_profile: Dict
    preferences: Dict
    tags: List[str]
    created_at: datetime
    updated_at: datetime
    created_by: UUID
    modified_by: UUID

    class Config:
        orm_mode = True
        schema_extra = {
            "example": {
                "client_id": "123e4567-e89b-12d3-a456-426614174000",
                "name": "Acme Corporation",
                "legal_entity_type": "corporation",
                "status": "active",
                "domicile": "Delaware, USA",
                "primary_email": "contact@acme.com",
                "primary_phone": "+1-555-0123",
                "address": {
                    "street": "123 Business Ave",
                    "city": "Metropolis",
                    "state": "DE",
                    "postal_code": "19801",
                    "country": "USA"
                },
                "client_join_date": "2024-01-15T12:00:00Z",
                "industry": "Technology",
                "website": "https://www.acme.com",
                "tags": ["tech", "enterprise"]
            }
        }


class ClientListResponse(BaseModel):
    """Schema for client list responses"""
    client_id: UUID
    name: str
    legal_entity_type: LegalEntityType
    status: ClientStatus
    industry: str
    client_join_date: datetime
    domicile: str
    tags: List[str]

    class Config:
        orm_mode = True
        schema_extra = {
            "example": {
                "client_id": "123e4567-e89b-12d3-a456-426614174000",
                "name": "Acme Corporation",
                "legal_entity_type": "corporation",
                "status": "active",
                "industry": "Technology",
                "client_join_date": "2024-01-15T12:00:00Z",
                "domicile": "Delaware, USA",
                "tags": ["tech", "enterprise"]
            }
        }