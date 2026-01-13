from typing import List, Optional
from sqlalchemy.orm import Session

from app.models.invoice import Invoice
from app.repositories.invoice_repository import InvoiceRepository
from app.schemas.invoice import InvoiceCreate, InvoiceUpdate


class InvoiceService:
    """Service for invoice operations."""
    
    def __init__(self):
        self.repository = InvoiceRepository()
    
    def create_invoice(
        self,
        db: Session,
        tenant_id: str,
        invoice_data: InvoiceCreate
    ) -> Invoice:
        """
        Create a new invoice.
        
        Args:
            db: Database session
            tenant_id: Tenant ID
            invoice_data: Invoice creation data
            
        Returns:
            Created Invoice instance
        """
        invoice_dict = invoice_data.model_dump()
        invoice_dict["is_reconciled"] = "false"
        return self.repository.create(db, tenant_id, invoice_dict)
    
    def get_invoice(
        self,
        db: Session,
        tenant_id: str,
        invoice_id: int
    ) -> Optional[Invoice]:
        """
        Get invoice by ID.
        
        Args:
            db: Database session
            tenant_id: Tenant ID
            invoice_id: Invoice ID
            
        Returns:
            Invoice instance or None
        """
        return self.repository.get_by_id(db, tenant_id, invoice_id)
    
    def get_invoices(
        self,
        db: Session,
        tenant_id: str,
        skip: int = 0,
        limit: int = 100
    ) -> List[Invoice]:
        """
        Get all invoices for a tenant.
        
        Args:
            db: Database session
            tenant_id: Tenant ID
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of Invoice instances
        """
        return self.repository.get_all(db, tenant_id, skip, limit)
    
    def delete_invoice(
        self,
        db: Session,
        tenant_id: str,
        invoice_id: int
    ) -> bool:
        """
        Delete an invoice.
        
        Args:
            db: Database session
            tenant_id: Tenant ID
            invoice_id: Invoice ID
            
        Returns:
            True if deleted, False if not found
        """
        return self.repository.delete(db, tenant_id, invoice_id)
    
    def get_unreconciled_invoices(
        self,
        db: Session,
        tenant_id: str
    ) -> List[Invoice]:
        """
        Get all unreconciled invoices for a tenant.
        
        Args:
            db: Database session
            tenant_id: Tenant ID
            
        Returns:
            List of unreconciled Invoice instances
        """
        return self.repository.get_unreconciled(db, tenant_id)
    
    def mark_as_reconciled(
        self,
        db: Session,
        tenant_id: str,
        invoice_id: int
    ) -> Optional[Invoice]:
        """
        Mark invoice as reconciled.
        
        Args:
            db: Database session
            tenant_id: Tenant ID
            invoice_id: Invoice ID
            
        Returns:
            Updated Invoice instance or None
        """
        return self.repository.update(db, tenant_id, invoice_id, {"is_reconciled": "true"})

