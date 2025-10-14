"""
Company model for multi-tenant organization management
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base


class Company(Base):
    """Company model for multi-tenant isolation"""

    __tablename__ = "companies"

    id = Column(Integer, primary_key=True, index=True)

    # Company Information
    company_name = Column(String, unique=True, nullable=False, index=True)
    contact_email = Column(String, nullable=False, index=True)
    contact_phone = Column(String, nullable=True)

    # Address Information
    address = Column(Text, nullable=True)
    city = Column(String, nullable=True)
    state = Column(String, nullable=True)
    country = Column(String, nullable=True)
    postal_code = Column(String, nullable=True)

    # Subscription & Status
    is_active = Column(Boolean, default=True)
    subscription_tier = Column(String, default="basic")  # basic, premium, enterprise
    max_users = Column(Integer, default=5)  # Maximum users allowed
    max_cv_uploads_monthly = Column(Integer, default=100)  # Monthly CV upload limit

    # Email/SMTP Settings
    smtp_host = Column(String, nullable=True)  # e.g., smtp.gmail.com
    smtp_port = Column(Integer, nullable=True, default=587)  # Usually 587 for TLS
    smtp_username = Column(String, nullable=True)  # Email address
    smtp_password = Column(String, nullable=True)  # Encrypted app password
    smtp_from_name = Column(String, nullable=True)  # Display name for emails
    smtp_enabled = Column(Boolean, default=False)  # Enable/disable email sending

    # Company Settings (JSON can be added later for custom settings)
    # settings = Column(JSON, nullable=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    users = relationship("User", back_populates="company")
    candidates = relationship("Candidate", back_populates="company")
    job_postings = relationship("JobPosting", back_populates="company")
    cv_analyses = relationship("CVAnalysis", back_populates="company")
    interviews = relationship("Interview", back_populates="company")

    def __repr__(self):
        return f"<Company(id={self.id}, name='{self.company_name}')>"
