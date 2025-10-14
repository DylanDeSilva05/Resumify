"""
CV Analysis model for storing candidate matching results
"""
from sqlalchemy import Column, Integer, String, Text, Float, JSON, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base


class CVAnalysis(Base):
    """CV Analysis model for storing matching results between candidates and job postings"""

    __tablename__ = "cv_analyses"

    id = Column(Integer, primary_key=True, index=True)

    # Multi-tenant: Company Association
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False, index=True)

    # Foreign Keys
    candidate_id = Column(Integer, ForeignKey("candidates.id"), nullable=False)
    job_posting_id = Column(Integer, ForeignKey("job_postings.id"), nullable=False)
    analyzed_by = Column(Integer, ForeignKey("users.id"), nullable=False)

    # Overall Matching Score
    overall_score = Column(Float, nullable=False, index=True)  # 0-100
    match_status = Column(String, nullable=False)  # shortlisted, rejected, pending

    # Detailed Scores (JSON)
    skill_match_score = Column(Float, default=0.0)
    education_match_score = Column(Float, default=0.0)
    experience_match_score = Column(Float, default=0.0)
    soft_skills_score = Column(Float, default=0.0)

    # Detailed Analysis Results (JSON fields)
    matched_skills = Column(JSON, nullable=True)      # Skills that match
    missing_skills = Column(JSON, nullable=True)      # Required skills not found
    matched_education = Column(JSON, nullable=True)   # Education requirements met
    experience_analysis = Column(JSON, nullable=True) # Experience breakdown

    # AI-Generated Summary
    ai_summary = Column(Text, nullable=True)
    strengths = Column(JSON, nullable=True)           # Key strengths
    concerns = Column(JSON, nullable=True)            # Potential concerns
    recommendations = Column(JSON, nullable=True)     # HR recommendations

    # Analysis Metadata
    analysis_version = Column(String, default="1.0")
    processing_time_ms = Column(Integer, nullable=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    company = relationship("Company", back_populates="cv_analyses")
    candidate = relationship("Candidate", back_populates="cv_analyses")
    job_posting = relationship("JobPosting", back_populates="cv_analyses")
    analyzer = relationship("User", foreign_keys=[analyzed_by])

    def __repr__(self):
        return f"<CVAnalysis(id={self.id}, score={self.overall_score}, status='{self.match_status}', company_id={self.company_id})>"