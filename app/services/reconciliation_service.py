from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session

from app.models.reconciliation import ReconciliationMatch
from app.repositories.reconciliation_repository import ReconciliationRepository
from app.services.reconciliation_engine import ReconciliationEngine, ReconciliationMatchResult
from app.services.ai_service import get_ai_service, AIServiceError
from app.services.invoice_service import InvoiceService
from app.services.bank_transaction_service import BankTransactionService


class ReconciliationService:
    """Service for reconciliation operations."""
    
    def __init__(self):
        self.repository = ReconciliationRepository()
        self.engine = ReconciliationEngine()
        self.invoice_service = InvoiceService()
        self.bank_transaction_service = BankTransactionService()
        self.ai_service = get_ai_service()
    
    def reconcile(
        self,
        db: Session,
        tenant_id: str
    ) -> List[ReconciliationMatch]:
        """
        Run reconciliation for a tenant.
        
        Args:
            db: Database session
            tenant_id: Tenant ID
            
        Returns:
            List of ReconciliationMatch instances
        """
        # Get unreconciled invoices and transactions
        invoices = self.invoice_service.get_unreconciled_invoices(db, tenant_id)
        transactions = self.bank_transaction_service.get_unreconciled_transactions(db, tenant_id)
        
        # Find matches
        match_results = self.engine.find_matches(invoices, transactions)
        
        # Create reconciliation matches
        matches = []
        for match_result in match_results:
            # Skip low-score matches (threshold can be adjusted)
            if match_result.score < 20:
                continue
            
            # Generate deterministic explanation
            invoice = next(i for i in invoices if i.id == match_result.invoice_id)
            transaction = next(t for t in transactions if t.id == match_result.bank_transaction_id)
            
            explanation = self.engine.generate_deterministic_explanation(
                match_result, invoice, transaction
            )
            
            # Create match record
            match = self.repository.create_match(
                db, tenant_id, match_result.invoice_id,
                match_result.bank_transaction_id, match_result.score, explanation
            )
            matches.append(match)
        
        return matches
    
    def confirm_match(
        self,
        db: Session,
        tenant_id: str,
        match_id: int
    ) -> Optional[ReconciliationMatch]:
        """
        Confirm a reconciliation match.
        
        Args:
            db: Database session
            tenant_id: Tenant ID
            match_id: Match ID
            
        Returns:
            Updated ReconciliationMatch instance or None
        """
        match = self.repository.get_by_match_id(db, tenant_id, match_id)
        if not match:
            return None
        
        # Update match status
        match = self.repository.update(db, tenant_id, match_id, {"status": "confirmed"})
        
        if match:
            # Mark invoice and transaction as reconciled
            self.invoice_service.mark_as_reconciled(db, tenant_id, match.invoice_id)
            self.bank_transaction_service.mark_as_reconciled(
                db, tenant_id, match.bank_transaction_id
            )
        
        return match
    
    async def explain_match(
        self,
        db: Session,
        tenant_id: str,
        match_id: int
    ) -> Dict[str, Any]:
        """
        Generate explanation for a reconciliation match.
        
        Args:
            db: Database session
            tenant_id: Tenant ID
            match_id: Match ID
            
        Returns:
            Dictionary with explanation and source
        """
        match = self.repository.get_by_match_id(db, tenant_id, match_id)
        if not match:
            return {"explanation": "Match not found", "source": "error"}
        
        # Get invoice and transaction data
        invoice = self.invoice_service.get_invoice(db, tenant_id, match.invoice_id)
        transaction = self.bank_transaction_service.get_bank_transaction(
            db, tenant_id, match.bank_transaction_id
        )
        
        if not invoice or not transaction:
            return {"explanation": "Invoice or transaction not found", "source": "error"}
        
        # Try AI explanation first
        try:
            invoice_data = {
                "invoice_number": invoice.invoice_number,
                "vendor": invoice.vendor,
                "amount": float(invoice.amount),
                "due_date": invoice.due_date.isoformat() if invoice.due_date else None,
                "description": invoice.description,
            }
            transaction_data = {
                "transaction_id": transaction.transaction_id,
                "amount": float(transaction.amount),
                "date": transaction.date.isoformat() if transaction.date else None,
                "description": transaction.description,
                "reference": transaction.reference,
            }
            
            ai_explanation = await self.ai_service.explain_reconciliation(
                invoice_data, transaction_data, float(match.score)
            )
            
            return {
                "explanation": ai_explanation,
                "source": "ai"
            }
        except AIServiceError:
            # Fallback to deterministic explanation
            pass
        
        # Fallback to deterministic explanation
        explanation = match.explanation or "No explanation available"
        return {
            "explanation": explanation,
            "source": "deterministic"
        }

