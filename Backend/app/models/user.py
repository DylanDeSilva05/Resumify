"""
User model for HR team members
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum
from app.core.database import Base


class UserRole(str, enum.Enum):
    """Unified role system for RBAC and multi-tenancy"""
    SUPER_ADMIN = "super_admin"      # System owner - can create companies
    COMPANY_ADMIN = "company_admin"  # Company owner - can manage company users
    COMPANY_USER = "company_user"    # Regular company employee - can use features
    RECRUITER = "recruiter"          # Limited access - CV screening, interviews


class User(Base):
    """User model for HR team authentication and management"""

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)

    # Multi-tenant: Company Association
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=True, index=True)
    # Note: company_id is nullable for SUPER_ADMIN users who don't belong to any company

    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    full_name = Column(String, nullable=False)
    hashed_password = Column(String, nullable=False)

    # Role-based access control and multi-tenancy
    # Use native_enum=False and create_constraint=False for SQLite compatibility
    role = Column(Enum(UserRole, native_enum=False, create_constraint=False), nullable=False, default=UserRole.COMPANY_USER)

    is_active = Column(Boolean, default=True)

    # 2FA Fields
    two_fa_enabled = Column(Boolean, default=False)
    two_fa_secret = Column(String, nullable=True)  # TOTP secret key
    backup_codes = Column(String, nullable=True)   # JSON array of backup codes

    # Security Fields
    failed_login_attempts = Column(Integer, default=0)
    account_locked_until = Column(DateTime(timezone=True), nullable=True)
    last_login = Column(DateTime(timezone=True), nullable=True)
    password_changed_at = Column(DateTime(timezone=True), server_default=func.now())

    # Password Reset Fields
    reset_otp = Column(String, nullable=True)  # OTP for password reset
    reset_otp_expires_at = Column(DateTime(timezone=True), nullable=True)  # OTP expiration time

    # Email/SMTP Settings (User-level)
    smtp_host = Column(String, nullable=True)
    smtp_port = Column(Integer, nullable=True, default=587)
    smtp_username = Column(String, nullable=True)
    smtp_password = Column(String, nullable=True)  # Encrypted
    smtp_from_name = Column(String, nullable=True)
    smtp_enabled = Column(Boolean, default=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    company = relationship("Company", back_populates="users")

    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}', email='{self.email}', company_id={self.company_id})>"