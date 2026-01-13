import pytest
from datetime import date

from app.models import Tenant, Invoice
from app.services.invoice_service import InvoiceService
from app.schemas.invoice import InvoiceCreate


def test_create_invoice(db_session, sample_tenant):
    """Test creating an invoice."""
    service = InvoiceService()
    invoice_data = InvoiceCreate(
        invoice_number="INV-002",
        vendor="New Vendor",
        amount=500.00,
        due_date=date(2024, 2, 1),
        description="New invoice"
    )
    invoice = service.create_invoice(db_session, str(sample_tenant.id), invoice_data)
    
    assert invoice.invoice_number == "INV-002"
    assert invoice.vendor == "New Vendor"
    assert float(invoice.amount) == 500.00
    assert invoice.tenant_id == sample_tenant.id
    assert invoice.is_reconciled == "false"


def test_get_invoice(db_session, sample_tenant, sample_invoice):
    """Test getting an invoice."""
    service = InvoiceService()
    invoice = service.get_invoice(db_session, str(sample_tenant.id), sample_invoice.id)
    
    assert invoice is not None
    assert invoice.id == sample_invoice.id
    assert invoice.invoice_number == "INV-001"


def test_get_invoices(db_session, sample_tenant, sample_invoice):
    """Test getting all invoices."""
    service = InvoiceService()
    invoices = service.get_invoices(db_session, str(sample_tenant.id))
    
    assert len(invoices) >= 1
    assert any(inv.id == sample_invoice.id for inv in invoices)


def test_delete_invoice(db_session, sample_tenant, sample_invoice):
    """Test deleting an invoice."""
    service = InvoiceService()
    deleted = service.delete_invoice(db_session, str(sample_tenant.id), sample_invoice.id)
    
    assert deleted is True
    
    # Verify it's deleted
    invoice = service.get_invoice(db_session, str(sample_tenant.id), sample_invoice.id)
    assert invoice is None


def test_get_unreconciled_invoices(db_session, sample_tenant, sample_invoice):
    """Test getting unreconciled invoices."""
    service = InvoiceService()
    unreconciled = service.get_unreconciled_invoices(db_session, str(sample_tenant.id))
    
    assert len(unreconciled) >= 1
    assert all(inv.is_reconciled == "false" for inv in unreconciled)


def test_mark_as_reconciled(db_session, sample_tenant, sample_invoice):
    """Test marking an invoice as reconciled."""
    service = InvoiceService()
    invoice = service.mark_as_reconciled(db_session, str(sample_tenant.id), sample_invoice.id)
    
    assert invoice is not None
    assert invoice.is_reconciled == "true"

