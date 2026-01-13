from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import verify_tenant
from app.models.tenant import Tenant
from app.services.bank_transaction_service import BankTransactionService
from app.schemas.bank_transaction import (
    BankTransactionImportRequest,
    BankTransactionImportResponse,
    BankTransactionResponse
)

router = APIRouter(prefix="/tenants/{tenant_id}/bank-transactions", tags=["bank-transactions"])


@router.post("/import", response_model=BankTransactionImportResponse, status_code=status.HTTP_201_CREATED)
def import_bank_transactions(
    tenant_id: str,
    import_request: BankTransactionImportRequest,
    db: Session = Depends(get_db),
    tenant: Tenant = Depends(verify_tenant)
):
    """
    Import bank transactions with idempotency.
    """
    service = BankTransactionService()
    result = service.import_transactions(db, tenant_id, import_request)
    
    # Convert to response schema
    transactions = [
        service.get_bank_transaction(db, tenant_id, t["id"])
        for t in result["transactions"]
    ]
    
    return BankTransactionImportResponse(
        imported_count=result["imported_count"],
        transactions=[BankTransactionResponse.model_validate(t) for t in transactions if t]
    )

