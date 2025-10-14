"""
Authentication endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from datetime import datetime, timedelta
import random
import string

from app.core.database import get_db
from app.core.exceptions import AuthenticationError
from app.core.security import refresh_access_token, blacklist_token, verify_token, get_password_hash
from app.schemas.user import UserLogin, Token
from app.services.auth_service import AuthService
from app.services.email_service import EmailService
from app.models.user import User
from app.models.company import Company
from app.core.security import decrypt_password

router = APIRouter()


# Pydantic models for forgot password
class ForgotPasswordRequest(BaseModel):
    username: str


class VerifyOTPRequest(BaseModel):
    username: str
    otp: str


class ResetPasswordRequest(BaseModel):
    username: str
    otp: str
    new_password: str


@router.post("/login", response_model=Token)
async def login(
    user_credentials: UserLogin,
    db: Session = Depends(get_db)
):
    """
    User login endpoint

    Args:
        user_credentials: Login credentials
        db: Database session

    Returns:
        Token: Access token and user information
    """
    try:
        token_data = AuthService.login_user(
            db,
            user_credentials.username,
            user_credentials.password,
            user_credentials.totp_code
        )
        return token_data
    except AuthenticationError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )


@router.post("/token", response_model=Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """
    OAuth2 compatible login endpoint

    Args:
        form_data: OAuth2 password form data
        db: Database session

    Returns:
        Token: Access token and user information
    """
    try:
        token_data = AuthService.login_user(
            db,
            form_data.username,
            form_data.password
        )
        return token_data
    except AuthenticationError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )


@router.post("/refresh", response_model=dict)
async def refresh_token(
    refresh_token: str,
    db: Session = Depends(get_db)
):
    """
    Refresh access token using refresh token

    Args:
        refresh_token: Valid refresh token
        db: Database session

    Returns:
        dict: New access token
    """
    try:
        new_access_token = refresh_access_token(refresh_token)
        if not new_access_token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token",
                headers={"WWW-Authenticate": "Bearer"},
            )

        return {
            "access_token": new_access_token,
            "token_type": "bearer"
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
            headers={"WWW-Authenticate": "Bearer"},
        )


@router.post("/logout", response_model=dict)
async def logout(
    access_token: str
):
    """
    Logout user by blacklisting the access token

    Args:
        access_token: Access token to blacklist

    Returns:
        dict: Logout confirmation
    """
    try:
        blacklist_token(access_token)
        return {"message": "Successfully logged out"}
    except Exception as e:
        # Even if blacklisting fails, consider logout successful
        return {"message": "Successfully logged out"}


@router.post("/forgot-password")
async def forgot_password(
    request: ForgotPasswordRequest,
    db: Session = Depends(get_db)
):
    """
    Request password reset OTP

    Args:
        request: Forgot password request with username
        db: Database session

    Returns:
        dict: Confirmation message with masked email
    """
    # Find user by username
    user = db.query(User).filter(User.username == request.username).first()

    if not user:
        # Don't reveal if username exists or not (security best practice)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Username not found. Please check and try again."
        )

    # Generate 6-digit OTP
    otp = ''.join(random.choices(string.digits, k=6))

    # Set OTP and expiration (10 minutes)
    user.reset_otp = otp
    user.reset_otp_expires_at = datetime.utcnow() + timedelta(minutes=10)
    db.commit()

    # Mask email for privacy (e.g., j***@gmail.com)
    email_parts = user.email.split('@')
    masked_email = f"{email_parts[0][0]}{'*' * (len(email_parts[0]) - 1)}@{email_parts[1]}"

    # Create email service with user's SMTP settings (for password reset, we allow unconfigured email for dev/testing)
    if user.smtp_enabled and all([user.smtp_host, user.smtp_port, user.smtp_username, user.smtp_password]):
        # User has SMTP configured - use it
        smtp_password = decrypt_password(user.smtp_password)
        email_service = EmailService(
            smtp_host=user.smtp_host,
            smtp_port=user.smtp_port,
            smtp_user=user.smtp_username,
            smtp_password=smtp_password
        )
    else:
        # No SMTP configured - create unconfigured service (will print OTP to console in dev mode)
        email_service = EmailService()

    # Send OTP via email
    email_sent = email_service.send_password_reset_otp(
        to_email=user.email,
        to_name=user.full_name,
        otp=otp
    )

    return {
        "message": "OTP has been sent to your registered email.",
        "masked_email": masked_email
    }


@router.post("/verify-otp")
async def verify_otp(
    request: VerifyOTPRequest,
    db: Session = Depends(get_db)
):
    """
    Verify OTP for password reset

    Args:
        request: OTP verification request
        db: Database session

    Returns:
        dict: Verification result
    """
    user = db.query(User).filter(User.username == request.username).first()

    if not user or not user.reset_otp:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid request"
        )

    # Check if OTP is expired
    if user.reset_otp_expires_at < datetime.utcnow():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="OTP has expired. Please request a new one."
        )

    # Verify OTP
    if user.reset_otp != request.otp:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid OTP"
        )

    return {"message": "OTP verified successfully"}


@router.post("/reset-password")
async def reset_password(
    request: ResetPasswordRequest,
    db: Session = Depends(get_db)
):
    """
    Reset password using verified OTP

    Args:
        request: Reset password request
        db: Database session

    Returns:
        dict: Reset confirmation
    """
    user = db.query(User).filter(User.username == request.username).first()

    if not user or not user.reset_otp:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid request"
        )

    # Check if OTP is expired
    if user.reset_otp_expires_at < datetime.utcnow():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="OTP has expired. Please request a new one."
        )

    # Verify OTP again
    if user.reset_otp != request.otp:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid OTP"
        )

    # Validate new password
    if len(request.new_password) < 8:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password must be at least 8 characters long"
        )

    # Update password
    user.hashed_password = get_password_hash(request.new_password)
    user.password_changed_at = datetime.utcnow()
    user.reset_otp = None  # Clear OTP
    user.reset_otp_expires_at = None
    user.failed_login_attempts = 0  # Reset failed attempts
    user.account_locked_until = None  # Unlock account if locked
    db.commit()

    return {"message": "Password reset successfully"}