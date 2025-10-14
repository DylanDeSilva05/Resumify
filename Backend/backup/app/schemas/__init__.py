# Import all schemas for easy access
from .user import UserCreate, UserUpdate, UserResponse, UserLogin, Token
from .candidate import CandidateResponse, CandidateCreate, CandidateUpdate
from .job_posting import JobPostingCreate, JobPostingResponse, JobPostingUpdate
from .cv_analysis import CVAnalysisResponse, CVAnalysisCreate
from .interview import InterviewCreate, InterviewResponse, InterviewUpdate

__all__ = [
    "UserCreate", "UserUpdate", "UserResponse", "UserLogin", "Token",
    "CandidateResponse", "CandidateCreate", "CandidateUpdate",
    "JobPostingCreate", "JobPostingResponse", "JobPostingUpdate",
    "CVAnalysisResponse", "CVAnalysisCreate",
    "InterviewCreate", "InterviewResponse", "InterviewUpdate"
]