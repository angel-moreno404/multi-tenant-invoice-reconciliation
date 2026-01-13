from typing import Optional, Union
from sqlalchemy.orm import Session

from app.models.tenant import Tenant
from app.repositories.base import BaseRepository


class TenantRepository(BaseRepository[Tenant]):
    """Repository for Tenant model."""
    
    def __init__(self):
        # Note: Tenant doesn't use tenant_id filtering
        super().__init__(Tenant)
    
    def get_by_id(self, db: Session, id: Union[str, int]) -> Optional[Tenant]:
        """
        Get tenant by ID (overridden because Tenant doesn't use tenant_id).
        
        Args:
            db: Database session
            id: Tenant ID (string or int)
            
        Returns:
            Tenant or None
        """
        id_int = int(id) if isinstance(id, str) else id
        return db.query(Tenant).filter(Tenant.id == id_int).first()
    
    def get_by_slug(self, db: Session, slug: str) -> Optional[Tenant]:
        """
        Get tenant by slug.
        
        Args:
            db: Database session
            slug: Tenant slug
            
        Returns:
            Tenant or None
        """
        return db.query(Tenant).filter(Tenant.slug == slug).first()
    
    def create(self, db: Session, obj_in: dict) -> Tenant:
        """
        Create a tenant (overridden because Tenant doesn't use tenant_id).
        
        Args:
            db: Database session
            obj_in: Dictionary with data to create
            
        Returns:
            Created Tenant instance
        """
        db_obj = Tenant(**obj_in)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

