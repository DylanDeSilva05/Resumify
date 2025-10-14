"""
Interview scheduling and management endpoints
"""
from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.api.deps import get_current_active_user
from app.models import User, Interview, Candidate, Company
from app.schemas.interview import (
    InterviewCreate, InterviewResponse, InterviewUpdate,
    InterviewListResponse, InterviewSchedulingRequest
)
from app.models.interview import InterviewType, InterviewStatus
from app.services.email_service import EmailService
from app.core.security import decrypt_password

router = APIRouter()


def get_company_email_service(company: Company) -> EmailService:
    """
    Get EmailService configured with company's SMTP settings

    IMPORTANT: Only returns a configured email service. Never returns a default/fallback service
    to prevent cross-company email usage.

    Args:
        company: Company object with SMTP settings

    Returns:
        EmailService: Configured email service with company's own SMTP settings

    Raises:
        ValueError: If company SMTP settings are not configured
    """
    import logging
    logger = logging.getLogger(__name__)

    if not company:
        logger.error("No company provided to get_company_email_service")
        raise ValueError("No company provided")

    if not company.smtp_enabled:
        logger.error(f"SMTP not enabled for company {company.id}")
        raise ValueError(f"SMTP not enabled for company {company.id}")

    if not all([company.smtp_host, company.smtp_port, company.smtp_username, company.smtp_password]):
        logger.error(f"SMTP settings incomplete for company {company.id}")
        raise ValueError(f"SMTP settings incomplete for company {company.id}")

    try:
        # Decrypt SMTP password
        smtp_password = decrypt_password(company.smtp_password)
        logger.info(f"Successfully decrypted SMTP password for company {company.id}")

        # Create email service with company's SMTP settings
        email_service = EmailService(
            smtp_host=company.smtp_host,
            smtp_port=company.smtp_port,
            smtp_user=company.smtp_username,
            smtp_password=smtp_password
        )

        if not email_service.enabled:
            logger.error(f"Email service not enabled after configuration for company {company.id}")
            raise ValueError(f"Email service configuration failed for company {company.id}")

        logger.info(f"Created email service for company {company.id}: enabled={email_service.enabled}")
        return email_service
    except Exception as e:
        # Never return unconfigured service - raise exception instead
        logger.error(f"Failed to create email service for company {company.id}: {str(e)}", exc_info=True)
        raise ValueError(f"Failed to create email service: {str(e)}")


@router.get("/", response_model=InterviewListResponse)
async def get_interviews(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    status: Optional[InterviewStatus] = Query(None),
    candidate_id: Optional[int] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get list of interviews with optional filtering

    Args:
        skip: Number of records to skip
        limit: Maximum number of records to return
        status: Optional status filter
        candidate_id: Optional candidate ID filter
        db: Database session
        current_user: Current authenticated user

    Returns:
        InterviewListResponse: Paginated interviews list
    """
    from sqlalchemy.orm import joinedload

    query = db.query(Interview).options(joinedload(Interview.candidate))

    # Apply filters
    if status:
        query = query.filter(Interview.status == status)
    if candidate_id:
        query = query.filter(Interview.candidate_id == candidate_id)

    # Get total count for pagination
    total = query.count()

    # Apply pagination and ordering
    interviews = query.order_by(Interview.scheduled_datetime.asc()).offset(skip).limit(limit).all()

    return InterviewListResponse(
        interviews=interviews,
        total=total,
        page=(skip // limit) + 1,
        pages=(total + limit - 1) // limit
    )


@router.post("/", response_model=InterviewResponse, status_code=status.HTTP_201_CREATED)
async def create_interview(
    interview_create: InterviewCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Schedule a new interview

    Args:
        interview_create: Interview creation data
        db: Database session
        current_user: Current authenticated user

    Returns:
        InterviewResponse: Created interview information
    """
    # Verify candidate exists
    candidate = db.query(Candidate).filter(Candidate.id == interview_create.candidate_id).first()
    if not candidate:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Candidate not found"
        )

    interview = Interview(
        company_id=candidate.company_id,  # Use candidate's company_id
        candidate_id=interview_create.candidate_id,
        scheduled_by=current_user.id,
        interview_type=interview_create.interview_type,
        scheduled_datetime=interview_create.scheduled_datetime,
        duration_minutes=interview_create.duration_minutes,
        location=interview_create.location,
        meeting_link=interview_create.meeting_link,
        position=interview_create.position,
        interviewer_name=interview_create.interviewer_name,
        interviewer_email=interview_create.interviewer_email
    )

    db.add(interview)
    db.commit()
    db.refresh(interview)

    return interview


@router.post("/schedule")
async def schedule_interview_simple(
    request: InterviewSchedulingRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Simple interview scheduling endpoint (for frontend compatibility)

    Args:
        request: Interview scheduling request
        db: Database session
        current_user: Current authenticated user

    Returns:
        Success message with interview details
    """
    # Verify candidate exists and load related data
    from sqlalchemy.orm import joinedload
    from app.models.cv_analysis import CVAnalysis

    candidate = db.query(Candidate).filter(Candidate.id == request.candidate_id).first()
    if not candidate:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Candidate not found"
        )

    # Get the job title from the candidate's CV analysis
    cv_analysis = db.query(CVAnalysis).options(
        joinedload(CVAnalysis.job_posting)
    ).filter(
        CVAnalysis.candidate_id == request.candidate_id
    ).order_by(CVAnalysis.created_at.desc()).first()

    job_title = "the position you applied for"  # Default fallback
    if cv_analysis and cv_analysis.job_posting:
        job_title = cv_analysis.job_posting.title

    # Parse datetime
    try:
        scheduled_datetime = datetime.fromisoformat(request.datetime.replace('Z', '+00:00'))
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid datetime format. Use ISO format."
        )

    # Map interview type
    type_mapping = {
        "video": InterviewType.VIDEO,
        "phone": InterviewType.PHONE,
        "in-person": InterviewType.IN_PERSON
    }
    interview_type = type_mapping.get(request.type)
    if not interview_type:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid interview type: {request.type}"
        )

    # Create interview
    interview = Interview(
        company_id=candidate.company_id,  # Use candidate's company_id
        candidate_id=request.candidate_id,
        scheduled_by=current_user.id,
        interview_type=interview_type,
        scheduled_datetime=scheduled_datetime,
        duration_minutes=60,  # Default duration
        interviewer_name=current_user.full_name,
        interviewer_email=current_user.email,
        position=job_title  # Store the actual job title
    )

    # CRITICAL: Verify USER'S SMTP configuration BEFORE creating interview record
    import logging
    logger = logging.getLogger(__name__)

    # Use current user's email settings (not company-level)
    if not current_user.smtp_enabled:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email settings not configured. Please enable and configure SMTP settings in Email Settings before scheduling interviews."
        )

    if not all([current_user.smtp_host, current_user.smtp_port, current_user.smtp_username, current_user.smtp_password]):
        missing_fields = []
        if not current_user.smtp_host: missing_fields.append("SMTP Host")
        if not current_user.smtp_port: missing_fields.append("SMTP Port")
        if not current_user.smtp_username: missing_fields.append("SMTP Username")
        if not current_user.smtp_password: missing_fields.append("SMTP Password")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Email settings incomplete. Missing: {', '.join(missing_fields)}. Please configure all SMTP settings in Email Settings."
        )

    # Decrypt user's SMTP password
    try:
        smtp_password = decrypt_password(current_user.smtp_password)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to decrypt SMTP password"
        )

    # Create email service with user's SMTP settings
    email_service = EmailService(
        smtp_host=current_user.smtp_host,
        smtp_port=current_user.smtp_port,
        smtp_user=current_user.smtp_username,
        smtp_password=smtp_password
    )

    if not email_service.enabled:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email service configuration failed. Please verify your SMTP settings."
        )

    # Only create interview AFTER email configuration is verified
    db.add(interview)
    db.commit()
    db.refresh(interview)

    # Send interview invitation email
    email_result = email_service.send_interview_invitation(
        candidate_name=candidate.name,
        candidate_email=candidate.email,
        job_title=job_title,  # Use the actual job title
        interview_datetime=scheduled_datetime,
        interview_type=request.type,
        interviewer_name=current_user.full_name,
        interviewer_email=current_user.email,
        meeting_link=interview.meeting_link,
        location=interview.location
    )

    return {
        "message": f"Interview scheduled successfully with {candidate.name}",
        "interview_id": interview.id,
        "candidate": candidate.name,
        "datetime": scheduled_datetime.isoformat(),
        "type": request.type,
        "email_sent": email_result.get("sent", False),
        "email_preview": {
            "subject": email_result.get("subject"),
            "body": email_result.get("body")
        }
    }


@router.post("/preview-email")
async def preview_interview_email(
    request: InterviewSchedulingRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Preview interview invitation email without scheduling

    Args:
        request: Interview scheduling request
        db: Database session
        current_user: Current authenticated user

    Returns:
        Email preview with subject and body
    """
    # Verify candidate exists and load related data
    from sqlalchemy.orm import joinedload
    from app.models.cv_analysis import CVAnalysis

    candidate = db.query(Candidate).filter(Candidate.id == request.candidate_id).first()
    if not candidate:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Candidate not found"
        )

    # Get the job title from the candidate's CV analysis
    cv_analysis = db.query(CVAnalysis).options(
        joinedload(CVAnalysis.job_posting)
    ).filter(
        CVAnalysis.candidate_id == request.candidate_id
    ).order_by(CVAnalysis.created_at.desc()).first()

    job_title = "the position you applied for"  # Default fallback
    if cv_analysis and cv_analysis.job_posting:
        job_title = cv_analysis.job_posting.title

    # Parse datetime
    try:
        scheduled_datetime = datetime.fromisoformat(request.datetime.replace('Z', '+00:00'))
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid datetime format. Use ISO format."
        )

    # Get company and create email service with company's SMTP settings
    company = db.query(Company).filter(Company.id == candidate.company_id).first()
    email_service = get_company_email_service(company)

    # Generate email preview
    email_content = email_service.generate_interview_email(
        candidate_name=candidate.name,
        candidate_email=candidate.email,
        job_title=job_title,  # Use the actual job title
        interview_datetime=scheduled_datetime,
        interview_type=request.type,
        interviewer_name=current_user.full_name
    )

    # Update email body to include interviewer contact info in preview
    if current_user.email:
        email_content["body"] = email_content["body"].replace(
            "Best regards,\nHR Team",
            f"Best regards,\n{current_user.full_name}\n{current_user.email}"
        )

    return {
        "preview": True,
        "subject": email_content["subject"],
        "body": email_content["body"],
        "to": email_content["to"],
        "to_name": email_content["to_name"],
        "from": f"{current_user.full_name} <{current_user.email}>"
    }


@router.get("/{interview_id}", response_model=InterviewResponse)
async def get_interview(
    interview_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get interview by ID

    Args:
        interview_id: Interview ID
        db: Database session
        current_user: Current authenticated user

    Returns:
        InterviewResponse: Interview information
    """
    interview = db.query(Interview).filter(Interview.id == interview_id).first()
    if not interview:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Interview not found"
        )

    return interview


@router.put("/{interview_id}", response_model=InterviewResponse)
async def update_interview(
    interview_id: int,
    interview_update: InterviewUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Update interview by ID

    Args:
        interview_id: Interview ID to update
        interview_update: Update data
        db: Database session
        current_user: Current authenticated user

    Returns:
        InterviewResponse: Updated interview information
    """
    interview = db.query(Interview).filter(Interview.id == interview_id).first()
    if not interview:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Interview not found"
        )

    # Update fields
    update_data = interview_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(interview, field, value)

    db.commit()
    db.refresh(interview)

    return interview


@router.delete("/{interview_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_interview(
    interview_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Cancel/delete interview by ID

    Args:
        interview_id: Interview ID to delete
        db: Database session
        current_user: Current authenticated user
    """
    interview = db.query(Interview).filter(Interview.id == interview_id).first()
    if not interview:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Interview not found"
        )

    db.delete(interview)
    db.commit()


@router.get("/candidate/{candidate_id}")
async def get_candidate_interviews(
    candidate_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get all interviews for a specific candidate

    Args:
        candidate_id: Candidate ID
        db: Database session
        current_user: Current authenticated user

    Returns:
        List of interviews for the candidate
    """
    # Verify candidate exists
    candidate = db.query(Candidate).filter(Candidate.id == candidate_id).first()
    if not candidate:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Candidate not found"
        )

    interviews = db.query(Interview).filter(
        Interview.candidate_id == candidate_id
    ).order_by(Interview.scheduled_datetime.asc()).all()

    return interviews