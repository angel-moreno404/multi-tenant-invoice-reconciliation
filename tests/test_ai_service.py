import pytest
from unittest.mock import Mock, patch, AsyncMock

from app.services.ai_service import AIService, AIServiceError
from app.core.config import settings


def test_ai_service_no_provider():
    """Test AI service with no provider configured."""
    with patch('app.services.ai_service.settings') as mock_settings:
        mock_settings.AI_PROVIDER = "none"
        mock_settings.OPENAI_API_KEY = None
        mock_settings.ANTHROPIC_API_KEY = None
        
        service = AIService()
        
        invoice_data = {"invoice_number": "INV-001", "amount": 1000.00}
        transaction_data = {"transaction_id": "TXN-001", "amount": 1000.00}
        
        with pytest.raises(AIServiceError):
            import asyncio
            asyncio.run(service.explain_reconciliation(invoice_data, transaction_data, 50.0))


@pytest.mark.asyncio
async def test_ai_service_graceful_fallback():
    """Test AI service graceful fallback."""
    service = AIService()
    
    invoice_data = {"invoice_number": "INV-001", "amount": 1000.00}
    transaction_data = {"transaction_id": "TXN-001", "amount": 1000.00}
    
    # Mock AI service to raise error
    with patch.object(service, 'explain_reconciliation', side_effect=AIServiceError("AI service error")):
        with pytest.raises(AIServiceError):
            await service.explain_reconciliation(invoice_data, transaction_data, 50.0)


def test_deterministic_explanation():
    """Test deterministic explanation generation."""
    from app.services.reconciliation_engine import ReconciliationEngine, ReconciliationMatchResult
    
    engine = ReconciliationEngine()
    
    from app.models.invoice import Invoice
    from app.models.bank_transaction import BankTransaction
    from datetime import date
    
    invoice = Invoice(
        id=1,
        invoice_number="INV-001",
        vendor="Test Vendor",
        amount=1000.00,
        due_date=date(2024, 1, 15),
        description="Test invoice"
    )
    
    transaction = BankTransaction(
        id=1,
        transaction_id="TXN-001",
        amount=1000.00,
        date=date(2024, 1, 15),
        description="Test transaction"
    )
    
    match_result = engine.calculate_match_score(invoice, transaction)
    explanation = engine.generate_deterministic_explanation(match_result, invoice, transaction)
    
    assert explanation is not None
    assert len(explanation) > 0
    assert "Match score" in explanation or "score" in explanation.lower()

