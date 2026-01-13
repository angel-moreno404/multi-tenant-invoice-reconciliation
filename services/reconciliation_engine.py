from typing import List, Tuple
from datetime import datetime, timedelta
from decimal import Decimal
from difflib import SequenceMatcher

from app.models.invoice import Invoice
from app.models.bank_transaction import BankTransaction


class ReconciliationMatchResult:
    """Result of a reconciliation match calculation."""
    
    def __init__(
        self,
        invoice_id: int,
        bank_transaction_id: int,
        score: float,
        reasons: List[str]
    ):
        self.invoice_id = invoice_id
        self.bank_transaction_id = bank_transaction_id
        self.score = score
        self.reasons = reasons


class ReconciliationEngine:
    """Engine for deterministic reconciliation matching."""
    
    # Heuristic weights
    EXACT_AMOUNT_MATCH = 50
    AMOUNT_WITHIN_TOLERANCE = 30
    DATE_PROXIMITY = 15
    TEXT_SIMILARITY = 10
    VENDOR_HINT = 10
    
    # Tolerances
    AMOUNT_TOLERANCE_PERCENT = 0.01  # 1%
    DATE_PROXIMITY_DAYS = 3
    
    def calculate_match_score(
        self,
        invoice: Invoice,
        bank_transaction: BankTransaction
    ) -> ReconciliationMatchResult:
        """
        Calculate match score between invoice and bank transaction.
        
        Args:
            invoice: Invoice instance
            bank_transaction: BankTransaction instance
            
        Returns:
            ReconciliationMatchResult with score and reasons
        """
        score = 0.0
        reasons = []
        
        # Convert amounts to Decimal for precise comparison
        invoice_amount = Decimal(str(invoice.amount))
        transaction_amount = Decimal(str(bank_transaction.amount))
        
        # Exact amount match (+50)
        if invoice_amount == transaction_amount:
            score += self.EXACT_AMOUNT_MATCH
            reasons.append("Exact amount match")
        
        # Amount within tolerance (+30)
        elif abs(invoice_amount - transaction_amount) / invoice_amount <= self.AMOUNT_TOLERANCE_PERCENT:
            score += self.AMOUNT_WITHIN_TOLERANCE
            diff = abs(float(invoice_amount - transaction_amount))
            reasons.append(f"Amount within tolerance ({diff:.2f} difference)")
        
        # Date proximity (±3 days) (+15)
        if invoice.due_date and bank_transaction.date:
            date_diff = abs((invoice.due_date - bank_transaction.date).days)
            if date_diff <= self.DATE_PROXIMITY_DAYS:
                score += self.DATE_PROXIMITY
                reasons.append(f"Date proximity ({date_diff} days difference)")
        
        # Text similarity (+10)
        text_similarity = self._calculate_text_similarity(invoice, bank_transaction)
        if text_similarity > 0.5:  # 50% similarity threshold
            score += self.TEXT_SIMILARITY
            reasons.append(f"Text similarity ({text_similarity:.1%})")
        
        # Vendor hint (+10)
        if self._vendor_hint_match(invoice, bank_transaction):
            score += self.VENDOR_HINT
            reasons.append("Vendor/proveedor hint match")
        
        return ReconciliationMatchResult(
            invoice_id=invoice.id,
            bank_transaction_id=bank_transaction.id,
            score=float(score),
            reasons=reasons
        )
    
    def _calculate_text_similarity(
        self,
        invoice: Invoice,
        bank_transaction: BankTransaction
    ) -> float:
        """
        Calculate text similarity between invoice and bank transaction.
        
        Args:
            invoice: Invoice instance
            bank_transaction: BankTransaction instance
            
        Returns:
            Similarity score between 0 and 1
        """
        # Combine text fields
        invoice_text = " ".join(filter(None, [
            invoice.vendor or "",
            invoice.description or "",
            invoice.invoice_number or ""
        ])).lower()
        
        transaction_text = " ".join(filter(None, [
            bank_transaction.description or "",
            bank_transaction.reference or "",
            bank_transaction.transaction_id or ""
        ])).lower()
        
        if not invoice_text or not transaction_text:
            return 0.0
        
        # Use SequenceMatcher for similarity
        similarity = SequenceMatcher(None, invoice_text, transaction_text).ratio()
        
        # Also check if vendor appears in transaction text
        if invoice.vendor:
            vendor_lower = invoice.vendor.lower()
            if vendor_lower in transaction_text:
                similarity = max(similarity, 0.6)  # Boost if vendor appears
        
        return similarity
    
    def _vendor_hint_match(
        self,
        invoice: Invoice,
        bank_transaction: BankTransaction
    ) -> bool:
        """
        Check if vendor hint matches between invoice and transaction.
        
        Args:
            invoice: Invoice instance
            bank_transaction: BankTransaction instance
            
        Returns:
            True if vendor hint matches
        """
        if not invoice.vendor:
            return False
        
        vendor_lower = invoice.vendor.lower()
        transaction_text = " ".join(filter(None, [
            bank_transaction.description or "",
            bank_transaction.reference or ""
        ])).lower()
        
        # Check if vendor appears in transaction text
        return vendor_lower in transaction_text
    
    def find_matches(
        self,
        invoices: List[Invoice],
        bank_transactions: List[BankTransaction]
    ) -> List[ReconciliationMatchResult]:
        """
        Find all potential matches between invoices and bank transactions.
        
        Args:
            invoices: List of invoices
            bank_transactions: List of bank transactions
            
        Returns:
            List of ReconciliationMatchResult sorted by score descending
        """
        matches = []
        
        for invoice in invoices:
            for bank_transaction in bank_transactions:
                match_result = self.calculate_match_score(invoice, bank_transaction)
                matches.append(match_result)
        
        # Sort by score descending
        matches.sort(key=lambda x: x.score, reverse=True)
        
        return matches
    
    def generate_deterministic_explanation(
        self,
        match_result: ReconciliationMatchResult,
        invoice: Invoice,
        bank_transaction: BankTransaction
    ) -> str:
        """
        Generate deterministic explanation for a match.
        
        Args:
            match_result: Reconciliation match result
            invoice: Invoice instance
            bank_transaction: BankTransaction instance
            
        Returns:
            Explanation string
        """
        if not match_result.reasons:
            return f"Low match score ({match_result.score}). No strong indicators of a match."
        
        explanation_parts = [f"Match score: {match_result.score}"]
        explanation_parts.append("Reasons:")
        for reason in match_result.reasons:
            explanation_parts.append(f"- {reason}")
        
        return " ".join(explanation_parts)

