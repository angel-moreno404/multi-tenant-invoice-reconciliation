import strawberry
from typing import List
from datetime import datetime


@strawberry.type
class Tenant:
    """Tenant GraphQL type."""
    id: int
    name: str
    slug: str
    created_at: datetime
    updated_at: datetime
    
    @classmethod
    def from_model(cls, tenant):
        """Create from SQLAlchemy model."""
        return cls(
            id=tenant.id,
            name=tenant.name,
            slug=tenant.slug,
            created_at=tenant.created_at,
            updated_at=tenant.updated_at
        )

