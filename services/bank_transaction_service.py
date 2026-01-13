import hashlib
import json
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models.bank_transaction import BankTransaction
from app.repositories.bank_transaction_repository import (
    BankTransactionRepository,
    IdempotencyCacheRepository
)
from app.schemas.bank_transaction import BankTransactionCreate, BankTransactionImportRequest


class BankTransactionService:
    """Service for bank transaction operations."""
    
    def __init__(self):
        self.repository = BankTransactionRepository()
        self.idempotency_cache = IdempotencyCacheRepository()
    
    def import_transactions(
        self,
        db: Session,
        tenant_id: str,
        import_request: BankTransactionImportRequest
    ) -> Dict[str, Any]:
        """
        Import bank transactions with idempotency.
        
        Args:
            db: Database session
            tenant_id: Tenant ID
            import_request: Import request with idempotency key and transactions
            
        Returns:
            Dictionary with imported transactions and count
            
        Raises:
            HTTPException: If idempotency key conflict
        """
        # Calculate payload hash
        payload_json = json.dumps(
            [t.model_dump() for t in import_request.transactions],
            sort_keys=True,
            default=str
        )
        payload_hash = hashlib.sha256(payload_json.encode()).hexdigest()
        
        # Check idempotency cache
        cache_entry = self.idempotency_cache.get_by_key(db, import_request.idempotency_key)
        
        if cache_entry:
            # Same key exists
            if cache_entry.payload_hash == payload_hash:
                # Same payload - return cached result
                result_data = json.loads(cache_entry.result_data)
                return result_data
            else:
                # Different payload - conflict
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Idempotency key conflict: same key with different payload"
                )
        
        # Process import
        imported_transactions = []
        for trans_data in import_request.transactions:
            # Check if transaction already exists
            existing = self.repository.get_by_transaction_id(
                db, tenant_id, trans_data.transaction_id
            )
            if not existing:
                trans_dict = trans_data.model_dump()
                trans_dict["is_reconciled"] = "false"
                db_trans = self.repository.create(db, tenant_id, trans_dict)
                imported_transactions.append(db_trans)
        
        # Create result
        result = {
            "imported_count": len(imported_transactions),
            "transactions": [
                {
                    "id": t.id,
                    "transaction_id": t.transaction_id,
                    "amount": float(t.amount),
                    "date": t.date.isoformat() if t.date else None,
                    "description": t.description,
                    "reference": t.reference,
                }
                for t in imported_transactions
            ]
        }
        
        # Cache result
        result_json = json.dumps(result, default=str)
        self.idempotency_cache.create_cache(
            db, tenant_id, import_request.idempotency_key, payload_hash, result_json
        )
        
        return result
    
    def get_bank_transaction(
        self,
        db: Session,
        tenant_id: str,
        transaction_id: int
    ) -> Optional[BankTransaction]:
        """
        Get bank transaction by ID.
        
        Args:
            db: Database session
            tenant_id: Tenant ID
            transaction_id: Transaction ID
            
        Returns:
            BankTransaction instance or None
        """
        return self.repository.get_by_id(db, tenant_id, transaction_id)
    
    def get_bank_transactions(
        self,
        db: Session,
        tenant_id: str,
        skip: int = 0,
        limit: int = 100
    ) -> List[BankTransaction]:
        """
        Get all bank transactions for a tenant.
        
        Args:
            db: Database session
            tenant_id: Tenant ID
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of BankTransaction instances
        """
        return self.repository.get_all(db, tenant_id, skip, limit)
    
    def get_unreconciled_transactions(
        self,
        db: Session,
        tenant_id: str
    ) -> List[BankTransaction]:
        """
        Get all unreconciled bank transactions for a tenant.
        
        Args:
            db: Database session
            tenant_id: Tenant ID
            
        Returns:
            List of unreconciled BankTransaction instances
        """
        return self.repository.get_unreconciled(db, tenant_id)
    
    def mark_as_reconciled(
        self,
        db: Session,
        tenant_id: str,
        transaction_id: int
    ) -> Optional[BankTransaction]:
        """
        Mark bank transaction as reconciled.
        
        Args:
            db: Database session
            tenant_id: Tenant ID
            transaction_id: Transaction ID
            
        Returns:
            Updated BankTransaction instance or None
        """
        return self.repository.update(db, tenant_id, transaction_id, {"is_reconciled": "true"})

