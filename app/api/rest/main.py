from fastapi import APIRouter

from app.api.rest.routes import tenants, invoices, bank_transactions, reconciliation

# Create main router
api_router = APIRouter()

# Include all route routers
api_router.include_router(tenants.router)
api_router.include_router(invoices.router)
api_router.include_router(bank_transactions.router)
api_router.include_router(reconciliation.router)

