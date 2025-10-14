"""
Interview schemas for request/response validation
"""
from pydantic import BaseModel, validator
from typing import Optional
from datetime import datetime
from app.models.interview import InterviewType, InterviewStatus


# Nested schemas for relationships
class CandidateInInterview(BaseModel):
    id: int
    name: str
    email: Optional[str] = None

    class Config:
        from_attributes = True


class JobPostingInInterview(BaseModel):
    id: int
    title: str

    class Config:
        from_attributes = True


class InterviewBase(BaseModel):
    candidate_id: int
    interview_type: InterviewType
    scheduled_datetime: datetime
    duration_minutes: int = 60
    location: Optional[str] = None
    meeting_link: Optional[str] = None
    position: Optional[str] = None
    interviewer_name: Optional[str] = None
    interviewer_email: Optional[str] = None

    @validator("scheduled_datetime")
    def validate_future_datetime(cls, v):
        if v <= datetime.utcnow():
            raise ValueError("Interview must be scheduled for a future date")
        return v


class InterviewCreate(InterviewBase):
    pass


class InterviewUpdate(BaseModel):
    interview_type: Optional[InterviewType] = None
    status: Optional[InterviewStatus] = None
    scheduled_datetime: Optional[datetime] = None
    duration_minutes: Optional[int] = None
    location: Optional[str] = None
    meeting_link: Optional[str] = None
    position: Optional[str] = None
    interviewer_name: Optional[str] = None
    interviewer_email: Optional[str] = None
    notes: Optional[str] = None
    feedback: Optional[str] = None
    rating: Optional[int] = None

    @validator("rating")
    def validate_rating(cls, v):
        if v is not None and (v < 1 or v > 10):
            raise ValueError("Rating must be between 1 and 10")
        return v

    @validator("scheduled_datetime")
    def validate_future_datetime(cls, v):
        if v and v <= datetime.utcnow():
            raise ValueError("Interview must be scheduled for a future date")
        return v


class InterviewResponse(BaseModel):
    id: int
    candidate_id: int
    scheduled_by: int
    interview_type: InterviewType
    scheduled_datetime: datetime  # No validation - allow past dates when reading
    duration_minutes: int = 60
    location: Optional[str] = None
    meeting_link: Optional[str] = None
    position: Optional[str] = None
    interviewer_name: Optional[str] = None
    interviewer_email: Optional[str] = None
    status: InterviewStatus = InterviewStatus.SCHEDULED
    notes: Optional[str] = None
    feedback: Optional[str] = None
    rating: Optional[int] = None
    invitation_sent: Optional[datetime] = None
    confirmation_received: Optional[datetime] = None
    reminder_sent: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    # Relationships
    candidate: Optional[CandidateInInterview] = None
    job_posting: Optional[JobPostingInInterview] = None

    class Config:
        from_attributes = True


class InterviewListResponse(BaseModel):
    interviews: list[InterviewResponse]
    total: int
    page: int
    pages: int


class InterviewSchedulingRequest(BaseModel):
    """Schema for scheduling interview from frontend"""
    candidate_id: int
    datetime: str  # ISO format datetime string
    type: str  # video, phone, in-person

    @validator("type")
    def validate_type(cls, v):
        valid_types = ["video", "phone", "in-person"]
        if v not in valid_types:
            raise ValueError(f"Type must be one of: {', '.join(valid_types)}")
        return v