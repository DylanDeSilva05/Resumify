"""
Two-Factor Authentication (2FA) service using TOTP (Time-based One-Time Password)
Compatible with Google Authenticator, Authy, and other TOTP apps
"""
import pyotp
import qrcode
import json
import secrets
import logging
from io import BytesIO
from typing import List, Tuple, Optional
from sqlalchemy.orm import Session

from app.models.user import User
from app.core.config import settings

logger = logging.getLogger(__name__)


class TwoFAService:
    """Service for managing Two-Factor Authentication"""

    def __init__(self):
        self.app_name = "Resumify HR System"

    def generate_secret_key(self) -> str:
        """Generate a new TOTP secret key"""
        return pyotp.random_base32()

    def generate_qr_code(self, user: User, secret: str) -> bytes:
        """
        Generate QR code for setting up 2FA in authenticator apps

        Args:
            user: User object
            secret: TOTP secret key

        Returns:
            bytes: QR code image as PNG bytes
        """
        # Create TOTP URI for authenticator apps
        totp_uri = pyotp.totp.TOTP(secret).provisioning_uri(
            name=user.email,
            issuer_name=self.app_name
        )

        # Generate QR code
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(totp_uri)
        qr.make(fit=True)

        # Create image
        img = qr.make_image(fill_color="black", back_color="white")

        # Convert to bytes
        byte_io = BytesIO()
        img.save(byte_io, format='PNG')
        byte_io.seek(0)
        return byte_io.getvalue()

    def generate_backup_codes(self, count: int = 10) -> List[str]:
        """
        Generate backup codes for account recovery

        Args:
            count: Number of backup codes to generate

        Returns:
            List[str]: List of backup codes
        """
        codes = []
        for _ in range(count):
            # Generate 8-character alphanumeric backup codes
            code = secrets.token_hex(4).upper()
            # Format as XXXX-XXXX for readability
            formatted_code = f"{code[:4]}-{code[4:]}"
            codes.append(formatted_code)
        return codes

    def verify_totp_code(self, secret: str, code: str, window: int = 1) -> bool:
        """
        Verify TOTP code from authenticator app

        Args:
            secret: User's TOTP secret key
            code: 6-digit code from authenticator app
            window: Time window tolerance (default 1 = ±30 seconds)

        Returns:
            bool: True if code is valid
        """
        try:
            totp = pyotp.TOTP(secret)
            return totp.verify(code, valid_window=window)
        except Exception as e:
            logger.error(f"TOTP verification failed: {e}")
            return False

    def verify_backup_code(self, user: User, code: str, db: Session) -> bool:
        """
        Verify and consume a backup code

        Args:
            user: User object
            code: Backup code to verify
            db: Database session

        Returns:
            bool: True if backup code is valid and consumed
        """
        if not user.backup_codes:
            return False

        try:
            backup_codes = json.loads(user.backup_codes)
            code_upper = code.upper().strip()

            if code_upper in backup_codes:
                # Remove used backup code
                backup_codes.remove(code_upper)
                user.backup_codes = json.dumps(backup_codes)
                db.commit()

                logger.info(f"Backup code used for user {user.id}")
                return True

        except (json.JSONDecodeError, ValueError) as e:
            logger.error(f"Error processing backup codes for user {user.id}: {e}")

        return False

    def enable_2fa_for_user(
        self,
        user: User,
        secret: str,
        backup_codes: List[str],
        db: Session
    ) -> bool:
        """
        Enable 2FA for a user

        Args:
            user: User object
            secret: TOTP secret key
            backup_codes: List of backup codes
            db: Database session

        Returns:
            bool: True if 2FA was successfully enabled
        """
        try:
            user.two_fa_secret = secret
            user.backup_codes = json.dumps(backup_codes)
            user.two_fa_enabled = True
            db.commit()

            logger.info(f"2FA enabled for user {user.id}")
            return True

        except Exception as e:
            logger.error(f"Failed to enable 2FA for user {user.id}: {e}")
            db.rollback()
            return False

    def disable_2fa_for_user(self, user: User, db: Session) -> bool:
        """
        Disable 2FA for a user

        Args:
            user: User object
            db: Database session

        Returns:
            bool: True if 2FA was successfully disabled
        """
        try:
            user.two_fa_enabled = False
            user.two_fa_secret = None
            user.backup_codes = None
            db.commit()

            logger.info(f"2FA disabled for user {user.id}")
            return True

        except Exception as e:
            logger.error(f"Failed to disable 2FA for user {user.id}: {e}")
            db.rollback()
            return False

    def generate_new_backup_codes(self, user: User, db: Session) -> Optional[List[str]]:
        """
        Generate new backup codes for a user (invalidates old ones)

        Args:
            user: User object
            db: Database session

        Returns:
            Optional[List[str]]: New backup codes if successful
        """
        if not user.two_fa_enabled:
            return None

        try:
            new_codes = self.generate_backup_codes()
            user.backup_codes = json.dumps(new_codes)
            db.commit()

            logger.info(f"New backup codes generated for user {user.id}")
            return new_codes

        except Exception as e:
            logger.error(f"Failed to generate new backup codes for user {user.id}: {e}")
            db.rollback()
            return None

    def get_backup_codes_count(self, user: User) -> int:
        """
        Get remaining backup codes count

        Args:
            user: User object

        Returns:
            int: Number of remaining backup codes
        """
        if not user.backup_codes:
            return 0

        try:
            backup_codes = json.loads(user.backup_codes)
            return len(backup_codes)
        except (json.JSONDecodeError, ValueError):
            return 0

    def is_2fa_required(self, user: User) -> bool:
        """
        Check if 2FA is required for this user

        Args:
            user: User object

        Returns:
            bool: True if 2FA is enabled and required
        """
        return user.two_fa_enabled and user.two_fa_secret is not None