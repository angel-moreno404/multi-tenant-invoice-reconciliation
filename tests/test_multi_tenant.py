import pytest
from datetime import date

from app.models import Tenant, Invoice
from app.services.invoice_service import InvoiceService
from app.schemas.invoice import InvoiceCreate


def test_tenant_isolation(db_session):
    """Test that tenants are isolated from each other."""
    # Create two tenants
    tenant1 = Tenant(name="Tenant 1", slug="tenant-1")
    tenant2 = Tenant(name="Tenant 2", slug="tenant-2")
    db_session.add(tenant1)
    db_session.add(tenant2)
    db_session.commit()
    db_session.refresh(tenant1)
    db_session.refresh(tenant2)
    
    # Create invoices for each tenant
    invoice_service = InvoiceService()
    
    invoice1_data = InvoiceCreate(
        invoice_number="INV-TENANT1-001",
        vendor="Vendor 1",
        amount=100.00,
        due_date=date(2024, 1, 1),
        description="Tenant 1 invoice"
    )
    invoice1 = invoice_service.create_invoice(db_session, str(tenant1.id), invoice1_data)
    
    invoice2_data = InvoiceCreate(
        invoice_number="INV-TENANT2-001",
        vendor="Vendor 2",
        amount=200.00,
        due_date=date(2024, 1, 2),
        description="Tenant 2 invoice"
    )
    invoice2 = invoice_service.create_invoice(db_session, str(tenant2.id), invoice2_data)
    
    # Get invoices for tenant1
    tenant1_invoices = invoice_service.get_invoices(db_session, str(tenant1.id))
    tenant1_invoice_ids = {inv.id for inv in tenant1_invoices}
    
    # Get invoices for tenant2
    tenant2_invoices = invoice_service.get_invoices(db_session, str(tenant2.id))
    tenant2_invoice_ids = {inv.id for inv in tenant2_invoices}
    
    # Verify isolation
    assert invoice1.id in tenant1_invoice_ids
    assert invoice1.id not in tenant2_invoice_ids
    assert invoice2.id in tenant2_invoice_ids
    assert invoice2.id not in tenant1_invoice_ids


def test_get_invoice_wrong_tenant(db_session):
    """Test that getting an invoice from wrong tenant returns None."""
    # Create two tenants
    tenant1 = Tenant(name="Tenant 1", slug="tenant-1")
    tenant2 = Tenant(name="Tenant 2", slug="tenant-2")
    db_session.add(tenant1)
    db_session.add(tenant2)
    db_session.commit()
    db_session.refresh(tenant1)
    db_session.refresh(tenant2)
    
    # Create invoice for tenant1
    invoice_service = InvoiceService()
    invoice_data = InvoiceCreate(
        invoice_number="INV-ISOLATE-001",
        vendor="Isolation Vendor",
        amount=300.00,
        due_date=date(2024, 1, 3),
        description="Isolation invoice"
    )
    invoice = invoice_service.create_invoice(db_session, str(tenant1.id), invoice_data)
    
    # Try to get invoice using tenant2 ID
    wrong_invoice = invoice_service.get_invoice(db_session, str(tenant2.id), invoice.id)
    
    # Should return None (not found)
    assert wrong_invoice is None

