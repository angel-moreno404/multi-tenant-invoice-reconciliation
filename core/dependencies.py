from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Generator

from app.core.database import get_db
from app.models.tenant import Tenant


def get_db_session() -> Generator[Session, None, None]:
    """Dependency for database session."""
    yield from get_db()


def verify_tenant(tenant_id: str, db: Session = Depends(get_db)) -> Tenant:
    """
    Dependency that verifies tenant exists and returns it.
    
    Args:
        tenant_id: ID of the tenant to verify (string from path, converted to int)
        db: Database session
        
    Returns:
        Tenant: Verified tenant object
        
    Raises:
        HTTPException: If tenant not found
    """
    try:
        tenant_id_int = int(tenant_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid tenant ID: {tenant_id}"
        )
    tenant = db.query(Tenant).filter(Tenant.id == tenant_id_int).first()
    if not tenant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Tenant {tenant_id} not found"
        )
    return tenant

