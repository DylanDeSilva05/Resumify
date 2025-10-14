"""
Candidate management endpoints
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.api.deps import get_current_active_user
from app.models import User, Candidate
from app.schemas.candidate import CandidateResponse, CandidateListResponse, CandidateUpdate

router = APIRouter()


@router.get("/", response_model=CandidateListResponse)
async def get_candidates(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    name: Optional[str] = Query(None),
    parsing_status: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get list of candidates with optional filtering
    (Filtered by user's company for data isolation)

    Args:
        skip: Number of records to skip
        limit: Maximum number of records to return
        name: Optional name filter
        parsing_status: Optional parsing status filter
        db: Database session
        current_user: Current authenticated user

    Returns:
        CandidateListResponse: Paginated candidates list
    """
    query = db.query(Candidate)

    # MULTI-TENANT FILTER: Only show candidates from user's company
    if current_user.company_id:
        query = query.filter(Candidate.company_id == current_user.company_id)

    # Apply filters
    if name:
        query = query.filter(Candidate.name.icontains(name))
    if parsing_status:
        query = query.filter(Candidate.parsing_status == parsing_status)

    # Get total count for pagination
    total = query.count()

    # Apply pagination
    candidates = query.offset(skip).limit(limit).all()

    return CandidateListResponse(
        candidates=candidates,
        total=total,
        page=(skip // limit) + 1,
        pages=(total + limit - 1) // limit
    )


@router.get("/{candidate_id}", response_model=CandidateResponse)
async def get_candidate(
    candidate_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get candidate by ID
    (Company-scoped for data isolation)

    Args:
        candidate_id: Candidate ID
        db: Database session
        current_user: Current authenticated user

    Returns:
        CandidateResponse: Candidate information
    """
    query = db.query(Candidate).filter(Candidate.id == candidate_id)

    # MULTI-TENANT FILTER: Only allow access to user's company candidates
    if current_user.company_id:
        query = query.filter(Candidate.company_id == current_user.company_id)

    candidate = query.first()

    if not candidate:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Candidate not found"
        )

    return candidate


@router.put("/{candidate_id}", response_model=CandidateResponse)
async def update_candidate(
    candidate_id: int,
    candidate_update: CandidateUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Update candidate information

    Args:
        candidate_id: Candidate ID to update
        candidate_update: Update data
        db: Database session
        current_user: Current authenticated user

    Returns:
        CandidateResponse: Updated candidate information
    """
    candidate = db.query(Candidate).filter(Candidate.id == candidate_id).first()
    if not candidate:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Candidate not found"
        )

    # Update fields
    update_data = candidate_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(candidate, field, value)

    db.commit()
    db.refresh(candidate)

    return candidate


@router.delete("/{candidate_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_candidate(
    candidate_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Delete candidate by ID

    Args:
        candidate_id: Candidate ID to delete
        db: Database session
        current_user: Current authenticated user
    """
    candidate = db.query(Candidate).filter(Candidate.id == candidate_id).first()
    if not candidate:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Candidate not found"
        )

    # Delete associated CV analysis records first
    from app.models import CVAnalysis
    db.query(CVAnalysis).filter(CVAnalysis.candidate_id == candidate_id).delete()

    # Delete the candidate
    db.delete(candidate)
    db.commit()


@router.get("/{candidate_id}/analyses")
async def get_candidate_analyses(
    candidate_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get all CV analyses for a specific candidate

    Args:
        candidate_id: Candidate ID
        db: Database session
        current_user: Current authenticated user

    Returns:
        List of CV analyses for the candidate
    """
    candidate = db.query(Candidate).filter(Candidate.id == candidate_id).first()
    if not candidate:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Candidate not found"
        )

    return candidate.cv_analyses