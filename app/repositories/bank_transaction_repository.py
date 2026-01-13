from typing import List, Optional, Union
from sqlalchemy.orm import Session
from sqlalchemy import and_

from app.models.bank_transaction import BankTransaction
from app.models.reconciliation import IdempotencyCache
from app.repositories.base import BaseRepository, _to_int


class BankTransactionRepository(BaseRepository[BankTransaction]):
    """Repository for BankTransaction model."""
    
    def __init__(self):
        super().__init__(BankTransaction)
    
    def get_by_transaction_id(
        self,
        db: Session,
        tenant_id: Union[str, int],
        transaction_id: str
    ) -> Optional[BankTransaction]:
        """
        Get bank transaction by transaction ID.
        
        Args:
            db: Database session
            tenant_id: Tenant ID
            transaction_id: Transaction ID
            
        Returns:
            BankTransaction or None
        """
        tenant_id_int = _to_int(tenant_id)
        return db.query(BankTransaction).filter(
            and_(
                BankTransaction.tenant_id == tenant_id_int,
                BankTransaction.transaction_id == transaction_id
            )
        ).first()
    
    def get_unreconciled(
        self,
        db: Session,
        tenant_id: Union[str, int]
    ) -> List[BankTransaction]:
        """
        Get all unreconciled bank transactions.
        
        Args:
            db: Database session
            tenant_id: Tenant ID
            
        Returns:
            List of unreconciled bank transactions
        """
        tenant_id_int = _to_int(tenant_id)
        return db.query(BankTransaction).filter(
            and_(
                BankTransaction.tenant_id == tenant_id_int,
                BankTransaction.is_reconciled == "false"
            )
        ).all()
    
    def create_many(
        self,
        db: Session,
        tenant_id: Union[str, int],
        transactions: List[dict]
    ) -> List[BankTransaction]:
        """
        Create multiple bank transactions.
        
        Args:
            db: Database session
            tenant_id: Tenant ID
            transactions: List of transaction data dictionaries
            
        Returns:
            List of created bank transactions
        """
        tenant_id_int = _to_int(tenant_id)
        db_objects = []
        for trans_data in transactions:
            trans_data["tenant_id"] = tenant_id_int
            db_obj = BankTransaction(**trans_data)
            db_objects.append(db_obj)
            db.add(db_obj)
        
        db.commit()
        for db_obj in db_objects:
            db.refresh(db_obj)
        
        return db_objects


class IdempotencyCacheRepository(BaseRepository[IdempotencyCache]):
    """Repository for IdempotencyCache model."""
    
    def __init__(self):
        super().__init__(IdempotencyCache)
    
    def get_by_key(
        self,
        db: Session,
        idempotency_key: str
    ) -> Optional[IdempotencyCache]:
        """
        Get idempotency cache by key.
        
        Args:
            db: Database session
            idempotency_key: Idempotency key
            
        Returns:
            IdempotencyCache or None
        """
        return db.query(IdempotencyCache).filter(
            IdempotencyCache.idempotency_key == idempotency_key
        ).first()
    
    def create_cache(
        self,
        db: Session,
        tenant_id: Union[str, int],
        idempotency_key: str,
        payload_hash: str,
        result_data: str
    ) -> IdempotencyCache:
        """
        Create idempotency cache entry.
        
        Args:
            db: Database session
            tenant_id: Tenant ID
            idempotency_key: Idempotency key
            payload_hash: Hash of payload
            result_data: JSON string of result data
            
        Returns:
            Created IdempotencyCache instance
        """
        from datetime import datetime
        
        tenant_id_int = _to_int(tenant_id)
        cache_obj = IdempotencyCache(
            idempotency_key=idempotency_key,
            tenant_id=tenant_id_int,
            payload_hash=payload_hash,
            result_data=result_data,
            created_at=datetime.utcnow().isoformat()
        )
        db.add(cache_obj)
        db.commit()
        db.refresh(cache_obj)
        return cache_obj
