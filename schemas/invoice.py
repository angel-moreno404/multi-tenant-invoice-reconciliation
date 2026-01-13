from pydantic import BaseModel, Field, field_validator
from typing import Optional, Union
from datetime import date, datetime
from decimal import Decimal


class InvoiceBase(BaseModel):
    """Base schema for Invoice."""
    invoice_number: str
    vendor: str
    amount: Decimal = Field(..., decimal_places=2)
    due_date: date
    description: Optional[str] = None


class InvoiceCreate(InvoiceBase):
    """Schema for creating an Invoice."""
    pass


class InvoiceUpdate(BaseModel):
    """Schema for updating an Invoice."""
    invoice_number: Optional[str] = None
    vendor: Optional[str] = None
    amount: Optional[Decimal] = None
    due_date: Optional[date] = None
    description: Optional[str] = None


class InvoiceResponse(InvoiceBase):
    """Schema for Invoice response."""
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

