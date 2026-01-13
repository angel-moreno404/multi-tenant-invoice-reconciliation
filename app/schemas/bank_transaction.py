from pydantic import BaseModel, Field, field_validator
from typing import Optional, List, Union
from datetime import date, datetime
from decimal import Decimal


class BankTransactionBase(BaseModel):
    """Base schema for BankTransaction."""
    transaction_id: str
    amount: Decimal = Field(..., decimal_places=2)
    date: date
    description: Optional[str] = None
    reference: Optional[str] = None


class BankTransactionCreate(BankTransactionBase):
    """Schema for creating a BankTransaction."""
    pass


class BankTransactionImportRequest(BaseModel):
    """Schema for importing bank transactions."""
    idempotency_key: str
    transactions: List[BankTransactionCreate]


class BankTransactionResponse(BankTransactionBase):
    """Schema for BankTransaction response."""
    id: int
    tenant_id: str
    is_reconciled: str
    created_at: datetime
    updated_at: datetime
    
    @field_validator('tenant_id', mode='before')
    @classmethod
    def convert_tenant_id_to_str(cls, v: Union[str, int]) -> str:
        """Convert tenant_id to string if it's an integer."""
        return str(v) if isinstance(v, int) else v
    
    class Config:
        from_attributes = True


class BankTransactionImportResponse(BaseModel):
    """Schema for bank transaction import response."""
    imported_count: int
    transactions: List[BankTransactionResponse]

