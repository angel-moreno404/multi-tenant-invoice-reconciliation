from typing import Generic, TypeVar, Type, List, Optional, Union
from sqlalchemy.orm import Session
from sqlalchemy import and_

from app.models.base import BaseModel

ModelType = TypeVar("ModelType", bound=BaseModel)


def _to_int(tenant_id: Union[str, int]) -> int:
    """Convert tenant_id to int if it's a string."""
    if isinstance(tenant_id, str):
        return int(tenant_id)
    return tenant_id


class BaseRepository(Generic[ModelType]):
    """Base repository with common CRUD operations."""
    
    def __init__(self, model: Type[ModelType]):
        """
        Initialize repository with model.
        
        Args:
            model: SQLAlchemy model class
        """
        self.model = model
    
    def get_by_id(self, db: Session, tenant_id: Union[str, int], id: int) -> Optional[ModelType]:
        """
        Get a record by ID filtered by tenant.
        
        Args:
            db: Database session
            tenant_id: Tenant ID for filtering (str or int)
            id: Record ID
            
        Returns:
            Model instance or None
        """
        tenant_id_int = _to_int(tenant_id)
        return db.query(self.model).filter(
            and_(
                self.model.tenant_id == tenant_id_int,
                self.model.id == id
            )
        ).first()
    
    def get_all(
        self,
        db: Session,
        tenant_id: Union[str, int],
        skip: int = 0,
        limit: int = 100
    ) -> List[ModelType]:
        """
        Get all records filtered by tenant.
        
        Args:
            db: Database session
            tenant_id: Tenant ID for filtering (str or int)
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of model instances
        """
        tenant_id_int = _to_int(tenant_id)
        return db.query(self.model).filter(
            self.model.tenant_id == tenant_id_int
        ).offset(skip).limit(limit).all()
    
    def create(self, db: Session, tenant_id: Union[str, int], obj_in: dict) -> ModelType:
        """
        Create a new record.
        
        Args:
            db: Database session
            tenant_id: Tenant ID (str or int)
            obj_in: Dictionary with data to create
            
        Returns:
            Created model instance
        """
        tenant_id_int = _to_int(tenant_id)
        obj_in["tenant_id"] = tenant_id_int
        db_obj = self.model(**obj_in)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def update(
        self,
        db: Session,
        tenant_id: Union[str, int],
        id: int,
        obj_in: dict
    ) -> Optional[ModelType]:
        """
        Update a record.
        
        Args:
            db: Database session
            tenant_id: Tenant ID for filtering (str or int)
            id: Record ID
            obj_in: Dictionary with data to update
            
        Returns:
            Updated model instance or None
        """
        tenant_id_int = _to_int(tenant_id)
        db_obj = self.get_by_id(db, tenant_id_int, id)
        if not db_obj:
            return None
        
        for key, value in obj_in.items():
            setattr(db_obj, key, value)
        
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def delete(self, db: Session, tenant_id: Union[str, int], id: int) -> bool:
        """
        Delete a record.
        
        Args:
            db: Database session
            tenant_id: Tenant ID for filtering (str or int)
            id: Record ID
            
        Returns:
            True if deleted, False if not found
        """
        tenant_id_int = _to_int(tenant_id)
        db_obj = self.get_by_id(db, tenant_id_int, id)
        if not db_obj:
            return False
        
        db.delete(db_obj)
        db.commit()
        return True
