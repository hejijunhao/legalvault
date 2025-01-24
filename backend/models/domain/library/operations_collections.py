# models/domain/library/operations_collections.py

from typing import List, Optional
from uuid import UUID

from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from models.database.library.collections import Collection as DBCollection
from models.domain.library.collections import Collection as DomainCollection

class CollectionOperations:
    def __init__(self, db: Session):
        self.db = db

    def create_collection(self, collection: DomainCollection) -> DomainCollection:
        db_collection = DBCollection(**collection.dict())
        self.db.add(db_collection)
        try:
            self.db.commit()
            self.db.refresh(db_collection)
            return DomainCollection.from_orm(db_collection)
        except IntegrityError:
            self.db.rollback()
            raise ValueError("Collection with this name already exists")

    def get_collection(self, collection_id: UUID) -> Optional[DomainCollection]:
        db_collection = self.db.query(DBCollection).filter(DBCollection.id == collection_id).first()
        return DomainCollection.from_orm(db_collection) if db_collection else None

    def get_collections_by_owner(self, owner_id: UUID) -> List[DomainCollection]:
        db_collections = self.db.query(DBCollection).filter(DBCollection.owner_id == owner_id).all()
        return [DomainCollection.from_orm(db_collection) for db_collection in db_collections]

    def update_collection(self, collection_id: UUID, update_data: dict) -> Optional[DomainCollection]:
        try:
            db_collection = self.db.query(DBCollection).filter(DBCollection.id == collection_id).first()
            if db_collection:
                for key, value in update_data.items():
                    if hasattr(db_collection, key):
                        setattr(db_collection, key, value)
                db_collection.updated_at = update_data.get('updated_at', db_collection.updated_at)
                self.db.commit()
                self.db.refresh(db_collection)
                return DomainCollection.from_orm(db_collection)
            return None
        except SQLAlchemyError:
            self.db.rollback()
            raise ValueError("Failed to update collection")

    def delete_collection(self, collection_id: UUID) -> bool:
        try:
            db_collection = self.db.query(DBCollection).filter(DBCollection.id == collection_id).first()
            if db_collection and not db_collection.is_default:
                self.db.delete(db_collection)
                self.db.commit()
                return True
            return False
        except SQLAlchemyError:
            self.db.rollback()
            raise ValueError("Failed to delete collection")

    def get_collections_by_type(self, collection_type: str) -> List[DomainCollection]:
        db_collections = self.db.query(DBCollection).filter(DBCollection.collection_type == collection_type).all()
        return [DomainCollection.from_orm(db_collection) for db_collection in db_collections]

    def get_default_collection(self, owner_id: UUID) -> Optional[DomainCollection]:
        db_collection = self.db.query(DBCollection).filter(
            DBCollection.owner_id == owner_id,
            DBCollection.is_default == True
        ).first()
        return DomainCollection.from_orm(db_collection) if db_collection else None

    def collection_exists(self, collection_id: UUID) -> bool:
        return self.db.query(DBCollection.id).filter(DBCollection.id == collection_id).first() is not None