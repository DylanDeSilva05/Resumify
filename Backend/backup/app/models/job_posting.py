"""
Job posting model for storing job requirements and criteria
"""
from sqlalchemy import Column, Integer, String, Text, JSON, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base


class JobPosting(Base):
    """Job posting model for storing job requirements and matching criteria"""

    __tablename__ = "job_postings"

    id = Column(Integer, primary_key=True, index=True)

    # Multi-tenant: Company Association
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False, index=True)

    # Basic Job Information
    title = Column(String, nullable=False, index=True)
    description = Column(Text, nullable=False)

    # Structured Requirements (JSON fields)
    required_skills = Column(JSON, nullable=True)      # Technical skills
    preferred_skills = Column(JSON, nullable=True)     # Nice-to-have skills
    education_requirements = Column(JSON, nullable=True)  # Degree requirements
    experience_requirements = Column(JSON, nullable=True)  # Years, industry experience
    soft_skills = Column(JSON, nullable=True)          # Communication, leadership, etc.

    # Experience Requirements
    min_experience_years = Column(Integer, default=0)
    max_experience_years = Column(Integer, nullable=True)

    # Location and Work Type
    location = Column(String, nullable=True)
    work_type = Column(String, nullable=True)  # remote, hybrid, onsite

    # Matching Configuration
    matching_weights = Column(JSON, nullable=True)  # Weights for different criteria

    # HR Information
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)

    # Status
    status = Column(String, default="active")  # active, inactive, closed

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    company = relationship("Company", back_populates="job_postings")
    creator = relationship("User", foreign_keys=[created_by])
    cv_analyses = relationship("CVAnalysis", back_populates="job_posting")

    def __repr__(self):
        return f"<JobPosting(id={self.id}, title='{self.title}', company_id={self.company_id})>"