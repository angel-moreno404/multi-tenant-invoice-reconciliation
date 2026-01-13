import json
from typing import Optional, Dict, Any
from openai import OpenAI
from anthropic import Anthropic

from app.core.config import settings


class AIServiceError(Exception):
    """Exception raised when AI service fails."""
    pass


class AIService:
    """Service for AI-powered reconciliation explanations."""
    
    def __init__(self):
        """Initialize AI service based on configuration."""
        self.provider = settings.AI_PROVIDER.lower() if settings.AI_PROVIDER else "none"
        self.openai_client = None
        self.anthropic_client = None
        
        if self.provider == "openai" and settings.OPENAI_API_KEY:
            self.openai_client = OpenAI(api_key=settings.OPENAI_API_KEY)
        elif self.provider == "anthropic" and settings.ANTHROPIC_API_KEY:
            self.anthropic_client = Anthropic(api_key=settings.ANTHROPIC_API_KEY)
    
    async def explain_reconciliation(
        self,
        invoice_data: Dict[str, Any],
        bank_transaction_data: Dict[str, Any],
        score: float
    ) -> str:
        """
        Generate AI explanation for a reconciliation match.
        
        Args:
            invoice_data: Invoice data dictionary
            bank_transaction_data: Bank transaction data dictionary
            score: Match score
            
        Returns:
            Explanation string
            
        Raises:
            AIServiceError: If AI service fails
        """
        if self.provider == "none":
            raise AIServiceError("AI provider not configured")
        
        try:
            prompt = self._build_prompt(invoice_data, bank_transaction_data, score)
            
            if self.provider == "openai" and self.openai_client:
                return await self._explain_with_openai(prompt)
            elif self.provider == "anthropic" and self.anthropic_client:
                return await self._explain_with_anthropic(prompt)
            else:
                raise AIServiceError("AI provider not properly configured")
        except Exception as e:
            raise AIServiceError(f"AI service error: {str(e)}")
    
    def _build_prompt(
        self,
        invoice_data: Dict[str, Any],
        bank_transaction_data: Dict[str, Any],
        score: float
    ) -> str:
        """Build prompt for AI explanation."""
        return f"""
Analyze this invoice and bank transaction match:

Invoice:
- Number: {invoice_data.get('invoice_number', 'N/A')}
- Vendor: {invoice_data.get('vendor', 'N/A')}
- Amount: {invoice_data.get('amount', 'N/A')}
- Due Date: {invoice_data.get('due_date', 'N/A')}
- Description: {invoice_data.get('description', 'N/A')}

Bank Transaction:
- Transaction ID: {bank_transaction_data.get('transaction_id', 'N/A')}
- Amount: {bank_transaction_data.get('amount', 'N/A')}
- Date: {bank_transaction_data.get('date', 'N/A')}
- Description: {bank_transaction_data.get('description', 'N/A')}
- Reference: {bank_transaction_data.get('reference', 'N/A')}

Match Score: {score}

Provide a brief explanation (2-3 sentences) of why these match or why the match score is what it is.
"""
    
    async def _explain_with_openai(self, prompt: str) -> str:
        """Generate explanation using OpenAI."""
        if not self.openai_client:
            raise AIServiceError("OpenAI client not configured")
        
        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a financial reconciliation assistant."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=200,
                temperature=0.7
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            raise AIServiceError(f"OpenAI error: {str(e)}")
    
    async def _explain_with_anthropic(self, prompt: str) -> str:
        """Generate explanation using Anthropic."""
        if not self.anthropic_client:
            raise AIServiceError("Anthropic client not configured")
        
        try:
            message = self.anthropic_client.messages.create(
                model="claude-3-haiku-20240307",
                max_tokens=200,
                temperature=0.7,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            return message.content[0].text.strip()
        except Exception as e:
            raise AIServiceError(f"Anthropic error: {str(e)}")


# Singleton instance
_ai_service_instance: Optional[AIService] = None


def get_ai_service() -> AIService:
    """Get singleton AI service instance."""
    global _ai_service_instance
    if _ai_service_instance is None:
        _ai_service_instance = AIService()
    return _ai_service_instance

