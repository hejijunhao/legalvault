# models/schemas/library/masterfiledatabase.py

from datetime import datetime
from typing import Dict, List, Optional, Any
from uuid import UUID
from pydantic import BaseModel, validator, constr
from models.database.library.masterfiledatabase import FileStatus, FileSource, DocumentType

class FileAttributesSchema(BaseModel):
   file_title: Optional[str]
   file_name: Optional[str]
   authors: List[str] = []
   date_added: Optional[datetime]
   date_modified: Optional[datetime]
   date_hidden: Optional[datetime]
   date_deleted: Optional[datetime]
   document_type: Optional[DocumentType]
   file_type: Optional[str]
   executive_summary: Optional[str]
   version: Optional[str]
   languages: List[str] = []
   status: FileStatus = FileStatus.AVAILABLE
   tags: List[str] = []

class ContentDetailsSchema(BaseModel):
   clause_types: List[str] = []
   key_concepts: List[str] = []
   jurisdictions: List[str] = []
   governing_law: Optional[str]
   file_structure: Optional[Dict[str, Any]]

class MasterFileCreateSchema(BaseModel):
   source: FileSource
   external_url: constr(min_length=1)
   directory: constr(min_length=1)
   import_action: str
   file_attributes: FileAttributesSchema
   content_details: Optional[ContentDetailsSchema]
   client_id: Optional[UUID]
   project_id: Optional[UUID]
   owner_id: UUID

   @validator('directory')
   def validate_directory(cls, v):
       if not v.startswith('/'):
           raise ValueError("Directory must start with '/'")
       return v

class MasterFileUpdateSchema(BaseModel):
   external_url: Optional[constr(min_length=1)]
   directory: Optional[constr(min_length=1)]
   file_attributes: Optional[FileAttributesSchema]
   content_details: Optional[ContentDetailsSchema]
   client_id: Optional[UUID]
   project_id: Optional[UUID]

class MasterFileResponseSchema(BaseModel):
   file_id: UUID
   source: FileSource
   external_url: str
   directory: str
   import_action: str
   file_attributes: FileAttributesSchema
   content_details: ContentDetailsSchema
   client_id: Optional[UUID]
   project_id: Optional[UUID]
   owner_id: UUID
   permissions: List[UUID]
   created_at: datetime
   updated_at: datetime

   class Config:
       orm_mode = True

class FilePermissionSchema(BaseModel):
   user_id: UUID
   add: bool = True

class FileStatusSchema(BaseModel):
   action: constr(regex='^(hide|unhide|delete|start_processing|finish_processing)$')