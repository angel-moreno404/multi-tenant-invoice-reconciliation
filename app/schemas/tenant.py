from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class TenantBase(BaseModel):
    """Base schema for Tenant."""
    name: str
    slug: str


class TenantCreate(TenantBase):
    """Schema for creating a Tenant."""
    pass


class TenantUpdate(BaseModel):
    """Schema for updating a Tenant."""
    name: Optional[str] = None
    slug: Optional[str] = None


class TenantResponse(TenantBase):
    """Schema for Tenant response."""
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

