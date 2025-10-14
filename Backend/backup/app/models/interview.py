"""
Interview model for scheduling and managing candidate interviews
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Enum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum
from app.core.database import Base


class InterviewType(str, enum.Enum):
    VIDEO = "video"
    PHONE = "phone"
    IN_PERSON = "in-person"


class InterviewStatus(str, enum.Enum):
    SCHEDULED = "scheduled"
    CONFIRMED = "confirmed"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    RESCHEDULED = "rescheduled"


class Interview(Base):
    """Interview model for managing candidate interview scheduling"""

    __tablename__ = "interviews"

    id = Column(Integer, primary_key=True, index=True)

    # Multi-tenant: Company Association
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False, index=True)

    # Foreign Keys
    candidate_id = Column(Integer, ForeignKey("candidates.id"), nullable=False)
    scheduled_by = Column(Integer, ForeignKey("users.id"), nullable=False)

    # Interview Details
    interview_type = Column(Enum(InterviewType), nullable=False)
    status = Column(Enum(InterviewStatus), default=InterviewStatus.SCHEDULED)

    # Scheduling Information
    scheduled_datetime = Column(DateTime(timezone=True), nullable=False, index=True)
    duration_minutes = Column(Integer, default=60)
    location = Column(String, nullable=True)  # For in-person or meeting link for video
    meeting_link = Column(String, nullable=True)  # Video call link

    # Interview Details
    position = Column(String, nullable=True)
    interviewer_name = Column(String, nullable=True)
    interviewer_email = Column(String, nullable=True)

    # Follow-up Information
    notes = Column(Text, nullable=True)
    feedback = Column(Text, nullable=True)
    rating = Column(Integer, nullable=True)  # 1-10 rating

    # Email Tracking
    invitation_sent = Column(DateTime(timezone=True), nullable=True)
    confirmation_received = Column(DateTime(timezone=True), nullable=True)
    reminder_sent = Column(DateTime(timezone=True), nullable=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    company = relationship("Company", back_populates="interviews")
    candidate = relationship("Candidate", back_populates="interviews")
    scheduler = relationship("User", foreign_keys=[scheduled_by])

    def __repr__(self):
        return f"<Interview(id={self.id}, candidate_id={self.candidate_id}, status='{self.status}', company_id={self.company_id})>"