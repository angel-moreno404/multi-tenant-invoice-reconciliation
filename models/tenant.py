from sqlalchemy import Column, String
from sqlalchemy.orm import relationship

from app.models.base import BaseModel


class Tenant(BaseModel):
    """Tenant model for multi-tenancy."""
    
    __tablename__ = "tenants"
    
    name = Column(String, nullable=False, index=True)
    slug = Column(String, unique=True, nullable=False, index=True)
    
    # Relationships
    invoices = relationship("Invoice", back_populates="tenant", cascade="all, delete-orphan")
    bank_transactions = relationship("BankTransaction", back_populates="tenant", cascade="all, delete-orphan")
    reconciliation_matches = relationship("ReconciliationMatch", back_populates="tenant", cascade="all, delete-orphan")

