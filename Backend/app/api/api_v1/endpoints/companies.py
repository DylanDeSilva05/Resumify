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
    CompanyStats,
    EmailSettingsUpdate,
    EmailSettingsResponse,
    EmailSettingsTest
)
from app.services.email_service import EmailService
from app.core.security import encrypt_password, decrypt_password

router = APIRouter()


def require_super_admin(current_user: User = Depends(get_current_active_user)):
    """Dependency to ensure user is a super admin"""
    if current_user.role != UserRole.SUPER_ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only super admins can perform this action"
        )
    return None  # Return None instead of user to avoid duplicate dependencies


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
    _: None = Depends(require_super_admin)
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
    _: None = Depends(require_super_admin)
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
    _: None = Depends(require_super_admin)
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


@router.get("/my-company/email-settings", response_model=EmailSettingsResponse)
async def get_email_settings(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get current user's company email settings

    Args:
        db: Database session
        current_user: Current authenticated user

    Returns:
        EmailSettingsResponse: Email settings (password hidden)
    """
    # Get company email settings
    company = get_user_company(current_user, db)

    if not company:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User is not associated with any company"
        )

    return EmailSettingsResponse(
        smtp_host=company.smtp_host,
        smtp_port=company.smtp_port or 587,
        smtp_username=company.smtp_username,
        smtp_from_name=company.smtp_from_name,
        smtp_enabled=company.smtp_enabled or False,
        password_configured=bool(company.smtp_password)
    )


@router.put("/my-company/email-settings", response_model=EmailSettingsResponse)
async def update_email_settings(
    settings: EmailSettingsUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Update company's email settings

    Args:
        settings: Email settings to update
        db: Database session
        current_user: Current authenticated user

    Returns:
        EmailSettingsResponse: Updated email settings
    """
    # Only company admins can update email settings
    if current_user.role not in [UserRole.SUPER_ADMIN, UserRole.COMPANY_ADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only company admins can update email settings"
        )

    # Get company
    company = get_user_company(current_user, db)

    if not company:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User is not associated with any company"
        )

    # Update company email settings
    update_data = settings.dict(exclude_unset=True)

    for field, value in update_data.items():
        if field == "smtp_password" and value:
            # Encrypt password before storing
            setattr(company, field, encrypt_password(value))
        else:
            setattr(company, field, value)

    db.commit()
    db.refresh(company)

    return EmailSettingsResponse(
        smtp_host=company.smtp_host,
        smtp_port=company.smtp_port or 587,
        smtp_username=company.smtp_username,
        smtp_from_name=company.smtp_from_name,
        smtp_enabled=company.smtp_enabled or False,
        password_configured=bool(company.smtp_password)
    )


@router.post("/my-company/email-settings/test")
async def test_email_settings(
    test_data: EmailSettingsTest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Test company email configuration by sending a test email

    Args:
        test_data: Test email request
        db: Database session
        current_user: Current authenticated user

    Returns:
        dict: Test result
    """
    # Only company admins can test email settings
    if current_user.role not in [UserRole.SUPER_ADMIN, UserRole.COMPANY_ADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only company admins can test email settings"
        )

    company = get_user_company(current_user, db)

    if not company:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User is not associated with any company"
        )

    # Check if email settings are configured
    if not all([company.smtp_host, company.smtp_port, company.smtp_username, company.smtp_password]):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email settings not fully configured. Please configure all SMTP settings first."
        )

    # Decrypt password
    try:
        smtp_password = decrypt_password(company.smtp_password)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to decrypt SMTP password"
        )

    # Create email service with company settings
    email_service = EmailService(
        smtp_host=company.smtp_host,
        smtp_port=company.smtp_port,
        smtp_user=company.smtp_username,
        smtp_password=smtp_password
    )

    # Send test email
    try:
        success = email_service.send_email(
            to_email=test_data.test_email,
            subject="Test Email from Resumify",
            body=f"""Hello,

This is a test email from your Resumify account to verify your email configuration is working correctly.

Company: {company.company_name}
Sent by: {current_user.full_name}

If you received this email, your email settings are configured correctly!

Best regards,
Resumify Team
""",
            from_name=company.smtp_from_name or company.company_name
        )

        if success:
            return {
                "success": True,
                "message": f"Test email sent successfully to {test_data.test_email}"
            }
        else:
            return {
                "success": False,
                "message": "Failed to send test email. Please check your SMTP settings."
            }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to send test email: {str(e)}"
        )
