"""
Profile management endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional
from pydantic import BaseModel, EmailStr

from app.api.deps import get_db, get_current_active_user
from app.models import User
from app.core.security import verify_password, get_password_hash

router = APIRouter()


class ProfileResponse(BaseModel):
    """Profile response schema"""
    id: int
    username: str
    email: EmailStr
    full_name: Optional[str] = None
    created_at: str
    is_active: bool

    class Config:
        from_attributes = True


class ProfileUpdate(BaseModel):
    """Profile update schema"""
    full_name: Optional[str] = None
    email: Optional[EmailStr] = None


class PasswordChange(BaseModel):
    """Password change schema"""
    current_password: str
    new_password: str


@router.get("/", response_model=ProfileResponse)
async def get_profile(
    current_user: User = Depends(get_current_active_user)
):
    """
    Get current user profile
    """
    return ProfileResponse(
        id=current_user.id,
        username=current_user.username,
        email=current_user.email,
        full_name=current_user.full_name,
        created_at=current_user.created_at.isoformat() if current_user.created_at else "",
        is_active=current_user.is_active
    )


@router.put("/", response_model=ProfileResponse)
async def update_profile(
    profile_data: ProfileUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Update current user profile
    """
    try:
        # Check if email is being changed and if it already exists
        if profile_data.email and profile_data.email != current_user.email:
            existing_user = db.query(User).filter(
                User.email == profile_data.email,
                User.id != current_user.id
            ).first()
            if existing_user:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email already registered"
                )

        # Update profile fields
        if profile_data.full_name is not None:
            current_user.full_name = profile_data.full_name
        if profile_data.email is not None:
            current_user.email = profile_data.email

        db.commit()
        db.refresh(current_user)

        return ProfileResponse(
            id=current_user.id,
            username=current_user.username,
            email=current_user.email,
            full_name=current_user.full_name,
            created_at=current_user.created_at.isoformat() if current_user.created_at else "",
            is_active=current_user.is_active
        )

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update profile: {str(e)}"
        )


@router.post("/change-password")
async def change_password(
    password_data: PasswordChange,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Change user password
    """
    try:
        # Verify current password
        if not verify_password(password_data.current_password, current_user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Incorrect current password"
            )

        # Validate new password
        if len(password_data.new_password) < 8:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="New password must be at least 8 characters long"
            )

        # Update password
        current_user.hashed_password = get_password_hash(password_data.new_password)
        db.commit()

        return {"message": "Password changed successfully"}

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to change password: {str(e)}"
        )


@router.get("/security-info")
async def get_security_info(
    current_user: User = Depends(get_current_active_user)
):
    """
    Get security information for the user
    """
    return {
        "two_factor_enabled": getattr(current_user, 'totp_secret', None) is not None,
        "last_login": getattr(current_user, 'last_login', None),
        "account_created": current_user.created_at.isoformat() if current_user.created_at else "",
        "login_attempts": getattr(current_user, 'failed_login_attempts', 0),
        "account_locked": not current_user.is_active
    }