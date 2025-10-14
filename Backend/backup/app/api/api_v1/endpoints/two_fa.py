"""
Two-Factor Authentication endpoints
"""
import logging
from fastapi import APIRouter, Depends, HTTPException, status, Response
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from io import BytesIO

from app.core.database import get_db
from app.api.deps import get_current_active_user
from app.models.user import User
from app.services.two_fa_service import TwoFAService
from app.services.security_service import SecurityService
from app.schemas.auth import (
    TwoFASetupResponse, TwoFAVerifyRequest, TwoFADisableRequest,
    BackupCodesResponse, TwoFAStatusResponse
)

router = APIRouter()
logger = logging.getLogger(__name__)

two_fa_service = TwoFAService()
security_service = SecurityService()


@router.post("/setup", response_model=TwoFASetupResponse)
async def setup_2fa(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Initialize 2FA setup for user - generates secret and QR code

    Returns:
        TwoFASetupResponse: Setup information including QR code URL
    """
    try:
        if current_user.two_fa_enabled:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="2FA is already enabled for this account"
            )

        # Generate new secret key
        secret = two_fa_service.generate_secret_key()

        # Generate backup codes
        backup_codes = two_fa_service.generate_backup_codes()

        # Store temporarily (not fully enabled until verified)
        current_user.two_fa_secret = secret
        current_user.backup_codes = None  # Will be set after verification
        db.commit()

        security_service.log_security_event(
            "2FA_SETUP_INITIATED",
            current_user.id,
            "User initiated 2FA setup",
            ""
        )

        return TwoFASetupResponse(
            secret=secret,
            backup_codes=backup_codes,
            qr_code_url=f"/api/v1/2fa/qr-code",
            manual_entry_key=secret
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"2FA setup failed for user {current_user.id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to setup 2FA"
        )


@router.get("/qr-code")
async def get_qr_code(
    current_user: User = Depends(get_current_active_user)
):
    """
    Generate and return QR code image for 2FA setup

    Returns:
        StreamingResponse: QR code image (PNG)
    """
    try:
        if not current_user.two_fa_secret:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="2FA setup not initiated. Call /setup first."
            )

        if current_user.two_fa_enabled:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="2FA is already enabled"
            )

        # Generate QR code
        qr_image_bytes = two_fa_service.generate_qr_code(
            current_user,
            current_user.two_fa_secret
        )

        return StreamingResponse(
            BytesIO(qr_image_bytes),
            media_type="image/png",
            headers={"Content-Disposition": "inline; filename=qr-code.png"}
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"QR code generation failed for user {current_user.id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate QR code"
        )


@router.post("/verify")
async def verify_and_enable_2fa(
    request: TwoFAVerifyRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Verify TOTP code and enable 2FA

    Args:
        request: Verification request with TOTP code

    Returns:
        BackupCodesResponse: Backup codes for user to save
    """
    try:
        if not current_user.two_fa_secret:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="2FA setup not initiated"
            )

        if current_user.two_fa_enabled:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="2FA is already enabled"
            )

        # Verify TOTP code
        if not two_fa_service.verify_totp_code(current_user.two_fa_secret, request.code):
            security_service.log_security_event(
                "2FA_VERIFICATION_FAILED",
                current_user.id,
                f"Invalid TOTP code during setup: {request.code}",
                ""
            )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid verification code"
            )

        # Generate and save backup codes
        backup_codes = two_fa_service.generate_backup_codes()

        # Enable 2FA
        if not two_fa_service.enable_2fa_for_user(
            current_user, current_user.two_fa_secret, backup_codes, db
        ):
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to enable 2FA"
            )

        security_service.log_security_event(
            "2FA_ENABLED",
            current_user.id,
            "2FA successfully enabled",
            ""
        )

        return BackupCodesResponse(
            backup_codes=backup_codes,
            message="2FA has been successfully enabled. Please save these backup codes in a secure location."
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"2FA verification failed for user {current_user.id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to verify and enable 2FA"
        )


@router.post("/disable")
async def disable_2fa(
    request: TwoFADisableRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Disable 2FA for user account

    Args:
        request: Disable request with current password and 2FA code

    Returns:
        dict: Success message
    """
    try:
        if not current_user.two_fa_enabled:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="2FA is not enabled"
            )

        # Verify current password
        from app.core.security import verify_password
        if not verify_password(request.password, current_user.hashed_password):
            security_service.log_security_event(
                "2FA_DISABLE_FAILED",
                current_user.id,
                "Invalid password during 2FA disable attempt",
                ""
            )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid password"
            )

        # Verify 2FA code
        if not two_fa_service.verify_totp_code(current_user.two_fa_secret, request.code):
            security_service.log_security_event(
                "2FA_DISABLE_FAILED",
                current_user.id,
                f"Invalid TOTP code during disable: {request.code}",
                ""
            )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid 2FA code"
            )

        # Disable 2FA
        if not two_fa_service.disable_2fa_for_user(current_user, db):
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to disable 2FA"
            )

        security_service.log_security_event(
            "2FA_DISABLED",
            current_user.id,
            "2FA successfully disabled",
            ""
        )

        return {"message": "2FA has been successfully disabled"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"2FA disable failed for user {current_user.id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to disable 2FA"
        )


@router.get("/status", response_model=TwoFAStatusResponse)
async def get_2fa_status(
    current_user: User = Depends(get_current_active_user)
):
    """
    Get current 2FA status for user

    Returns:
        TwoFAStatusResponse: Current 2FA status and backup codes count
    """
    backup_codes_count = two_fa_service.get_backup_codes_count(current_user)

    return TwoFAStatusResponse(
        enabled=current_user.two_fa_enabled,
        backup_codes_remaining=backup_codes_count
    )


@router.post("/backup-codes/regenerate", response_model=BackupCodesResponse)
async def regenerate_backup_codes(
    request: TwoFAVerifyRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Generate new backup codes (invalidates old ones)

    Args:
        request: Verification request with TOTP code

    Returns:
        BackupCodesResponse: New backup codes
    """
    try:
        if not current_user.two_fa_enabled:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="2FA is not enabled"
            )

        # Verify TOTP code
        if not two_fa_service.verify_totp_code(current_user.two_fa_secret, request.code):
            security_service.log_security_event(
                "BACKUP_CODES_REGEN_FAILED",
                current_user.id,
                f"Invalid TOTP code during backup codes regeneration: {request.code}",
                ""
            )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid 2FA code"
            )

        # Generate new backup codes
        new_codes = two_fa_service.generate_new_backup_codes(current_user, db)
        if not new_codes:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to generate new backup codes"
            )

        security_service.log_security_event(
            "BACKUP_CODES_REGENERATED",
            current_user.id,
            "Backup codes regenerated",
            ""
        )

        return BackupCodesResponse(
            backup_codes=new_codes,
            message="New backup codes generated. Please save these codes in a secure location."
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Backup codes regeneration failed for user {current_user.id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to regenerate backup codes"
        )