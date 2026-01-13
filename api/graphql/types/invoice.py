import strawberry
from typing import Optional
from datetime import date, datetime
from decimal import Decimal


@strawberry.type
class Invoice:
    """Invoice GraphQL type."""
    id: int
    tenant_id: str
    invoice_number: str
    vendor: str
    amount: float
    due_date: date
    description: Optional[str]
    is_reconciled: str
    created_at: datetime
    updated_at: datetime
    
    @classmethod
    def from_model(cls, invoice):
        """Create from SQLAlchemy model."""
        return cls(
            id=invoice.id,
            tenant_id=str(invoice.tenant_id),
            invoice_number=invoice.invoice_number,
            vendor=invoice.vendor,
            amount=float(invoice.amount),
            due_date=invoice.due_date,
            description=invoice.description,
            is_reconciled=invoice.is_reconciled,
            created_at=invoice.created_at,
            updated_at=invoice.updated_at
        )


@strawberry.input
class InvoiceInput:
    """Input type for creating an invoice."""
    invoice_number: str
    vendor: str
    amount: float
    due_date: date
    description: Optional[str] = None

