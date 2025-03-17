# models/domain/research/search.py

from typing import Dict, List, Optional, Any
from uuid import UUID
import logging
from datetime import datetime
from enum import Enum

logger = logging.getLogger(__name__)

# Domain enums for search categorization
class QueryCategory(str, Enum):
    CLEAR = "clear"
    UNCLEAR = "unclear"
    IRRELEVANT = "irrelevant"
    BORDERLINE = "borderline"  # For queries that might need review

class QueryType(str, Enum):
    COURT_CASE = "court_case"
    LEGISLATIVE = "legislative"
    COMMERCIAL = "commercial"
    GENERAL = "general"

class QueryStatus(str, Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    NEEDS_CLARIFICATION = "needs_clarification"
    IRRELEVANT = "irrelevant_query"

class ResearchSearch:
    """
    Domain model for legal research searches.
    Focuses on core domain logic and validation without external API or persistence concerns.
    """
    
    def __init__(self, title: str, description: Optional[str] = None, user_id: Optional[UUID] = None, 
                 enterprise_id: Optional[UUID] = None):
        """
        Initialize with search data and context.
        
        Args:
            title: Title of the search (initially the query text)
            description: Optional description of the search
            user_id: UUID of the user initiating the search
            enterprise_id: Optional UUID of the user's enterprise
        """
        self.title = title
        self.description = description
        self.user_id = user_id
        self.enterprise_id = enterprise_id
        self.created_at = datetime.utcnow()
        self.status = QueryStatus.PENDING  # Default to PENDING until processing completes
        self._validate()
        
    def _validate(self) -> None:
        """Validate search properties."""
        if not self.title or not self.title.strip():
            raise ValueError("Search title cannot be empty")
            
        if len(self.title.strip()) < 3:
            raise ValueError("Search title must be at least 3 characters")

    def validate_query(self, query: str) -> bool:
        """
        Check if the query is valid for processing.
        
        Args:
            query: User's search query
            
        Returns:
            True if valid, False otherwise
        """
        if not query or not query.strip():
            return False
            
        # Basic length validation
        if len(query.strip()) < 3:
            return False
            
        return True
    
    def categorize_query(self, query: str, analysis: Dict[str, Any]) -> QueryCategory:
        """
        Categorize a query based on analysis results.
        
        Args:
            query: The search query
            analysis: Analysis results from LLM or other processing
            
        Returns:
            QueryCategory enum value
        """
        # Validate analysis dictionary to avoid KeyErrors
        is_legal_query = analysis.get("is_legal_query", True)
        if not is_legal_query:
            return QueryCategory.IRRELEVANT
            
        clarity_score = analysis.get("clarity_score", 0.0)
        
        if clarity_score < 0.6:
            return QueryCategory.UNCLEAR
        elif clarity_score < 0.8:
            return QueryCategory.BORDERLINE
        else:
            return QueryCategory.CLEAR
    
    def determine_query_type(self, query: str, analysis: Dict[str, Any]) -> QueryType:
        """
        Determine the type of legal query.
        
        Args:
            query: The search query
            analysis: Analysis results from LLM or other processing
            
        Returns:
            QueryType enum value
        """
        # Safely get query_type with a default
        query_type = analysis.get("query_type", "general").lower()
        
        if query_type == "court_case":
            return QueryType.COURT_CASE
        elif query_type == "legislative":
            return QueryType.LEGISLATIVE
        elif query_type == "commercial":
            return QueryType.COMMERCIAL
        else:
            return QueryType.GENERAL
    
    def update_status(self, status: QueryStatus) -> None:
        """
        Update the status of this search.
        
        Args:
            status: New status value
        """
        self.status = status
        
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the domain model to a dictionary representation.
        
        Returns:
            Dictionary representation of the search
        """
        return {
            "title": self.title,
            "description": self.description,
            "user_id": str(self.user_id) if self.user_id else None,
            "enterprise_id": str(self.enterprise_id) if self.enterprise_id else None,
            "created_at": self.created_at.isoformat(),
            "status": self.status.value
        }