# models/domain/research/research_errors.py

from typing import Optional, Dict, Any

class ResearchError(Exception):
    """
    Base exception for all research domain errors.
    
    Provides a foundation for domain-specific error handling with support for
    additional context through a details dictionary.
    
    Attributes:
        message: Human-readable error description
        details: Optional dictionary with additional error context
    """
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.details = details or {}

    def __str__(self) -> str:
        """String representation with details if present."""
        base = super().__str__()
        return f"{base} - Details: {self.details}" if self.details else base

class ValidationError(ResearchError):
    """
    Raised when domain validation fails.
    
    Used for validation failures in domain models like ResearchSearch and ResearchMessage.
    Examples include:
    - Invalid input data (empty strings, wrong types)
    - Business rule violations (minimum lengths, allowed values)
    - State validation failures
    """
    pass

class DatabaseError(ResearchError):
    """
    Raised for database operation failures.
    
    Wraps underlying SQLAlchemy errors while preserving the original exception
    and providing additional context. Used primarily in Operations classes
    for database interaction errors.
    
    Attributes:
        message: Human-readable error description
        details: Optional dictionary with additional error context
        original_error: The underlying exception that caused this error
    """
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None, original_error: Optional[Exception] = None):
        super().__init__(message, details)
        self.original_error = original_error  # Capture underlying SQLAlchemy error
        
    def __str__(self) -> str:
        """Enhanced string representation including original error if present."""
        base = super().__str__()
        if self.original_error:
            return f"{base} (Original error: {str(self.original_error)})"
        return base