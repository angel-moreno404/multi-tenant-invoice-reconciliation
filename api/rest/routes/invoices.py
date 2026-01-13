from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import verify_tenant
from app.models.tenant import Tenant
from app.services.invoice_service import InvoiceService
from app.schemas.invoice import InvoiceCreate, InvoiceResponse

router = APIRouter(prefix="/tenants/{tenant_id}/invoices", tags=["invoices"])


@router.post("", response_model=InvoiceResponse, status_code=status.HTTP_201_CREATED)
def create_invoice(
    tenant_id: str,
    invoice_data: InvoiceCreate,
    db: Session = Depends(get_db),
    tenant: Tenant = Depends(verify_tenant)
):
    """
    Create a new invoice for a tenant.
    """
    service = InvoiceService()
    invoice = service.create_invoice(db, tenant_id, invoice_data)
    return invoice


@router.get("", response_model=List[InvoiceResponse])
def get_invoices(
    tenant_id: str,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    tenant: Tenant = Depends(verify_tenant)
):
    """
    Get all invoices for a tenant.
    """
    service = InvoiceService()
    invoices = service.get_invoices(db, tenant_id, skip, limit)
    return invoices


@router.delete("/{invoice_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_invoice(
    tenant_id: str,
    invoice_id: int,
    db: Session = Depends(get_db),
    tenant: Tenant = Depends(verify_tenant)
):
    """
    Delete an invoice.
    """
    service = InvoiceService()
    deleted = service.delete_invoice(db, tenant_id, invoice_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Invoice {invoice_id} not found"
        )
    return None

