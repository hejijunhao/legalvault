# models/domain/enterprise.py

from uuid import UUID

class EnterpriseManager:
    def validate_domain(self, domain: str) -> bool:
        pass

    def get_user_count(self, enterprise_id: UUID) -> int:
        pass