"""
Company schemas for request/response validation
"""
from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime


class CompanyBase(BaseModel):
    """Base company schema with common fields"""
    company_name: str = Field(..., min_length=1, max_length=255, description="Company name")
    contact_email: EmailStr = Field(..., description="Primary contact email")
    contact_phone: Optional[str] = Field(None, max_length=50)
    address: Optional[str] = None
    city: Optional[str] = Field(None, max_length=100)
    state: Optional[str] = Field(None, max_length=100)
    country: Optional[str] = Field(None, max_length=100)
    postal_code: Optional[str] = Field(None, max_length=20)


class CompanyCreate(CompanyBase):
    """Schema for creating a new company"""
    subscription_tier: Optional[str] = Field("basic", description="Subscription tier")
    max_users: Optional[int] = Field(5, ge=1, description="Maximum users allowed")
    max_cv_uploads_monthly: Optional[int] = Field(100, ge=0, description="Monthly CV upload limit")


class CompanyUpdate(BaseModel):
    """Schema for updating a company"""
    company_name: Optional[str] = Field(None, min_length=1, max_length=255)
    contact_email: Optional[EmailStr] = None
    contact_phone: Optional[str] = Field(None, max_length=50)
    address: Optional[str] = None
    city: Optional[str] = Field(None, max_length=100)
    state: Optional[str] = Field(None, max_length=100)
    country: Optional[str] = Field(None, max_length=100)
    postal_code: Optional[str] = Field(None, max_length=20)
    is_active: Optional[bool] = None
    subscription_tier: Optional[str] = None
    max_users: Optional[int] = Field(None, ge=1)
    max_cv_uploads_monthly: Optional[int] = Field(None, ge=0)


class CompanyResponse(CompanyBase):
    """Schema for company response"""
    id: int
    is_active: bool
    subscription_tier: str
    max_users: int
    max_cv_uploads_monthly: int
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


class CompanyListResponse(BaseModel):
    """Schema for paginated company list"""
    companies: list[CompanyResponse]
    total: int
    page: int
    pages: int


class CompanyStats(BaseModel):
    """Schema for company statistics"""
    id: int
    company_name: str
    total_users: int
    total_candidates: int
    total_job_postings: int
    total_cv_analyses: int
    is_active: bool
    subscription_tier: str

    class Config:
        from_attributes = True
