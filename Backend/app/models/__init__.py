# Import all models here for easy access
from .company import Company
from .user import User, UserRole
from .candidate import Candidate
from .job_posting import JobPosting
from .cv_analysis import CVAnalysis
from .interview import Interview

__all__ = [
    "Company",
    "User",
    "UserRole",
    "Candidate",
    "JobPosting",
    "CVAnalysis",
    "Interview"
]