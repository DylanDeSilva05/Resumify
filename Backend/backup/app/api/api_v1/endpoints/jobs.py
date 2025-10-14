"""
Job posting management endpoints
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.api.deps import get_current_active_user, get_current_hr_manager
from app.models import User, JobPosting
from app.schemas.job_posting import (
    JobPostingCreate, JobPostingResponse, JobPostingUpdate,
    JobPostingListResponse, ParsedJobRequirements
)
from app.services.nlp_service import NLPService

router = APIRouter()
nlp_service = NLPService()


@router.get("/", response_model=JobPostingListResponse)
async def get_job_postings(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    title: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get list of job postings with optional filtering

    Args:
        skip: Number of records to skip
        limit: Maximum number of records to return
        title: Optional title filter
        status: Optional status filter
        db: Database session
        current_user: Current authenticated user

    Returns:
        JobPostingListResponse: Paginated job postings list
    """
    query = db.query(JobPosting)

    # Apply filters
    if title:
        query = query.filter(JobPosting.title.icontains(title))
    if status:
        query = query.filter(JobPosting.status == status)

    # Get total count for pagination
    total = query.count()

    # Apply pagination and ordering
    job_postings = query.order_by(JobPosting.created_at.desc()).offset(skip).limit(limit).all()

    return JobPostingListResponse(
        job_postings=job_postings,
        total=total,
        page=(skip // limit) + 1,
        pages=(total + limit - 1) // limit
    )


@router.post("/", response_model=JobPostingResponse, status_code=status.HTTP_201_CREATED)
async def create_job_posting(
    job_create: JobPostingCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_hr_manager)
):
    """
    Create a new job posting

    Args:
        job_create: Job posting creation data
        db: Database session
        current_user: Current HR manager user

    Returns:
        JobPostingResponse: Created job posting information
    """
    # If no structured requirements provided, try to parse from description
    if not job_create.required_skills and not job_create.preferred_skills:
        try:
            parsed = nlp_service.parse_job_requirements(job_create.description)
            job_create.required_skills = parsed.required_skills
            job_create.preferred_skills = parsed.preferred_skills
            job_create.education_requirements = parsed.education_requirements
            job_create.experience_requirements = parsed.experience_requirements
            job_create.soft_skills = parsed.soft_skills
            job_create.min_experience_years = parsed.min_experience_years
            job_create.max_experience_years = parsed.max_experience_years
        except Exception:
            # If parsing fails, continue with manual requirements
            pass

    job_posting = JobPosting(
        company_id=current_user.company_id,  # Multi-tenant: associate with user's company
        title=job_create.title,
        description=job_create.description,
        required_skills=job_create.required_skills,
        preferred_skills=job_create.preferred_skills,
        education_requirements=job_create.education_requirements,
        experience_requirements=job_create.experience_requirements,
        soft_skills=job_create.soft_skills,
        location=job_create.location,
        work_type=job_create.work_type,
        min_experience_years=job_create.min_experience_years,
        max_experience_years=job_create.max_experience_years,
        matching_weights=job_create.matching_weights,
        created_by=current_user.id,
        status="active"
    )

    db.add(job_posting)
    db.commit()
    db.refresh(job_posting)

    return job_posting


@router.get("/{job_id}", response_model=JobPostingResponse)
async def get_job_posting(
    job_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get job posting by ID

    Args:
        job_id: Job posting ID
        db: Database session
        current_user: Current authenticated user

    Returns:
        JobPostingResponse: Job posting information
    """
    job_posting = db.query(JobPosting).filter(JobPosting.id == job_id).first()
    if not job_posting:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job posting not found"
        )

    return job_posting


@router.put("/{job_id}", response_model=JobPostingResponse)
async def update_job_posting(
    job_id: int,
    job_update: JobPostingUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_hr_manager)
):
    """
    Update job posting by ID

    Args:
        job_id: Job posting ID to update
        job_update: Update data
        db: Database session
        current_user: Current HR manager user

    Returns:
        JobPostingResponse: Updated job posting information
    """
    job_posting = db.query(JobPosting).filter(JobPosting.id == job_id).first()
    if not job_posting:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job posting not found"
        )

    # Update fields
    update_data = job_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(job_posting, field, value)

    db.commit()
    db.refresh(job_posting)

    return job_posting


@router.delete("/{job_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_job_posting(
    job_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_hr_manager)
):
    """
    Delete job posting by ID

    Args:
        job_id: Job posting ID to delete
        db: Database session
        current_user: Current HR manager user
    """
    job_posting = db.query(JobPosting).filter(JobPosting.id == job_id).first()
    if not job_posting:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job posting not found"
        )

    # Delete associated CV analysis records first
    from app.models import CVAnalysis
    db.query(CVAnalysis).filter(CVAnalysis.job_posting_id == job_id).delete()

    # Delete the job posting
    db.delete(job_posting)
    db.commit()


@router.get("/{job_id}/analyses")
async def get_job_analyses(
    job_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get all CV analyses for a specific job posting

    Args:
        job_id: Job posting ID
        db: Database session
        current_user: Current authenticated user

    Returns:
        List of CV analyses for the job posting
    """
    job_posting = db.query(JobPosting).filter(JobPosting.id == job_id).first()
    if not job_posting:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job posting not found"
        )

    return job_posting.cv_analyses