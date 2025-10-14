"""
CV Upload and Processing endpoints
"""
import os
import logging
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.api.deps import get_current_active_user
from app.models import User, Candidate
from app.schemas.candidate import CandidateResponse
from app.services.cv_parser import CVParser
from app.utils.file_utils import is_allowed_file, get_safe_filename, ensure_upload_directory
from app.core.config import settings

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/cv", response_model=List[CandidateResponse])
async def upload_cvs(
    files: List[UploadFile] = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Upload and parse CV files

    Args:
        files: List of CV files to upload
        db: Database session
        current_user: Current authenticated user

    Returns:
        List[CandidateResponse]: List of created candidate records
    """
    if not files:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No files provided"
        )

    # Ensure upload directory exists
    upload_dir = ensure_upload_directory()
    cv_parser = CVParser()
    candidates = []

    for file in files:
        try:
            # Validate file
            if not file.filename:
                logger.warning("Skipping file with no filename")
                continue

            if not is_allowed_file(file.filename):
                logger.warning(f"Skipping unsupported file: {file.filename}")
                continue

            # Save file
            safe_filename = get_safe_filename(file.filename)
            file_path = upload_dir / safe_filename

            # Write file content
            content = await file.read()
            with open(file_path, "wb") as f:
                f.write(content)

            logger.info(f"Saved file: {file_path}")

            # Parse CV
            parsed_data = cv_parser.parse_cv_file(str(file_path))

            # Extract candidate name
            candidate_name = cv_parser.extract_candidate_name(parsed_data.get('raw_text', ''))

            # Create candidate record
            candidate = Candidate(
                company_id=current_user.company_id,  # Multi-tenant: associate with user's company
                name=candidate_name,
                email=parsed_data.get('personal_info', {}).get('email'),
                phone=parsed_data.get('personal_info', {}).get('phone'),
                original_filename=file.filename,
                file_path=str(file_path),
                file_size=len(content),
                raw_text=parsed_data.get('raw_text'),
                personal_info=parsed_data.get('personal_info'),
                education=parsed_data.get('education'),
                work_experience=parsed_data.get('work_experience'),
                skills=parsed_data.get('skills'),
                certifications=parsed_data.get('certifications'),
                languages=parsed_data.get('languages'),
                total_experience_years=parsed_data.get('total_experience_years', 0.0),
                parsing_status=parsed_data.get('parsing_status', 'completed'),
                parsing_error=parsed_data.get('parsing_error')
            )

            db.add(candidate)
            db.flush()  # Get the ID
            candidates.append(candidate)

            logger.info(f"Created candidate: {candidate.name} (ID: {candidate.id})")

        except Exception as e:
            logger.error(f"Failed to process file {file.filename}: {str(e)}")
            # Continue with other files instead of failing completely
            continue

    if not candidates:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No valid CV files could be processed"
        )

    db.commit()

    logger.info(f"Successfully processed {len(candidates)} CV files")
    return candidates


@router.delete("/cv/{candidate_id}")
async def delete_uploaded_cv(
    candidate_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Delete uploaded CV and associated file

    Args:
        candidate_id: ID of candidate to delete
        db: Database session
        current_user: Current authenticated user
    """
    candidate = db.query(Candidate).filter(Candidate.id == candidate_id).first()
    if not candidate:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Candidate not found"
        )

    # Delete physical file
    try:
        if os.path.exists(candidate.file_path):
            os.remove(candidate.file_path)
            logger.info(f"Deleted file: {candidate.file_path}")
    except Exception as e:
        logger.warning(f"Failed to delete file {candidate.file_path}: {str(e)}")

    # Delete database record
    db.delete(candidate)
    db.commit()

    return {"message": "CV deleted successfully"}