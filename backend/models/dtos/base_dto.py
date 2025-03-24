# models/dtos/base_dto.py

from datetime import datetime
from typing import Dict, List, Optional, Any, TypeVar, Generic
from pydantic import BaseModel, Field
from uuid import UUID

T = TypeVar('T')

class PaginationDTO(BaseModel):
    """Base DTO for paginated results"""
    total: int
    offset: int = 0
    limit: int = 100

class PaginatedListDTO(PaginationDTO, Generic[T]):
    """Generic paginated list DTO"""
    items: List[T]

class StatusDTO(BaseModel):
    """Base DTO for status information"""
    status: str
    created_at: datetime
    updated_at: Optional[datetime] = None

    @classmethod
    def from_enum(cls, enum_value: Any) -> str:
        """Convert enum to string status"""
        return enum_value.value if hasattr(enum_value, 'value') else str(enum_value)

class TupleConverterMixin:
    """Mixin for converting database tuples to DTOs"""
    @classmethod
    def from_tuple(cls, tuple_data: tuple, field_map: Dict[int, str]) -> Dict[str, Any]:
        """
        Convert tuple to dictionary using field mapping
        
        Args:
            tuple_data: Database tuple result
            field_map: Mapping of tuple indices to field names
            
        Returns:
            Dictionary with mapped fields
        """
        result = {}
        for idx, field_name in field_map.items():
            if idx < len(tuple_data):
                result[field_name] = tuple_data[idx]
        return result