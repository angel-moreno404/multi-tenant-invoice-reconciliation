from typing import List, Optional
from sqlalchemy.orm import Session

from app.models.tenant import Tenant
from app.repositories.tenant_repository import TenantRepository
from app.schemas.tenant import TenantCreate, TenantUpdate


class TenantService:
    """Service for tenant operations."""
    
    def __init__(self):
        self.repository = TenantRepository()
    
    def create_tenant(
        self,
        db: Session,
        tenant_data: TenantCreate
    ) -> Tenant:
        """
        Create a new tenant.
        
        Args:
            db: Database session
            tenant_data: Tenant creation data
            
        Returns:
            Created Tenant instance
        """
        tenant_dict = tenant_data.model_dump()
        return self.repository.create(db, tenant_dict)
    
    def get_tenant(
        self,
        db: Session,
        tenant_id: str
    ) -> Optional[Tenant]:
        """
        Get tenant by ID.
        
        Args:
            db: Database session
            tenant_id: Tenant ID (can be integer ID or slug)
            
        Returns:
            Tenant instance or None
        """
        # Try by ID first (assuming ID is integer string)
        try:
            id_int = int(tenant_id)
            tenant = self.repository.get_by_id(db, id_int)
            if tenant:
                return tenant
        except ValueError:
            pass
        
        # Try by slug
        return self.repository.get_by_slug(db, tenant_id)
    
    def get_all_tenants(
        self,
        db: Session
    ) -> List[Tenant]:
        """
        Get all tenants.
        
        Args:
            db: Database session
            
        Returns:
            List of Tenant instances
        """
        return db.query(Tenant).all()

