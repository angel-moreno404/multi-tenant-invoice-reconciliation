from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import verify_tenant
from app.models.tenant import Tenant
from app.services.reconciliation_service import ReconciliationService
from app.schemas.reconciliation import (
    ReconciliationRequest,
    ReconciliationResponse,
    ReconciliationMatchResponse,
    ConfirmMatchRequest,
    ExplainReconciliationRequest,
    ExplainReconciliationResponse
)

router = APIRouter(prefix="/tenants/{tenant_id}/reconcile", tags=["reconciliation"])


@router.post("", response_model=ReconciliationResponse)
def reconcile(
    tenant_id: str,
    request: ReconciliationRequest,
    db: Session = Depends(get_db),
    tenant: Tenant = Depends(verify_tenant)
):
    """
    Run reconciliation for a tenant.
    """
    service = ReconciliationService()
    matches = service.reconcile(db, tenant_id)
    
    return ReconciliationResponse(
        matches=[ReconciliationMatchResponse.model_validate(m) for m in matches],
        total_matches=len(matches)
    )


@router.post("/matches/{match_id}/confirm")
def confirm_match(
    tenant_id: str,
    match_id: int,
    request: ConfirmMatchRequest,
    db: Session = Depends(get_db),
    tenant: Tenant = Depends(verify_tenant)
):
    """
    Confirm a reconciliation match.
    """
    service = ReconciliationService()
    match = service.confirm_match(db, tenant_id, match_id)
    
    if not match:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Match {match_id} not found"
        )
    
    return ReconciliationMatchResponse.model_validate(match)


@router.get("/explain", response_model=ExplainReconciliationResponse)
async def explain_reconciliation(
    tenant_id: str,
    match_id: int,
    db: Session = Depends(get_db),
    tenant: Tenant = Depends(verify_tenant)
):
    """
    Generate explanation for a reconciliation match.
    """
    service = ReconciliationService()
    result = await service.explain_match(db, tenant_id, match_id)
    
    return ExplainReconciliationResponse(
        explanation=result["explanation"],
        source=result["source"]
    )

