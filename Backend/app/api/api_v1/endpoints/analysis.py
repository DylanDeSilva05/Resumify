"""
CV Analysis endpoints for CV upload, parsing, and candidate matching
"""
import os
import logging
from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.config import settings
from app.core.exceptions import FileProcessingError, ValidationError
from app.api.deps import get_current_active_user
from app.models import User, Candidate, JobPosting, CVAnalysis
from app.schemas.cv_analysis import (
    CVUploadRequest, AnalysisResults, CandidateWithAnalysis, CVAnalysisResponse
)
from app.schemas.job_posting import JobRequirementsParsing, ParsedJobRequirements
from app.services.cv_parser import CVParser
from app.services.cv_analyzer import CVAnalyzer
from app.services.nlp_service import NLPService

logger = logging.getLogger(__name__)
router = APIRouter()

# Initialize services
cv_parser = CVParser()
cv_analyzer = CVAnalyzer()
nlp_service = NLPService()


@router.post("/upload-and-analyze")
async def upload_and_analyze_cvs(
    files: List[UploadFile] = File(...),
    job_title: str = Form(...),
    job_requirements: str = Form(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Upload CV files and analyze them against job requirements

    This is the main endpoint that the frontend dashboard uses to:
    1. Upload multiple CV files
    2. Parse each CV to extract structured information
    3. Analyze candidates against job requirements
    4. Return shortlisted and rejected candidates

    Args:
        files: List of uploaded CV files (PDF, DOC, DOCX)
        job_title: Job title/position
        job_requirements: Natural language job requirements
        db: Database session
        current_user: Current authenticated user

    Returns:
        AnalysisResults: Analysis summary with candidate matches
    """
    try:
        # Validate files
        if not files:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No files uploaded"
            )

        # Check file extensions
        allowed_extensions = settings.ALLOWED_EXTENSIONS
        for file in files:
            file_ext = file.filename.split('.')[-1].lower() if '.' in file.filename else ''
            if file_ext not in allowed_extensions:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"File type '{file_ext}' not allowed. Supported: {', '.join(allowed_extensions)}"
                )

        # Parse job requirements using NLP
        parsed_requirements = nlp_service.parse_job_requirements(job_requirements)

        # Ensure user has a company
        if not current_user.company_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User must be associated with a company to upload CVs"
            )

        # Create job posting record
        job_posting = JobPosting(
            company_id=current_user.company_id,  # MULTI-TENANT: Set company_id
            title=job_title,
            description=job_requirements,
            required_skills=parsed_requirements.required_skills,
            preferred_skills=parsed_requirements.preferred_skills,
            education_requirements=parsed_requirements.education_requirements,
            experience_requirements=parsed_requirements.experience_requirements,
            soft_skills=parsed_requirements.soft_skills,
            min_experience_years=parsed_requirements.min_experience_years,
            max_experience_years=parsed_requirements.max_experience_years,
            created_by=current_user.id,
            status="active"
        )
        db.add(job_posting)
        db.flush()  # Get the ID without committing

        candidates = []
        processing_results = []

        # Process each uploaded file
        for file in files:
            try:
                # Save file
                file_path = os.path.join(settings.UPLOAD_FOLDER, file.filename)
                with open(file_path, "wb") as buffer:
                    content = await file.read()
                    buffer.write(content)

                # Parse CV
                logger.info(f"Parsing CV: {file.filename}")
                parsed_data = cv_parser.parse_cv_file(file_path)

                # Extract candidate name
                candidate_name = cv_parser.extract_candidate_name(parsed_data.get('raw_text', ''))
                candidate_email = parsed_data.get('personal_info', {}).get('email')

                # Create candidate record
                candidate = Candidate(
                    company_id=current_user.company_id,  # MULTI-TENANT: Set company_id
                    name=candidate_name,
                    email=candidate_email,
                    original_filename=file.filename,
                    file_path=file_path,
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
                db.flush()  # Get the ID without committing
                candidates.append(candidate)

                processing_results.append({
                    'filename': file.filename,
                    'status': 'success',
                    'candidate_id': candidate.id
                })

            except Exception as e:
                logger.error(f"Failed to process file {file.filename}: {str(e)}")
                processing_results.append({
                    'filename': file.filename,
                    'status': 'failed',
                    'error': str(e)
                })

        if not candidates:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No candidates could be processed successfully"
            )

        # Analyze candidates against job requirements
        logger.info(f"Analyzing {len(candidates)} candidates against job requirements")
        analysis_results = cv_analyzer.analyze_candidates_for_job(
            db, candidates, job_posting, current_user.id
        )

        # Create analysis records
        cv_analyses = []
        for analysis_data in analysis_results:
            cv_analysis = CVAnalysis(
                company_id=current_user.company_id,  # MULTI-TENANT: Set company_id
                candidate_id=analysis_data.candidate_id,
                job_posting_id=analysis_data.job_posting_id,
                analyzed_by=current_user.id,
                overall_score=analysis_data.overall_score,
                match_status=analysis_data.match_status,
                skill_match_score=analysis_data.skill_match_score,
                education_match_score=analysis_data.education_match_score,
                experience_match_score=analysis_data.experience_match_score,
                soft_skills_score=analysis_data.soft_skills_score,
                matched_skills=analysis_data.matched_skills,
                missing_skills=analysis_data.missing_skills,
                matched_education=analysis_data.matched_education,
                experience_analysis=analysis_data.experience_analysis,
                ai_summary=analysis_data.ai_summary,
                strengths=analysis_data.strengths,
                concerns=analysis_data.concerns,
                recommendations=analysis_data.recommendations,
                processing_time_ms=analysis_data.processing_time_ms
            )
            db.add(cv_analysis)
            cv_analyses.append(cv_analysis)

        # Commit all changes
        db.commit()

        # Prepare response data
        candidate_results = []
        for analysis in cv_analyses:
            candidate = next(c for c in candidates if c.id == analysis.candidate_id)
            candidate_results.append(CandidateWithAnalysis(
                id=candidate.id,
                name=candidate.name,
                email=candidate.email,
                match_score=analysis.overall_score,
                summary=analysis.ai_summary or f"Overall match: {analysis.overall_score:.0f}%",
                strengths=analysis.strengths or [],
                concerns=analysis.concerns or [],
                match_status=analysis.match_status
            ))

        # Calculate statistics
        stats = cv_analyzer.get_analysis_statistics(cv_analyses)

        return AnalysisResults(
            total=stats['total'],
            shortlisted=stats['shortlisted'],
            rejected=stats['rejected'],
            candidates=candidate_results
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Analysis failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Analysis failed: {str(e)}"
        )


@router.post("/parse-requirements", response_model=ParsedJobRequirements)
async def parse_job_requirements(
    requirements: JobRequirementsParsing,
    current_user: User = Depends(get_current_active_user)
):
    """
    Parse natural language job requirements into structured format

    Args:
        requirements: Raw job requirements text
        current_user: Current authenticated user

    Returns:
        ParsedJobRequirements: Structured job requirements
    """
    try:
        parsed = nlp_service.parse_job_requirements(requirements.raw_requirements)
        return parsed
    except Exception as e:
        logger.error(f"Failed to parse requirements: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Failed to parse requirements: {str(e)}"
        )


@router.get("/results/{analysis_id}", response_model=CVAnalysisResponse)
async def get_analysis_result(
    analysis_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get detailed analysis results by ID
    (Company-scoped for data isolation)

    Args:
        analysis_id: CV analysis ID
        db: Database session
        current_user: Current authenticated user

    Returns:
        CVAnalysisResponse: Detailed analysis results
    """
    query = db.query(CVAnalysis).filter(CVAnalysis.id == analysis_id)

    # MULTI-TENANT FILTER: Only allow access to user's company data
    if current_user.company_id:
        query = query.filter(CVAnalysis.company_id == current_user.company_id)

    analysis = query.first()

    if not analysis:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Analysis not found"
        )

    return analysis


@router.get("/candidates/{status}")
async def get_candidates_by_status(
    status: str,
    job_posting_id: int = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get candidates by match status (shortlisted, rejected, pending)
    (Company-scoped for data isolation)

    Args:
        status: Match status filter
        job_posting_id: Optional job posting ID filter
        db: Database session
        current_user: Current authenticated user

    Returns:
        List of candidates with the specified status
    """
    query = db.query(CVAnalysis).filter(CVAnalysis.match_status == status)

    # MULTI-TENANT FILTER: Only show analyses from user's company
    if current_user.company_id:
        query = query.filter(CVAnalysis.company_id == current_user.company_id)

    if job_posting_id:
        query = query.filter(CVAnalysis.job_posting_id == job_posting_id)

    analyses = query.all()

    results = []
    for analysis in analyses:
        candidate = db.query(Candidate).filter(Candidate.id == analysis.candidate_id).first()
        if candidate:
            results.append(CandidateWithAnalysis(
                id=candidate.id,
                name=candidate.name,
                email=candidate.email,
                match_score=analysis.overall_score,
                summary=analysis.ai_summary or f"Overall match: {analysis.overall_score:.0f}%",
                strengths=analysis.strengths or [],
                concerns=analysis.concerns or [],
                match_status=analysis.match_status
            ))

    return results


@router.post("/demo-upload-and-analyze")
async def demo_upload_and_analyze_cvs(
    files: List[UploadFile] = File(...),
    job_title: str = Form(...),
    job_requirements: str = Form(...),
    db: Session = Depends(get_db)
):
    """
    DEMO VERSION: Upload CV files and analyze them against job requirements
    This endpoint works without authentication for testing purposes.
    """
    try:
        # Validate files
        if not files:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No files uploaded"
            )

        # Check file extensions
        allowed_extensions = settings.ALLOWED_EXTENSIONS
        for file in files:
            file_ext = file.filename.split('.')[-1].lower() if '.' in file.filename else ''
            if file_ext not in allowed_extensions:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"File type '{file_ext}' not allowed. Supported: {', '.join(allowed_extensions)}"
                )

        # Parse job requirements using NLP
        parsed_requirements = nlp_service.parse_job_requirements(job_requirements)

        # Get demo company (company_id = 1) or create if doesn't exist
        from app.models import Company
        demo_company = db.query(Company).filter(Company.id == 1).first()
        if not demo_company:
            # Create demo company for testing
            demo_company = Company(
                company_name="Demo Company",
                contact_email="demo@resumify.com",
                is_active=True
            )
            db.add(demo_company)
            db.flush()

        # Create temporary job posting for analysis (don't save to DB)
        job_posting = JobPosting(
            company_id=1,  # Demo company ID
            title=job_title,
            description=job_requirements,
            required_skills=parsed_requirements.required_skills,
            preferred_skills=parsed_requirements.preferred_skills,
            education_requirements=parsed_requirements.education_requirements,
            experience_requirements=parsed_requirements.experience_requirements,
            soft_skills=parsed_requirements.soft_skills,
            min_experience_years=parsed_requirements.min_experience_years,
            max_experience_years=parsed_requirements.max_experience_years,
            created_by=1,  # Demo user ID
            status="active"
        )
        job_posting.id = 0  # Temporary ID

        candidates = []
        processing_results = []

        # Process each uploaded file
        for file in files:
            try:
                # Save file temporarily
                file_path = os.path.join(settings.UPLOAD_FOLDER, file.filename)
                with open(file_path, "wb") as buffer:
                    content = await file.read()
                    buffer.write(content)

                # Parse CV
                logger.info(f"Parsing CV: {file.filename}")
                parsed_data = cv_parser.parse_cv_file(file_path)

                # Extract candidate name
                candidate_name = cv_parser.extract_candidate_name(parsed_data.get('raw_text', ''))
                candidate_email = parsed_data.get('personal_info', {}).get('email')

                # Get demo company (company_id = 1) or create if doesn't exist
                from app.models import Company
                demo_company = db.query(Company).filter(Company.id == 1).first()
                if not demo_company:
                    # Create demo company for testing
                    demo_company = Company(
                        id=1,
                        name="Demo Company",
                        industry="Technology",
                        size="1-10",
                        website="https://demo.resumify.com"
                    )
                    db.add(demo_company)
                    db.flush()

                # Create candidate record and save to DB
                candidate = Candidate(
                    company_id=1,  # Demo company ID
                    name=candidate_name,
                    email=candidate_email,
                    original_filename=file.filename,
                    file_path=file_path,
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

                # Save candidate to database
                db.add(candidate)
                db.flush()  # This assigns the ID

                candidates.append(candidate)

                processing_results.append({
                    'filename': file.filename,
                    'status': 'success',
                    'candidate_id': candidate.id
                })

                # Clean up temporary file
                try:
                    os.remove(file_path)
                except:
                    pass

            except Exception as e:
                logger.error(f"Failed to process file {file.filename}: {str(e)}")
                processing_results.append({
                    'filename': file.filename,
                    'status': 'failed',
                    'error': str(e)
                })

        if not candidates:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No candidates could be processed successfully"
            )

        # Analyze candidates against job requirements
        logger.info(f"Analyzing {len(candidates)} candidates against job requirements")
        analysis_results = cv_analyzer.analyze_candidates_for_job(
            db, candidates, job_posting, 1  # Demo user ID
        )

        # Prepare response data
        candidate_results = []
        for analysis in analysis_results:
            candidate = next(c for c in candidates if c.id == analysis.candidate_id)
            candidate_results.append(CandidateWithAnalysis(
                id=candidate.id,
                name=candidate.name,
                email=candidate.email,
                match_score=analysis.overall_score,
                summary=analysis.ai_summary or f"Overall match: {analysis.overall_score:.0f}%",
                strengths=analysis.strengths or [],
                concerns=analysis.concerns or [],
                match_status=analysis.match_status
            ))

        # Calculate statistics
        stats = cv_analyzer.get_analysis_statistics(analysis_results)

        # Commit all candidates to database
        db.commit()

        return AnalysisResults(
            total=stats['total'],
            shortlisted=stats['shortlisted'],
            rejected=stats['rejected'],
            candidates=candidate_results
        )

    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Demo analysis failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Analysis failed: {str(e)}"
        )


@router.post("/bulk")
async def analyze_candidates_bulk(
    request: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Analyze existing candidates against job requirements

    Args:
        request: Request containing candidate_ids, job_title, job_requirements
        db: Database session
        current_user: Current authenticated user

    Returns:
        List of analysis results
    """
    try:
        candidate_ids = request.get('candidate_ids', [])
        job_title = request.get('job_title', '')
        job_requirements = request.get('job_requirements', '')

        if not candidate_ids:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No candidate IDs provided"
            )

        # Get candidates from database
        candidates = db.query(Candidate).filter(Candidate.id.in_(candidate_ids)).all()

        if not candidates:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No candidates found"
            )

        # Parse job requirements using NLP
        parsed_requirements = nlp_service.parse_job_requirements(job_requirements)

        # Create temporary job posting for analysis
        job_posting = JobPosting(
            title=job_title,
            description=job_requirements,
            required_skills=parsed_requirements.required_skills,
            preferred_skills=parsed_requirements.preferred_skills,
            education_requirements=parsed_requirements.education_requirements,
            experience_requirements=parsed_requirements.experience_requirements,
            soft_skills=parsed_requirements.soft_skills,
            min_experience_years=parsed_requirements.min_experience_years,
            max_experience_years=parsed_requirements.max_experience_years,
            created_by=current_user.id,
            status="active"
        )

        # Don't save to database for temporary analysis
        # Just set an ID for the analysis
        job_posting.id = 0

        # Analyze candidates
        analysis_results = cv_analyzer.analyze_candidates_for_job(
            db, candidates, job_posting, current_user.id
        )

        # Convert to response format
        results = []
        for analysis_data in analysis_results:
            candidate = next(c for c in candidates if c.id == analysis_data.candidate_id)
            results.append({
                'candidate_id': analysis_data.candidate_id,
                'job_posting_id': analysis_data.job_posting_id,
                'overall_score': analysis_data.overall_score,
                'match_status': analysis_data.match_status,
                'skill_match_score': analysis_data.skill_match_score,
                'education_match_score': analysis_data.education_match_score,
                'experience_match_score': analysis_data.experience_match_score,
                'soft_skills_score': analysis_data.soft_skills_score,
                'matched_skills': analysis_data.matched_skills,
                'missing_skills': analysis_data.missing_skills,
                'ai_summary': analysis_data.ai_summary,
                'strengths': analysis_data.strengths,
                'concerns': analysis_data.concerns,
                'recommendations': analysis_data.recommendations,
                'candidate_name': candidate.name,
                'candidate_email': candidate.email
            })

        return results

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Bulk analysis failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Analysis failed: {str(e)}"
        )