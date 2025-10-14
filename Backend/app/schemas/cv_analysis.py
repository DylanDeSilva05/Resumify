"""
CV Analysis schemas for request/response validation
"""
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
from datetime import datetime


class CVAnalysisBase(BaseModel):
    candidate_id: int
    job_posting_id: int
    overall_score: float
    match_status: str  # shortlisted, rejected, pending


class CVAnalysisCreate(CVAnalysisBase):
    skill_match_score: float = 0.0
    education_match_score: float = 0.0
    experience_match_score: float = 0.0
    soft_skills_score: float = 0.0
    matched_skills: Optional[List[str]] = []
    missing_skills: Optional[List[str]] = []
    matched_education: Optional[List[str]] = []
    experience_analysis: Optional[Dict[str, Any]] = None
    ai_summary: Optional[str] = None
    strengths: Optional[List[str]] = []
    concerns: Optional[List[str]] = []
    recommendations: Optional[List[str]] = []
    processing_time_ms: Optional[int] = None


class CVAnalysisResponse(CVAnalysisBase):
    id: int
    analyzed_by: int
    skill_match_score: float = 0.0
    education_match_score: float = 0.0
    experience_match_score: float = 0.0
    soft_skills_score: float = 0.0
    matched_skills: Optional[List[str]] = []
    missing_skills: Optional[List[str]] = []
    matched_education: Optional[List[str]] = []
    experience_analysis: Optional[Dict[str, Any]] = None
    ai_summary: Optional[str] = None
    strengths: Optional[List[str]] = []
    concerns: Optional[List[str]] = []
    recommendations: Optional[List[str]] = []
    analysis_version: str = "1.0"
    processing_time_ms: Optional[int] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class CandidateWithAnalysis(BaseModel):
    """Schema for candidate with analysis results"""
    id: int
    name: str
    email: Optional[str] = None
    match_score: float
    summary: str
    strengths: List[str] = []
    concerns: List[str] = []
    match_status: str


class AnalysisResults(BaseModel):
    """Schema for analysis results summary"""
    total: int
    shortlisted: int
    rejected: int
    candidates: List[CandidateWithAnalysis]


class CVUploadRequest(BaseModel):
    """Schema for CV upload and analysis request"""
    job_title: str
    job_requirements: str

    class Config:
        schema_extra = {
            "example": {
                "job_title": "Senior Software Developer",
                "job_requirements": "We are looking for a Senior Software Developer with 3-5 years of experience in Python, React, and SQL databases. Bachelor's degree in Computer Science required. Strong communication and problem-solving skills essential."
            }
        }