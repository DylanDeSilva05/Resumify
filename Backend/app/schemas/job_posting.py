"""
Job posting schemas for request/response validation
"""
from pydantic import BaseModel, validator
from typing import Optional, Dict, Any, List
from datetime import datetime


class JobPostingBase(BaseModel):
    title: str
    description: str
    location: Optional[str] = None
    work_type: Optional[str] = None
    min_experience_years: int = 0
    max_experience_years: Optional[int] = None

    @validator("title")
    def validate_title(cls, v):
        if len(v.strip()) < 3:
            raise ValueError("Job title must be at least 3 characters long")
        return v.strip()

    @validator("description")
    def validate_description(cls, v):
        if len(v.strip()) < 10:
            raise ValueError("Job description must be at least 10 characters long")
        return v.strip()


class JobPostingCreate(JobPostingBase):
    required_skills: Optional[List[str]] = []
    preferred_skills: Optional[List[str]] = []
    education_requirements: Optional[List[str]] = []
    experience_requirements: Optional[List[str]] = []
    soft_skills: Optional[List[str]] = []
    matching_weights: Optional[Dict[str, float]] = None


class JobPostingUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    required_skills: Optional[List[str]] = None
    preferred_skills: Optional[List[str]] = None
    education_requirements: Optional[List[str]] = None
    experience_requirements: Optional[List[str]] = None
    soft_skills: Optional[List[str]] = None
    location: Optional[str] = None
    work_type: Optional[str] = None
    min_experience_years: Optional[int] = None
    max_experience_years: Optional[int] = None
    status: Optional[str] = None
    matching_weights: Optional[Dict[str, float]] = None


class JobPostingResponse(JobPostingBase):
    id: int
    required_skills: Optional[List[str]] = []
    preferred_skills: Optional[List[str]] = []
    education_requirements: Optional[List[str]] = []
    experience_requirements: Optional[List[str]] = []
    soft_skills: Optional[List[str]] = []
    matching_weights: Optional[Dict[str, float]] = None
    created_by: int
    status: str = "active"
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class JobPostingListResponse(BaseModel):
    job_postings: List[JobPostingResponse]
    total: int
    page: int
    pages: int


class JobRequirementsParsing(BaseModel):
    """Schema for parsing job requirements from natural language"""
    raw_requirements: str

    class Config:
        schema_extra = {
            "example": {
                "raw_requirements": "We are looking for a Senior Software Developer with 3-5 years of experience in Python, React, and SQL databases. Bachelor's degree in Computer Science required. Strong communication and problem-solving skills essential."
            }
        }


class ParsedJobRequirements(BaseModel):
    """Schema for structured job requirements after parsing"""
    required_skills: List[str]
    preferred_skills: List[str]
    education_requirements: List[str]
    experience_requirements: List[str]
    soft_skills: List[str]
    min_experience_years: int
    max_experience_years: Optional[int] = None