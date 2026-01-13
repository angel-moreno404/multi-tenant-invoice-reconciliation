from sqlalchemy import Column, String, Numeric, Date, ForeignKey, Integer
from sqlalchemy.orm import relationship

from app.models.base import BaseModel


class BankTransaction(BaseModel):
    """Bank transaction model."""
    
    __tablename__ = "bank_transactions"
    
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False, index=True)
    transaction_id = Column(String, nullable=False, unique=True, index=True)
    amount = Column(Numeric(precision=10, scale=2), nullable=False)
    date = Column(Date, nullable=False)
    description = Column(String)
    reference = Column(String)
    is_reconciled = Column(String, default="false", nullable=False)  # "true" or "false"
    
    # Relationships
    tenant = relationship("Tenant", back_populates="bank_transactions")
    reconciliation_matches = relationship("ReconciliationMatch", back_populates="bank_transaction", cascade="all, delete-orphan")

