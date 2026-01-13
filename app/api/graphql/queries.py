import strawberry
from typing import List, Optional
from sqlalchemy.orm import Session

from app.api.graphql.types.tenant import Tenant
from app.api.graphql.types.invoice import Invoice
from app.api.graphql.types.bank_transaction import BankTransaction
from app.api.graphql.types.reconciliation import ExplainReconciliationResponse
from app.services.tenant_service import TenantService
from app.services.invoice_service import InvoiceService
from app.services.bank_transaction_service import BankTransactionService
from app.services.reconciliation_service import ReconciliationService
from app.core.database import SessionLocal


@strawberry.type
class Query:
    """GraphQL queries."""
    
    @strawberry.field
    def tenants(self) -> List[Tenant]:
        """Get all tenants."""
        db = SessionLocal()
        try:
            service = TenantService()
            tenants = service.get_all_tenants(db)
            return [Tenant.from_model(t) for t in tenants]
        finally:
            db.close()
    
    @strawberry.field
    def invoices(self, tenant_id: str, skip: int = 0, limit: int = 100) -> List[Invoice]:
        """Get invoices for a tenant."""
        db = SessionLocal()
        try:
            service = InvoiceService()
            invoices = service.get_invoices(db, tenant_id, skip, limit)
            return [Invoice.from_model(i) for i in invoices]
        finally:
            db.close()
    
    @strawberry.field
    def bank_transactions(self, tenant_id: str, skip: int = 0, limit: int = 100) -> List[BankTransaction]:
        """Get bank transactions for a tenant."""
        db = SessionLocal()
        try:
            service = BankTransactionService()
            transactions = service.get_bank_transactions(db, tenant_id, skip, limit)
            return [BankTransaction.from_model(t) for t in transactions]
        finally:
            db.close()
    
    @strawberry.field
    async def explain_reconciliation(
        self,
        tenant_id: str,
        match_id: int
    ) -> ExplainReconciliationResponse:
        """Generate explanation for a reconciliation match."""
        db = SessionLocal()
        try:
            service = ReconciliationService()
            result = await service.explain_match(db, tenant_id, match_id)
            return ExplainReconciliationResponse(
                explanation=result["explanation"],
                source=result["source"]
            )
        finally:
            db.close()

