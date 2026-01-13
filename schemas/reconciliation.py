from pydantic import BaseModel, Field, field_validator
from typing import Optional, List, Union
from datetime import datetime
from decimal import Decimal

from app.schemas.invoice import InvoiceResponse
from app.schemas.bank_transaction import BankTransactionResponse


class ReconciliationMatchBase(BaseModel):
    """Base schema for ReconciliationMatch."""
    invoice_id: int
    bank_transaction_id: int
    score: Decimal = Field(..., decimal_places=2)
    explanation: Optional[str] = None


class ReconciliationMatchResponse(ReconciliationMatchBase):
    """Schema for ReconciliationMatch response."""
    id: int
    tenant_id: str
    status: str
    created_at: datetime
    updated_at: datetime
    invoice: Optional[InvoiceResponse] = None
    bank_transaction: Optional[BankTransactionResponse] = None
    
    @field_validator('tenant_id', mode='before')
    @classmethod
    def convert_tenant_id_to_str(cls, v: Union[str, int]) -> str:
        """Convert tenant_id to string if it's an integer."""
        return str(v) if isinstance(v, int) else v
    
    class Config:
        from_attributes = True


class ReconciliationRequest(BaseModel):
    """Schema for reconciliation request."""
    pass


class ReconciliationResponse(BaseModel):
    """Schema for reconciliation response."""
    matches: List[ReconciliationMatchResponse]
    total_matches: int


class ConfirmMatchRequest(BaseModel):
    """Schema for confirming a match."""
    pass


class ExplainReconciliationRequest(BaseModel):
    """Schema for explaining a reconciliation."""
    match_id: int


class ExplainReconciliationResponse(BaseModel):
    """Schema for explaining a reconciliation response."""
    explanation: str
    source: str  # "ai" or "deterministic"

