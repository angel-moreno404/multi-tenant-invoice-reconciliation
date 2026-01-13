from fastapi import FastAPI
from strawberry.fastapi import GraphQLRouter

from app.core.database import Base, engine
from app.api.rest.main import api_router
from app.api.graphql.schema import schema

# Create database tables
Base.metadata.create_all(bind=engine)

# Create FastAPI app
app = FastAPI(
    title="Invoice Reconciliation API",
    description="Multi-tenant invoice reconciliation system",
    version="1.0.0"
)

# Include REST API router
app.include_router(api_router, prefix="/api/v1")

# Add GraphQL router
graphql_app = GraphQLRouter(schema)
app.include_router(graphql_app, prefix="/graphql")


@app.get("/")
def root():
    """Root endpoint."""
    return {
        "message": "Invoice Reconciliation API",
        "version": "1.0.0",
        "docs": "/docs",
        "graphql": "/graphql"
    }


@app.get("/health")
def health():
    """Health check endpoint."""
    return {"status": "healthy"}

