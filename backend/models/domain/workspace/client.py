# models/domain/workspace/client.py

from abc import ABC, abstractmethod
from datetime import datetime
from typing import Optional, Dict, List, Any
from uuid import UUID

from models.database.workspace.client import ClientStatus, LegalEntityType


class ClientStateError(Exception):
    """Custom exception for invalid client state transitions"""
    pass


class ClientDomainBase(ABC):
    """
    Abstract base domain model for Client entities. Handles business logic, state management,
    and behavior for clients in the LegalVault system.
    """

    def __init__(
            self,
            client_id: UUID,
            name: str,
            legal_entity_type: LegalEntityType,
            status: ClientStatus,
            domicile: str,
            primary_email: str,
            primary_phone: str,
            address: Dict[str, str],
            client_join_date: datetime,
            industry: str,
            created_by: UUID,
            modified_by: UUID,
            tax_id: Optional[str] = None,
            registration_number: Optional[str] = None,
            website: Optional[str] = None,
            client_profile: Optional[Dict] = None,
            preferences: Optional[Dict] = None,
            tags: Optional[List[str]] = None,
            created_at: Optional[datetime] = None,
            updated_at: Optional[datetime] = None
    ):
        self.client_id = client_id
        self.name = name
        self.legal_entity_type = legal_entity_type
        self.status = status
        self.domicile = domicile
        self.primary_email = primary_email
        self.primary_phone = primary_phone
        self.address = address
        self.client_join_date = client_join_date
        self.industry = industry
        self.tax_id = tax_id
        self.registration_number = registration_number
        self.website = website
        self.client_profile = client_profile or {
            "summary": "",
            "last_updated": datetime.utcnow().isoformat()
        }
        self.preferences = preferences or {
            "communication_preference": "email",
            "billing_currency": "USD",
            "language": "en",
            "timezone": "UTC"
        }
        self.tags = tags or []
        self.created_by = created_by
        self.modified_by = modified_by
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at or datetime.utcnow()

    def _validate_active_state(self) -> None:
        """Validates if client can be modified"""
        if self.status == ClientStatus.INACTIVE:
            raise ClientStateError("Cannot modify an inactive client")

    def _update_modification_metadata(self, modified_by: UUID) -> None:
        """Updates modification metadata"""
        self.modified_by = modified_by
        self.updated_at = datetime.utcnow()

    @abstractmethod
    def validate_tenant_specific_rules(self) -> bool:
        """Validates tenant-specific business rules"""
        pass

    @abstractmethod
    def get_tenant_specific_preferences(self) -> Dict[str, Any]:
        """Retrieves tenant-specific preference configurations"""
        pass

    def update_core_details(
            self,
            modified_by: UUID,
            name: Optional[str] = None,
            legal_entity_type: Optional[LegalEntityType] = None,
            industry: Optional[str] = None
    ) -> None:
        """
        Updates core client details.

        Args:
            modified_by: User making the modification
            name: New client name
            legal_entity_type: New legal entity type
            industry: New industry

        Raises:
            ClientStateError: If client is inactive
        """
        self._validate_active_state()
        if name is not None:
            self.name = name
        if legal_entity_type is not None:
            self.legal_entity_type = legal_entity_type
        if industry is not None:
            self.industry = industry
        self._update_modification_metadata(modified_by)

    def update_contact_info(
            self,
            modified_by: UUID,
            primary_email: Optional[str] = None,
            primary_phone: Optional[str] = None,
            address: Optional[Dict[str, str]] = None,
            website: Optional[str] = None
    ) -> None:
        """
        Updates client contact information.

        Args:
            modified_by: User making the modification
            primary_email: New primary email
            primary_phone: New primary phone
            address: New address dictionary
            website: New website URL

        Raises:
            ClientStateError: If client is inactive
        """
        self._validate_active_state()
        if primary_email is not None:
            self.primary_email = primary_email
        if primary_phone is not None:
            self.primary_phone = primary_phone
        if address is not None:
            self.address = address
        if website is not None:
            self.website = website
        self._update_modification_metadata(modified_by)

    def update_business_info(
            self,
            modified_by: UUID,
            tax_id: Optional[str] = None,
            registration_number: Optional[str] = None,
            domicile: Optional[str] = None
    ) -> None:
        """
        Updates client business information.

        Args:
            modified_by: User making the modification
            tax_id: New tax ID
            registration_number: New registration number
            domicile: New domicile

        Raises:
            ClientStateError: If client is inactive
        """
        self._validate_active_state()
        if tax_id is not None:
            self.tax_id = tax_id
        if registration_number is not None:
            self.registration_number = registration_number
        if domicile is not None:
            self.domicile = domicile
        self._update_modification_metadata(modified_by)

    def update_profile(
            self,
            modified_by: UUID,
            summary: str
    ) -> None:
        """
        Updates client profile summary.

        Args:
            modified_by: User making the modification
            summary: New profile summary

        Raises:
            ClientStateError: If client is inactive
        """
        self._validate_active_state()
        self.client_profile = {
            "summary": summary,
            "last_updated": datetime.utcnow().isoformat()
        }
        self._update_modification_metadata(modified_by)

    def update_preferences(
            self,
            modified_by: UUID,
            preferences: Dict[str, Any]
    ) -> None:
        """
        Updates client preferences.

        Args:
            modified_by: User making the modification
            preferences: Dictionary of preference updates

        Raises:
            ClientStateError: If client is inactive
        """
        self._validate_active_state()
        self.preferences.update(preferences)
        self._update_modification_metadata(modified_by)

    def add_tags(
            self,
            modified_by: UUID,
            new_tags: List[str]
    ) -> None:
        """
        Adds tags to client.

        Args:
            modified_by: User making the modification
            new_tags: List of tags to add

        Raises:
            ClientStateError: If client is inactive
        """
        self._validate_active_state()
        self.tags.extend([tag for tag in new_tags if tag not in self.tags])
        self._update_modification_metadata(modified_by)

    def remove_tags(
            self,
            modified_by: UUID,
            tags_to_remove: List[str]
    ) -> None:
        """
        Removes tags from client.

        Args:
            modified_by: User making the modification
            tags_to_remove: List of tags to remove

        Raises:
            ClientStateError: If client is inactive
        """
        self._validate_active_state()
        self.tags = [tag for tag in self.tags if tag not in tags_to_remove]
        self._update_modification_metadata(modified_by)

    def deactivate(self, modified_by: UUID) -> None:
        """
        Deactivates the client.

        Args:
            modified_by: User deactivating the client

        Raises:
            ClientStateError: If client is already inactive
        """
        if self.status == ClientStatus.INACTIVE:
            raise ClientStateError("Client is already inactive")

        self.status = ClientStatus.INACTIVE
        self._update_modification_metadata(modified_by)

    def reactivate(self, modified_by: UUID) -> None:
        """
        Reactivates the client.

        Args:
            modified_by: User reactivating the client

        Raises:
            ClientStateError: If client is already active
        """
        if self.status == ClientStatus.ACTIVE:
            raise ClientStateError("Client is already active")

        self.status = ClientStatus.ACTIVE
        self._update_modification_metadata(modified_by)

    def dict(self) -> dict:
        """Converts domain model to dictionary representation"""
        return {
            'client_id': self.client_id,
            'name': self.name,
            'legal_entity_type': self.legal_entity_type,
            'status': self.status,
            'domicile': self.domicile,
            'primary_email': self.primary_email,
            'primary_phone': self.primary_phone,
            'address': self.address,
            'client_join_date': self.client_join_date,
            'industry': self.industry,
            'tax_id': self.tax_id,
            'registration_number': self.registration_number,
            'website': self.website,
            'client_profile': self.client_profile,
            'preferences': self.preferences,
            'tags': self.tags,
            'created_by': self.created_by,
            'modified_by': self.modified_by,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }

class ClientDomain(ClientDomainBase):
    """
    Concrete implementation of the ClientDomainBase.
    Tenant-specific implementations should inherit from ClientDomainBase.
    """

    def validate_tenant_specific_rules(self) -> bool:
        """Default implementation of tenant-specific validation"""
        return True

    def get_tenant_specific_preferences(self) -> Dict[str, Any]:
        """Default implementation of tenant-specific preferences"""
        return self.preferences
