from typing import List, Optional, Union
from sqlalchemy.orm import Session
from sqlalchemy import and_

from app.models.invoice import Invoice
from app.repositories.base import BaseRepository, _to_int


class InvoiceRepository(BaseRepository[Invoice]):
    """Repository for Invoice model."""
    
    def __init__(self):
        super().__init__(Invoice)
    
    def get_by_invoice_number(
        self,
        db: Session,
        tenant_id: Union[str, int],
        invoice_number: str
    ) -> Optional[Invoice]:
        """
        Get invoice by invoice number.
        
        Args:
            db: Database session
            tenant_id: Tenant ID
            invoice_number: Invoice number
            
        Returns:
            Invoice or None
        """
        tenant_id_int = _to_int(tenant_id)
        return db.query(Invoice).filter(
            and_(
                Invoice.tenant_id == tenant_id_int,
                Invoice.invoice_number == invoice_number
            )
        ).first()
    
    def get_unreconciled(
        self,
        db: Session,
        tenant_id: Union[str, int]
    ) -> List[Invoice]:
        """
        Get all unreconciled invoices.
        
        Args:
            db: Database session
            tenant_id: Tenant ID
            
        Returns:
            List of unreconciled invoices
        """
        tenant_id_int = _to_int(tenant_id)
        return db.query(Invoice).filter(
            and_(
                Invoice.tenant_id == tenant_id_int,
                Invoice.is_reconciled == "false"
            )
        ).all()
    
    def filter_by_vendor(
        self,
        db: Session,
        tenant_id: Union[str, int],
        vendor: str
    ) -> List[Invoice]:
        """
        Filter invoices by vendor.
        
        Args:
            db: Database session
            tenant_id: Tenant ID
            vendor: Vendor name
            
        Returns:
            List of invoices
        """
        tenant_id_int = _to_int(tenant_id)
        return db.query(Invoice).filter(
            and_(
                Invoice.tenant_id == tenant_id_int,
                Invoice.vendor == vendor
            )
        ).all()
