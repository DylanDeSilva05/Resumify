"""
Authentication and 2FA schemas
"""
from pydantic import BaseModel, EmailStr, validator
from typing import Optional, List
from datetime import datetime

from app.models.user import UserRole


class LoginRequest(BaseModel):
    username: str
    password: str
    totp_code: Optional[str] = None  # 2FA code if enabled
    backup_code: Optional[str] = None  # Backup code if TOTP unavailable

    @validator('username')
    def username_must_not_be_empty(cls, v):
        if not v.strip():
            raise ValueError('Username cannot be empty')
        return v.strip()

    @validator('password')
    def password_must_not_be_empty(cls, v):
        if not v:
            raise ValueError('Password cannot be empty')
        return v


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: int
    username: str
    role: UserRole
    two_fa_required: bool = False  # True if 2FA verification is pending
    expires_in: int  # Token expiration in seconds


class TwoFASetupResponse(BaseModel):
    secret: str
    backup_codes: List[str]
    qr_code_url: str
    manual_entry_key: str


class TwoFAVerifyRequest(BaseModel):
    code: str

    @validator('code')
    def validate_code(cls, v):
        # Remove spaces and validate format
        code = v.replace(' ', '').strip()
        if not code.isdigit() or len(code) != 6:
            raise ValueError('Code must be 6 digits')
        return code


class TwoFADisableRequest(BaseModel):
    password: str
    code: str

    @validator('code')
    def validate_code(cls, v):
        code = v.replace(' ', '').strip()
        if not code.isdigit() or len(code) != 6:
            raise ValueError('Code must be 6 digits')
        return code


class BackupCodesResponse(BaseModel):
    backup_codes: List[str]
    message: str


class TwoFAStatusResponse(BaseModel):
    enabled: bool
    backup_codes_remaining: int


class UserCreateRequest(BaseModel):
    username: str
    email: EmailStr
    full_name: str
    password: str
    role: UserRole

    @validator('username')
    def validate_username(cls, v):
        username = v.strip()
        if len(username) < 3:
            raise ValueError('Username must be at least 3 characters long')
        if not username.replace('_', '').replace('-', '').isalnum():
            raise ValueError('Username can only contain letters, numbers, hyphens, and underscores')
        return username

    @validator('full_name')
    def validate_full_name(cls, v):
        name = v.strip()
        if len(name) < 2:
            raise ValueError('Full name must be at least 2 characters long')
        return name

    @validator('password')
    def validate_password(cls, v):
        # Basic validation - detailed validation in SecurityService
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        return v


class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    full_name: str
    role: UserRole
    is_active: bool
    two_fa_enabled: bool
    last_login: Optional[datetime]
    created_at: datetime

    class Config:
        from_attributes = True


class UserUpdateRequest(BaseModel):
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    role: Optional[UserRole] = None
    is_active: Optional[bool] = None

    @validator('full_name')
    def validate_full_name(cls, v):
        if v is not None:
            name = v.strip()
            if len(name) < 2:
                raise ValueError('Full name must be at least 2 characters long')
            return name
        return v


class PasswordChangeRequest(BaseModel):
    current_password: str
    new_password: str
    confirm_password: str

    @validator('confirm_password')
    def passwords_match(cls, v, values):
        if 'new_password' in values and v != values['new_password']:
            raise ValueError('New password and confirmation do not match')
        return v

    @validator('new_password')
    def validate_new_password(cls, v):
        if len(v) < 8:
            raise ValueError('New password must be at least 8 characters long')
        return v


class PasswordResetRequest(BaseModel):
    email: EmailStr


class PasswordResetConfirm(BaseModel):
    token: str
    new_password: str
    confirm_password: str

    @validator('confirm_password')
    def passwords_match(cls, v, values):
        if 'new_password' in values and v != values['new_password']:
            raise ValueError('Password and confirmation do not match')
        return v

    @validator('new_password')
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        return v


class SecurityEventResponse(BaseModel):
    event_type: str
    timestamp: datetime
    ip_address: str
    details: str
    success: bool


class AccountSecurityResponse(BaseModel):
    two_fa_enabled: bool
    backup_codes_remaining: int
    last_login: Optional[datetime]
    failed_login_attempts: int
    account_locked: bool
    password_last_changed: datetime
    recent_security_events: List[SecurityEventResponse]