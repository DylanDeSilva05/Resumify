"""
Main API router for version 1
"""
from fastapi import APIRouter

from app.api.api_v1.endpoints import auth, users, candidates, jobs, analysis, interviews, upload, two_fa, profile

api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(users.router, prefix="/users", tags=["User Management"])
api_router.include_router(candidates.router, prefix="/candidates", tags=["Candidates"])
api_router.include_router(jobs.router, prefix="/jobs", tags=["Job Postings"])
api_router.include_router(analysis.router, prefix="/analysis", tags=["CV Analysis"])
api_router.include_router(interviews.router, prefix="/interviews", tags=["Interviews"])
api_router.include_router(upload.router, prefix="/upload", tags=["File Upload"])
api_router.include_router(two_fa.router, prefix="/2fa", tags=["Two-Factor Authentication"])
api_router.include_router(profile.router, prefix="/profile", tags=["Profile Management"])