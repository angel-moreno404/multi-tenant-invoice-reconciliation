from typing import List, Optional, Union
from sqlalchemy.orm import Session
from sqlalchemy import and_

from app.models.reconciliation import ReconciliationMatch
from app.repositories.base import BaseRepository, _to_int


class ReconciliationRepository(BaseRepository[ReconciliationMatch]):
    """Repository for ReconciliationMatch model."""
    
    def __init__(self):
        super().__init__(ReconciliationMatch)
    
    def get_by_match_id(
        self,
        db: Session,
        tenant_id: Union[str, int],
        match_id: int
    ) -> Optional[ReconciliationMatch]:
        """
        Get reconciliation match by match ID.
        
        Args:
            db: Database session
            tenant_id: Tenant ID
            match_id: Match ID
            
        Returns:
            ReconciliationMatch or None
        """
        return self.get_by_id(db, tenant_id, match_id)
    
    def get_pending_matches(
        self,
        db: Session,
        tenant_id: Union[str, int]
    ) -> List[ReconciliationMatch]:
        """
        Get all pending reconciliation matches.
        
        Args:
            db: Database session
            tenant_id: Tenant ID
            
        Returns:
            List of pending reconciliation matches
        """
        tenant_id_int = _to_int(tenant_id)
        return db.query(ReconciliationMatch).filter(
            and_(
                ReconciliationMatch.tenant_id == tenant_id_int,
                ReconciliationMatch.status == "pending"
            )
        ).all()
    
    def get_by_invoice_and_transaction(
        self,
        db: Session,
        tenant_id: Union[str, int],
        invoice_id: int,
        bank_transaction_id: int
    ) -> Optional[ReconciliationMatch]:
        """
        Get reconciliation match by invoice and bank transaction.
        
        Args:
            db: Database session
            tenant_id: Tenant ID
            invoice_id: Invoice ID
            bank_transaction_id: Bank transaction ID
            
        Returns:
            ReconciliationMatch or None
        """
        tenant_id_int = _to_int(tenant_id)
        return db.query(ReconciliationMatch).filter(
            and_(
                ReconciliationMatch.tenant_id == tenant_id_int,
                ReconciliationMatch.invoice_id == invoice_id,
                ReconciliationMatch.bank_transaction_id == bank_transaction_id
            )
        ).first()
    
    def create_match(
        self,
        db: Session,
        tenant_id: Union[str, int],
        invoice_id: int,
        bank_transaction_id: int,
        score: float,
        explanation: Optional[str] = None
    ) -> ReconciliationMatch:
        """
        Create a reconciliation match.
        
        Args:
            db: Database session
            tenant_id: Tenant ID
            invoice_id: Invoice ID
            bank_transaction_id: Bank transaction ID
            score: Match score
            explanation: Optional explanation
            
        Returns:
            Created ReconciliationMatch instance
        """
        tenant_id_int = _to_int(tenant_id)
        match_obj = ReconciliationMatch(
            tenant_id=tenant_id_int,
            invoice_id=invoice_id,
            bank_transaction_id=bank_transaction_id,
            score=score,
            status="pending",
            explanation=explanation
        )
        db.add(match_obj)
        db.commit()
        db.refresh(match_obj)
        return match_obj
