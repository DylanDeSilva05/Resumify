"""
Company management endpoints
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.core.database import get_db
from app.api.deps import get_current_active_user
from app.models import User, Company, Candidate, JobPosting, CVAnalysis, UserRole
from app.schemas.company import (
    CompanyCreate,
    CompanyUpdate,
    CompanyResponse,
    CompanyListResponse,
    CompanyStats
)

router = APIRouter()


def require_super_admin(current_user: User):
    """Dependency to ensure user is a super admin"""
    if current_user.role != UserRole.SUPER_ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only super admins can perform this action"
        )
    return current_user


def get_user_company(current_user: User, db: Session):
    """Get the user's company or raise error if not found"""
    if current_user.role == UserRole.SUPER_ADMIN:
        return None  # Super admins don't have a company

    if not current_user.company_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User is not associated with any company"
        )

    company = db.query(Company).filter(Company.id == current_user.company_id).first()
    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Company not found"
        )

    return company


@router.post("/", response_model=CompanyResponse, status_code=status.HTTP_201_CREATED)
async def create_company(
    company_data: CompanyCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    _: User = Depends(require_super_admin)
):
    """
    Create a new company (Super Admin only)

    Args:
        company_data: Company creation data
        db: Database session
        current_user: Current authenticated user

    Returns:
        CompanyResponse: Created company information
    """
    # Check if company name already exists
    existing = db.query(Company).filter(
        Company.company_name == company_data.company_name
    ).first()

    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Company with name '{company_data.company_name}' already exists"
        )

    # Create new company
    new_company = Company(**company_data.dict())
    db.add(new_company)
    db.commit()
    db.refresh(new_company)

    return new_company


@router.get("/", response_model=CompanyListResponse)
async def list_companies(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    is_active: Optional[bool] = Query(None),
    search: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    _: User = Depends(require_super_admin)
):
    """
    List all companies (Super Admin only)

    Args:
        skip: Number of records to skip
        limit: Maximum number of records to return
        is_active: Filter by active status
        search: Search by company name
        db: Database session
        current_user: Current authenticated user

    Returns:
        CompanyListResponse: Paginated list of companies
    """
    query = db.query(Company)

    # Apply filters
    if is_active is not None:
        query = query.filter(Company.is_active == is_active)

    if search:
        query = query.filter(Company.company_name.icontains(search))

    # Get total count
    total = query.count()

    # Apply pagination
    companies = query.offset(skip).limit(limit).all()

    return CompanyListResponse(
        companies=companies,
        total=total,
        page=(skip // limit) + 1,
        pages=(total + limit - 1) // limit
    )


@router.get("/my-company", response_model=CompanyResponse)
async def get_my_company(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get current user's company information

    Args:
        db: Database session
        current_user: Current authenticated user

    Returns:
        CompanyResponse: User's company information
    """
    company = get_user_company(current_user, db)

    if not company:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User is not associated with any company"
        )

    return company


@router.get("/{company_id}", response_model=CompanyResponse)
async def get_company(
    company_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get company by ID

    Super admins can view any company.
    Regular users can only view their own company.

    Args:
        company_id: Company ID
        db: Database session
        current_user: Current authenticated user

    Returns:
        CompanyResponse: Company information
    """
    company = db.query(Company).filter(Company.id == company_id).first()

    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Company not found"
        )

    # Authorization check
    if current_user.role != UserRole.SUPER_ADMIN:
        if current_user.company_id != company_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only view your own company"
            )

    return company


@router.put("/{company_id}", response_model=CompanyResponse)
async def update_company(
    company_id: int,
    company_update: CompanyUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Update company information

    Super admins can update any company.
    Company admins can update their own company (limited fields).

    Args:
        company_id: Company ID
        company_update: Update data
        db: Database session
        current_user: Current authenticated user

    Returns:
        CompanyResponse: Updated company information
    """
    company = db.query(Company).filter(Company.id == company_id).first()

    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Company not found"
        )

    # Authorization check
    is_super_admin = current_user.role == UserRole.SUPER_ADMIN
    is_company_admin = (
        current_user.role == UserRole.COMPANY_ADMIN and
        current_user.company_id == company_id
    )

    if not (is_super_admin or is_company_admin):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to update this company"
        )

    # Company admins can only update certain fields
    if is_company_admin and not is_super_admin:
        restricted_fields = {'is_active', 'subscription_tier', 'max_users', 'max_cv_uploads_monthly'}
        update_data = company_update.dict(exclude_unset=True)

        if any(field in update_data for field in restricted_fields):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Company admins cannot modify subscription settings"
            )

    # Update fields
    update_data = company_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(company, field, value)

    db.commit()
    db.refresh(company)

    return company


@router.delete("/{company_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_company(
    company_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    _: User = Depends(require_super_admin)
):
    """
    Delete company (Super Admin only)

    WARNING: This will cascade delete all associated data:
    - Users
    - Candidates
    - Job Postings
    - CV Analyses
    - Interviews

    Args:
        company_id: Company ID to delete
        db: Database session
        current_user: Current authenticated user
    """
    company = db.query(Company).filter(Company.id == company_id).first()

    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Company not found"
        )

    # Delete the company (cascades to all related records)
    db.delete(company)
    db.commit()


@router.get("/{company_id}/stats", response_model=CompanyStats)
async def get_company_stats(
    company_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get company statistics

    Args:
        company_id: Company ID
        db: Database session
        current_user: Current authenticated user

    Returns:
        CompanyStats: Company statistics
    """
    company = db.query(Company).filter(Company.id == company_id).first()

    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Company not found"
        )

    # Authorization check
    if current_user.role != UserRole.SUPER_ADMIN:
        if current_user.company_id != company_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only view your own company statistics"
            )

    # Get statistics
    total_users = db.query(func.count(User.id)).filter(User.company_id == company_id).scalar()
    total_candidates = db.query(func.count(Candidate.id)).filter(Candidate.company_id == company_id).scalar()
    total_job_postings = db.query(func.count(JobPosting.id)).filter(JobPosting.company_id == company_id).scalar()
    total_cv_analyses = db.query(func.count(CVAnalysis.id)).filter(CVAnalysis.company_id == company_id).scalar()

    return CompanyStats(
        id=company.id,
        company_name=company.company_name,
        total_users=total_users,
        total_candidates=total_candidates,
        total_job_postings=total_job_postings,
        total_cv_analyses=total_cv_analyses,
        is_active=company.is_active,
        subscription_tier=company.subscription_tier
    )
