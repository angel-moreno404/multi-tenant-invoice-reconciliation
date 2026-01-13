from sqlalchemy import Column, String, Integer, ForeignKey, Numeric
from sqlalchemy.orm import relationship

from app.models.base import BaseModel


class ReconciliationMatch(BaseModel):
    """Reconciliation match model."""
    
    __tablename__ = "reconciliation_matches"
    
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False, index=True)
    invoice_id = Column(Integer, ForeignKey("invoices.id"), nullable=False, index=True)
    bank_transaction_id = Column(Integer, ForeignKey("bank_transactions.id"), nullable=False, index=True)
    score = Column(Numeric(precision=5, scale=2), nullable=False)
    status = Column(String, default="pending", nullable=False)  # "pending", "confirmed", "rejected"
    explanation = Column(String)  # AI-generated or deterministic explanation
    
    # Relationships
    tenant = relationship("Tenant", back_populates="reconciliation_matches")
    invoice = relationship("Invoice", back_populates="reconciliation_matches")
    bank_transaction = relationship("BankTransaction", back_populates="reconciliation_matches")


class IdempotencyCache(BaseModel):
    """Idempotency cache for bank transaction imports."""
    
    __tablename__ = "idempotency_cache"
    
    idempotency_key = Column(String, unique=True, nullable=False, index=True)
    tenant_id = Column(Integer, nullable=False, index=True)
    payload_hash = Column(String, nullable=False)
    result_data = Column(String)  # JSON string
    created_at = Column(String, nullable=False)  # ISO format string

