"""
Candidate model for storing CV information and analysis results
"""
from sqlalchemy import Column, Integer, String, Text, Float, DateTime, ForeignKey, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base


class Candidate(Base):
    """Candidate model for storing parsed CV information"""

    __tablename__ = "candidates"

    id = Column(Integer, primary_key=True, index=True)

    # Multi-tenant: Company Association
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False, index=True)

    # Basic Information
    name = Column(String, nullable=False, index=True)
    email = Column(String, nullable=True, index=True)
    phone = Column(String, nullable=True)

    # CV File Information
    original_filename = Column(String, nullable=False)
    file_path = Column(String, nullable=False)
    file_size = Column(Integer, nullable=False)

    # Parsed Content
    raw_text = Column(Text, nullable=True)

    # Structured Information (JSON fields)
    personal_info = Column(JSON, nullable=True)  # Contact info, location, etc.
    education = Column(JSON, nullable=True)      # Degrees, institutions, years
    work_experience = Column(JSON, nullable=True)  # Jobs, companies, durations
    skills = Column(JSON, nullable=True)         # Technical and soft skills
    certifications = Column(JSON, nullable=True)  # Professional certifications
    languages = Column(JSON, nullable=True)     # Language proficiencies

    # Experience Metrics
    total_experience_years = Column(Float, default=0.0)

    # Analysis Status
    parsing_status = Column(String, default="pending")  # pending, completed, failed
    parsing_error = Column(Text, nullable=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    company = relationship("Company", back_populates="candidates")
    cv_analyses = relationship("CVAnalysis", back_populates="candidate")
    interviews = relationship("Interview", back_populates="candidate")

    def __repr__(self):
        return f"<Candidate(id={self.id}, name='{self.name}', email='{self.email}', company_id={self.company_id})>"