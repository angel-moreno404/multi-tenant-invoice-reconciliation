import pytest
from datetime import date
from fastapi import HTTPException

from app.models import Tenant, BankTransaction
from app.services.bank_transaction_service import BankTransactionService
from app.schemas.bank_transaction import BankTransactionImportRequest, BankTransactionCreate


def test_import_transactions(db_session, sample_tenant):
    """Test importing bank transactions."""
    service = BankTransactionService()
    
    transactions = [
        BankTransactionCreate(
            transaction_id="TXN-IMPORT-001",
            amount=100.00,
            date=date(2024, 1, 1),
            description="Imported transaction 1"
        ),
        BankTransactionCreate(
            transaction_id="TXN-IMPORT-002",
            amount=200.00,
            date=date(2024, 1, 2),
            description="Imported transaction 2"
        )
    ]
    
    import_request = BankTransactionImportRequest(
        idempotency_key="test-key-001",
        transactions=transactions
    )
    
    result = service.import_transactions(db_session, str(sample_tenant.id), import_request)
    
    assert result["imported_count"] == 2
    assert len(result["transactions"]) == 2


def test_import_transactions_idempotency(db_session, sample_tenant):
    """Test idempotency of import."""
    service = BankTransactionService()
    
    transactions = [
        BankTransactionCreate(
            transaction_id="TXN-IDEMPOTENT-001",
            amount=300.00,
            date=date(2024, 1, 3),
            description="Idempotent transaction"
        )
    ]
    
    import_request = BankTransactionImportRequest(
        idempotency_key="idempotent-key-001",
        transactions=transactions
    )
    
    # First import
    result1 = service.import_transactions(db_session, str(sample_tenant.id), import_request)
    
    # Second import with same key and payload
    result2 = service.import_transactions(db_session, str(sample_tenant.id), import_request)
    
    # Should return cached result
    assert result1["imported_count"] == result2["imported_count"]


def test_import_transactions_idempotency_conflict(db_session, sample_tenant):
    """Test idempotency conflict with different payload."""
    service = BankTransactionService()
    
    transactions1 = [
        BankTransactionCreate(
            transaction_id="TXN-CONFLICT-001",
            amount=400.00,
            date=date(2024, 1, 4),
            description="Conflict transaction"
        )
    ]
    
    transactions2 = [
        BankTransactionCreate(
            transaction_id="TXN-CONFLICT-002",  # Different transaction
            amount=500.00,
            date=date(2024, 1, 5),
            description="Different transaction"
        )
    ]
    
    import_request1 = BankTransactionImportRequest(
        idempotency_key="conflict-key-001",
        transactions=transactions1
    )
    
    import_request2 = BankTransactionImportRequest(
        idempotency_key="conflict-key-001",  # Same key
        transactions=transactions2  # Different payload
    )
    
    # First import
    service.import_transactions(db_session, str(sample_tenant.id), import_request1)
    
    # Second import with same key but different payload should fail
    with pytest.raises(HTTPException) as exc_info:
        service.import_transactions(db_session, str(sample_tenant.id), import_request2)
    
    assert exc_info.value.status_code == 409


def test_get_bank_transactions(db_session, sample_tenant, sample_bank_transaction):
    """Test getting bank transactions."""
    service = BankTransactionService()
    transactions = service.get_bank_transactions(db_session, str(sample_tenant.id))
    
    assert len(transactions) >= 1
    assert any(t.id == sample_bank_transaction.id for t in transactions)

