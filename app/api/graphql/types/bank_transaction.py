import strawberry
from typing import Optional, List
from datetime import date, datetime


@strawberry.type
class BankTransaction:
    """BankTransaction GraphQL type."""
    id: int
    tenant_id: str
    transaction_id: str
    amount: float
    date: date
    description: Optional[str]
    reference: Optional[str]
    is_reconciled: str
    created_at: datetime
    updated_at: datetime
    
    @classmethod
    def from_model(cls, transaction):
        """Create from SQLAlchemy model."""
        return cls(
            id=transaction.id,
            tenant_id=str(transaction.tenant_id),
            transaction_id=transaction.transaction_id,
            amount=float(transaction.amount),
            date=transaction.date,
            description=transaction.description,
            reference=transaction.reference,
            is_reconciled=transaction.is_reconciled,
            created_at=transaction.created_at,
            updated_at=transaction.updated_at
        )


@strawberry.input
class BankTransactionInput:
    """Input type for creating a bank transaction."""
    transaction_id: str
    amount: float
    date: date
    description: Optional[str] = None
    reference: Optional[str] = None


@strawberry.input
class BankTransactionImportInput:
    """Input type for importing bank transactions."""
    idempotency_key: str
    transactions: List[BankTransactionInput]

