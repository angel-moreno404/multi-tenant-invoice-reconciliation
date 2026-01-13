import pytest
from datetime import date, timedelta

from app.models import Tenant, Invoice, BankTransaction, ReconciliationMatch
from app.services.reconciliation_service import ReconciliationService
from app.services.reconciliation_engine import ReconciliationEngine
from app.services.invoice_service import InvoiceService
from app.services.bank_transaction_service import BankTransactionService
from app.schemas.invoice import InvoiceCreate
from app.schemas.bank_transaction import BankTransactionCreate


def test_reconciliation_engine_exact_match(db_session, sample_tenant):
    """Test reconciliation engine with exact match."""
    engine = ReconciliationEngine()
    
    invoice = Invoice(
        tenant_id=sample_tenant.id,
        invoice_number="INV-MATCH-001",
        vendor="Match Vendor",
        amount=1000.00,
        due_date=date(2024, 1, 15),
        description="Match invoice"
    )
    
    transaction = BankTransaction(
        tenant_id=sample_tenant.id,
        transaction_id="TXN-MATCH-001",
        amount=1000.00,
        date=date(2024, 1, 15),
        description="Match transaction"
    )
    
    result = engine.calculate_match_score(invoice, transaction)
    
    assert result.score >= 50  # Exact amount match
    assert result.invoice_id == invoice.id
    assert result.bank_transaction_id == transaction.id


def test_reconciliation_engine_date_proximity(db_session, sample_tenant):
    """Test reconciliation engine with date proximity."""
    engine = ReconciliationEngine()
    
    invoice = Invoice(
        tenant_id=sample_tenant.id,
        invoice_number="INV-DATE-001",
        vendor="Date Vendor",
        amount=500.00,
        due_date=date(2024, 1, 15),
        description="Date invoice"
    )
    
    transaction = BankTransaction(
        tenant_id=sample_tenant.id,
        transaction_id="TXN-DATE-001",
        amount=500.00,
        date=date(2024, 1, 17),  # 2 days after
        description="Date transaction"
    )
    
    result = engine.calculate_match_score(invoice, transaction)
    
    assert result.score >= 50  # Exact amount + date proximity
    assert len(result.reasons) >= 2


def test_reconcile(db_session, sample_tenant):
    """Test reconciliation service."""
    # Create invoice and transaction
    invoice_service = InvoiceService()
    transaction_service = BankTransactionService()
    
    invoice_data = InvoiceCreate(
        invoice_number="INV-RECONCILE-001",
        vendor="Reconcile Vendor",
        amount=750.00,
        due_date=date(2024, 1, 20),
        description="Reconcile invoice"
    )
    invoice = invoice_service.create_invoice(db_session, str(sample_tenant.id), invoice_data)
    
    trans_data = BankTransactionCreate(
        transaction_id="TXN-RECONCILE-001",
        amount=750.00,
        date=date(2024, 1, 21),
        description="Reconcile transaction"
    )
    from app.schemas.bank_transaction import BankTransactionImportRequest
    import_request = BankTransactionImportRequest(
        idempotency_key="reconcile-key-001",
        transactions=[trans_data]
    )
    result = transaction_service.import_transactions(db_session, str(sample_tenant.id), import_request)
    transaction_id = result["transactions"][0]["id"]
    
    # Run reconciliation
    reconciliation_service = ReconciliationService()
    matches = reconciliation_service.reconcile(db_session, str(sample_tenant.id))
    
    assert len(matches) >= 1
    match = next((m for m in matches if m.invoice_id == invoice.id), None)
    assert match is not None
    assert match.score > 0


def test_confirm_match(db_session, sample_tenant):
    """Test confirming a match."""
    # Create invoice, transaction, and match
    invoice_service = InvoiceService()
    transaction_service = BankTransactionService()
    
    invoice_data = InvoiceCreate(
        invoice_number="INV-CONFIRM-001",
        vendor="Confirm Vendor",
        amount=800.00,
        due_date=date(2024, 1, 25),
        description="Confirm invoice"
    )
    invoice = invoice_service.create_invoice(db_session, str(sample_tenant.id), invoice_data)
    
    trans_data = BankTransactionCreate(
        transaction_id="TXN-CONFIRM-001",
        amount=800.00,
        date=date(2024, 1, 25),
        description="Confirm transaction"
    )
    from app.schemas.bank_transaction import BankTransactionImportRequest
    import_request = BankTransactionImportRequest(
        idempotency_key="confirm-key-001",
        transactions=[trans_data]
    )
    result = transaction_service.import_transactions(db_session, str(sample_tenant.id), import_request)
    transaction_id = result["transactions"][0]["id"]
    
    # Run reconciliation
    reconciliation_service = ReconciliationService()
    matches = reconciliation_service.reconcile(db_session, str(sample_tenant.id))
    match = next((m for m in matches if m.invoice_id == invoice.id), None)
    
    assert match is not None
    
    # Confirm match
    confirmed_match = reconciliation_service.confirm_match(db_session, str(sample_tenant.id), match.id)
    
    assert confirmed_match is not None
    assert confirmed_match.status == "confirmed"
    
    # Verify invoice and transaction are marked as reconciled
    invoice = invoice_service.get_invoice(db_session, str(sample_tenant.id), invoice.id)
    assert invoice.is_reconciled == "true"

