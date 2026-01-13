import strawberry
from typing import Optional
from datetime import datetime

from app.api.graphql.types.invoice import Invoice
from app.api.graphql.types.bank_transaction import BankTransaction


@strawberry.type
class ReconciliationMatch:
    """ReconciliationMatch GraphQL type."""
    id: int
    tenant_id: str
    invoice_id: int
    bank_transaction_id: int
    score: float
    status: str
    explanation: Optional[str]
    created_at: datetime
    updated_at: datetime
    invoice: Optional[Invoice] = None
    bank_transaction: Optional[BankTransaction] = None
    
    @classmethod
    def from_model(cls, match, invoice=None, bank_transaction=None):
        """Create from SQLAlchemy model."""
        return cls(
            id=match.id,
            tenant_id=str(match.tenant_id),
            invoice_id=match.invoice_id,
            bank_transaction_id=match.bank_transaction_id,
            score=float(match.score),
            status=match.status,
            explanation=match.explanation,
            created_at=match.created_at,
            updated_at=match.updated_at,
            invoice=Invoice.from_model(invoice) if invoice else None,
            bank_transaction=BankTransaction.from_model(bank_transaction) if bank_transaction else None
        )


@strawberry.type
class ReconciliationResponse:
    """Response type for reconciliation."""
    matches: list[ReconciliationMatch]
    total_matches: int


@strawberry.type
class ExplainReconciliationResponse:
    """Response type for reconciliation explanation."""
    explanation: str
    source: str

