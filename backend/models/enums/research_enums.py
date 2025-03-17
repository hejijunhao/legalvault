from enum import Enum

class QueryCategory(str, Enum):
    """
    Categories for classifying research queries based on clarity and relevance.
    Used primarily in workflow analysis.
    """
    CLEAR = "clear"
    UNCLEAR = "unclear"
    IRRELEVANT = "irrelevant"
    BORDERLINE = "borderline"  # For queries that might need review

class QueryType(str, Enum):
    """
    Types of legal queries that can be processed.
    Used to route queries to appropriate processing logic.
    """
    COURT_CASE = "court_case"
    LEGISLATIVE = "legislative"
    COMMERCIAL = "commercial"
    GENERAL = "general"

class QueryStatus(str, Enum):
    """
    Status of a research query in the system.
    Used in both domain logic and database persistence.
    """
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    NEEDS_CLARIFICATION = "needs_clarification"
    IRRELEVANT = "irrelevant_query"