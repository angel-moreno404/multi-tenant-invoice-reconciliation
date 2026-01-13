import strawberry
from typing import List
from sqlalchemy.orm import Session

from app.api.graphql.types.tenant import Tenant
from app.api.graphql.types.invoice import Invoice
from app.api.graphql.types.bank_transaction import BankTransaction, BankTransactionInput
from app.api.graphql.types.reconciliation import ReconciliationResponse, ReconciliationMatch
from app.services.tenant_service import TenantService
from app.services.invoice_service import InvoiceService
from app.services.bank_transaction_service import BankTransactionService
from app.services.reconciliation_service import ReconciliationService
from app.schemas.tenant import TenantCreate
from app.schemas.invoice import InvoiceCreate
from app.schemas.bank_transaction import BankTransactionImportRequest, BankTransactionCreate
from app.core.database import SessionLocal


@strawberry.type
class Mutation:
    """GraphQL mutations."""
    
    @strawberry.mutation
    def create_tenant(self, name: str, slug: str) -> Tenant:
        """Create a new tenant."""
        db = SessionLocal()
        try:
            service = TenantService()
            tenant_data = TenantCreate(name=name, slug=slug)
            tenant = service.create_tenant(db, tenant_data)
            return Tenant.from_model(tenant)
        finally:
            db.close()
    
    @strawberry.mutation
    def create_invoice(
        self,
        tenant_id: str,
        invoice_number: str,
        vendor: str,
        amount: float,
        due_date: str,
        description: str = None
    ) -> Invoice:
        """Create a new invoice."""
        from datetime import datetime
        
        db = SessionLocal()
        try:
            service = InvoiceService()
            due_date_obj = datetime.fromisoformat(due_date).date()
            invoice_data = InvoiceCreate(
                invoice_number=invoice_number,
                vendor=vendor,
                amount=amount,
                due_date=due_date_obj,
                description=description
            )
            invoice = service.create_invoice(db, tenant_id, invoice_data)
            return Invoice.from_model(invoice)
        finally:
            db.close()
    
    @strawberry.mutation
    def delete_invoice(self, tenant_id: str, invoice_id: int) -> bool:
        """Delete an invoice."""
        db = SessionLocal()
        try:
            service = InvoiceService()
            deleted = service.delete_invoice(db, tenant_id, invoice_id)
            return deleted
        finally:
            db.close()
    
    @strawberry.mutation
    def import_bank_transactions(
        self,
        tenant_id: str,
        idempotency_key: str,
        transactions: List[BankTransactionInput]
    ) -> List[BankTransaction]:
        """Import bank transactions."""
        from datetime import datetime
        
        db = SessionLocal()
        try:
            service = BankTransactionService()
            
            # Convert to BankTransactionCreate
            trans_list = []
            for t_input in transactions:
                # BankTransactionInput.date is already a date type from strawberry
                trans_list.append(BankTransactionCreate(
                    transaction_id=t_input.transaction_id,
                    amount=t_input.amount,
                    date=t_input.date,
                    description=t_input.description,
                    reference=t_input.reference
                ))
            
            import_request = BankTransactionImportRequest(
                idempotency_key=idempotency_key,
                transactions=trans_list
            )
            result = service.import_transactions(db, tenant_id, import_request)
            
            # Return imported transactions
            imported = []
            for t_data in result["transactions"]:
                trans = service.get_bank_transaction(db, tenant_id, t_data["id"])
                if trans:
                    imported.append(BankTransaction.from_model(trans))
            return imported
        finally:
            db.close()
    
    @strawberry.mutation
    def reconcile(self, tenant_id: str) -> ReconciliationResponse:
        """Run reconciliation for a tenant."""
        db = SessionLocal()
        try:
            service = ReconciliationService()
            matches = service.reconcile(db, tenant_id)
            
            return ReconciliationResponse(
                matches=[ReconciliationMatch.from_model(m) for m in matches],
                total_matches=len(matches)
            )
        finally:
            db.close()
    
    @strawberry.mutation
    def confirm_match(self, tenant_id: str, match_id: int) -> ReconciliationMatch:
        """Confirm a reconciliation match."""
        db = SessionLocal()
        try:
            service = ReconciliationService()
            match = service.confirm_match(db, tenant_id, match_id)
            if not match:
                raise Exception(f"Match {match_id} not found")
            return ReconciliationMatch.from_model(match)
        finally:
            db.close()

