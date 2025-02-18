# models/enums/workspace_enums.py

from enum import Enum

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