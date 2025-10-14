"""
Candidate schemas for request/response validation
"""
from pydantic import BaseModel, EmailStr, validator
from typing import Optional, Dict, Any, List
from datetime import datetime


class CandidateBase(BaseModel):
    name: str
    email: Optional[EmailStr] = None
    phone: Optional[str] = None


class CandidateCreate(CandidateBase):
    original_filename: str
    file_path: str
    file_size: int


class CandidateUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    personal_info: Optional[Dict[str, Any]] = None
    education: Optional[List[Dict[str, Any]]] = None
    work_experience: Optional[List[Dict[str, Any]]] = None
    skills: Optional[Dict[str, Any]] = None
    certifications: Optional[List[Dict[str, Any]]] = None
    languages: Optional[List[Dict[str, Any]]] = None


class CandidateResponse(CandidateBase):
    id: int
    original_filename: str
    file_size: int
    raw_text: Optional[str] = None
    personal_info: Optional[Dict[str, Any]] = None
    education: Optional[List[Dict[str, Any]]] = None
    work_experience: Optional[List[Dict[str, Any]]] = None
    skills: Optional[Dict[str, Any]] = None
    certifications: Optional[List[Dict[str, Any]]] = None
    languages: Optional[List[Dict[str, Any]]] = None
    total_experience_years: float = 0.0
    parsing_status: str = "pending"
    parsing_error: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class CandidateListResponse(BaseModel):
    candidates: List[CandidateResponse]
    total: int
    page: int
    pages: int