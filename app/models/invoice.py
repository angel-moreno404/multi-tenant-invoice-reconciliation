from sqlalchemy import Column, String, Numeric, Date, ForeignKey, Integer
from sqlalchemy.orm import relationship

from app.models.base import BaseModel


class Invoice(BaseModel):
    """Invoice model."""
    
    __tablename__ = "invoices"
    
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False, index=True)
    invoice_number = Column(String, nullable=False, index=True)
    vendor = Column(String, nullable=False)
    amount = Column(Numeric(precision=10, scale=2), nullable=False)
    due_date = Column(Date, nullable=False)
    description = Column(String)
    is_reconciled = Column(String, default="false", nullable=False)  # "true" or "false"
    
    # Relationships
    tenant = relationship("Tenant", back_populates="invoices")
    reconciliation_matches = relationship("ReconciliationMatch", back_populates="invoice", cascade="all, delete-orphan")

