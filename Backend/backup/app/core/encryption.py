"""
Field-level encryption utilities for sensitive data
"""
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from typing import Optional, Union
import base64
import os
import logging

from .config import settings

logger = logging.getLogger(__name__)


class DataEncryption:
    """Handle field-level encryption for sensitive data"""

    def __init__(self, password: Optional[str] = None):
        """
        Initialize encryption with password-derived key

        Args:
            password: Password for key derivation. Uses SECRET_KEY if not provided.
        """
        self.password = password or settings.SECRET_KEY
        self._fernet = None

    @property
    def fernet(self) -> Fernet:
        """Get Fernet instance, creating it if needed"""
        if self._fernet is None:
            # Generate a salt (in production, store this securely)
            salt = b'resumify_salt_2024'  # TODO: Use random salt in production

            # Derive key from password
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=salt,
                iterations=100000,
            )
            key = base64.urlsafe_b64encode(kdf.derive(self.password.encode()))
            self._fernet = Fernet(key)

        return self._fernet

    def encrypt(self, data: Union[str, bytes]) -> str:
        """
        Encrypt sensitive data

        Args:
            data: Data to encrypt (string or bytes)

        Returns:
            str: Base64 encoded encrypted data
        """
        if isinstance(data, str):
            data = data.encode('utf-8')

        try:
            encrypted_data = self.fernet.encrypt(data)
            return base64.urlsafe_b64encode(encrypted_data).decode('utf-8')
        except Exception as e:
            logger.error(f"Encryption failed: {e}")
            raise

    def decrypt(self, encrypted_data: str) -> str:
        """
        Decrypt sensitive data

        Args:
            encrypted_data: Base64 encoded encrypted data

        Returns:
            str: Decrypted data as string
        """
        try:
            # Decode from base64
            encrypted_bytes = base64.urlsafe_b64decode(encrypted_data.encode('utf-8'))

            # Decrypt
            decrypted_bytes = self.fernet.decrypt(encrypted_bytes)
            return decrypted_bytes.decode('utf-8')
        except Exception as e:
            logger.error(f"Decryption failed: {e}")
            raise

    def is_encrypted(self, data: str) -> bool:
        """
        Check if data appears to be encrypted (base64 format check)

        Args:
            data: Data to check

        Returns:
            bool: True if data appears encrypted, False otherwise
        """
        try:
            # Check if it's valid base64
            decoded = base64.urlsafe_b64decode(data.encode('utf-8'))
            # Try to decrypt to verify it's our encryption
            self.fernet.decrypt(decoded)
            return True
        except:
            return False


# Global encryption instance
encryptor = DataEncryption()


def encrypt_pii(data: str) -> str:
    """
    Encrypt personally identifiable information

    Args:
        data: PII data to encrypt

    Returns:
        str: Encrypted data
    """
    return encryptor.encrypt(data)


def decrypt_pii(encrypted_data: str) -> str:
    """
    Decrypt personally identifiable information

    Args:
        encrypted_data: Encrypted PII data

    Returns:
        str: Decrypted data
    """
    return encryptor.decrypt(encrypted_data)


def encrypt_resume_content(content: str) -> str:
    """
    Encrypt resume content

    Args:
        content: Resume text content

    Returns:
        str: Encrypted content
    """
    return encrypt_pii(content)


def decrypt_resume_content(encrypted_content: str) -> str:
    """
    Decrypt resume content

    Args:
        encrypted_content: Encrypted resume content

    Returns:
        str: Decrypted content
    """
    return decrypt_pii(encrypted_content)


def mask_sensitive_data(data: str, mask_char: str = "*", visible_chars: int = 3) -> str:
    """
    Mask sensitive data for display purposes (for logs, non-production environments)

    Args:
        data: Sensitive data to mask
        mask_char: Character to use for masking
        visible_chars: Number of characters to leave visible at start/end

    Returns:
        str: Masked data
    """
    if len(data) <= visible_chars * 2:
        return mask_char * len(data)

    start = data[:visible_chars]
    end = data[-visible_chars:]
    middle = mask_char * (len(data) - visible_chars * 2)

    return f"{start}{middle}{end}"