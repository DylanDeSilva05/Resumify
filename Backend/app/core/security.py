"""
Security utilities for authentication and authorization
"""
from datetime import datetime, timedelta
from typing import Optional, Union, Dict, Any
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import HTTPException, status
import logging
import re
import redis
from .config import settings

logger = logging.getLogger(__name__)

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Redis client for session management and rate limiting
try:
    redis_client = redis.from_url(settings.REDIS_URL, decode_responses=True)
    # Test connection
    redis_client.ping()
    REDIS_AVAILABLE = True
except Exception as e:
    logger.warning(f"Redis not available: {e}. Some security features will use in-memory fallback.")
    redis_client = None
    REDIS_AVAILABLE = False


def create_access_token(
    subject: Union[str, int], expires_delta: Optional[timedelta] = None
) -> str:
    """
    Create JWT access token

    Args:
        subject: Subject to encode in token (usually user_id)
        expires_delta: Token expiration time

    Returns:
        str: Encoded JWT token
    """
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )

    to_encode = {"exp": expire, "sub": str(subject), "type": "access"}
    encoded_jwt = jwt.encode(
        to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM
    )
    return encoded_jwt


def create_refresh_token(subject: Union[str, int]) -> str:
    """
    Create JWT refresh token

    Args:
        subject: Subject to encode in token (usually user_id)

    Returns:
        str: Encoded JWT refresh token
    """
    expire = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode = {"exp": expire, "sub": str(subject), "type": "refresh"}
    encoded_jwt = jwt.encode(
        to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM
    )
    return encoded_jwt


def verify_token(token: str, token_type: str = "access") -> Optional[str]:
    """
    Verify JWT token and extract subject

    Args:
        token: JWT token to verify
        token_type: Type of token ("access" or "refresh")

    Returns:
        str: Subject from token if valid, None otherwise
    """
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        user_id: str = payload.get("sub")
        token_type_claim: str = payload.get("type")

        if user_id is None or token_type_claim != token_type:
            return None

        # Check if token is blacklisted
        if is_token_blacklisted(token):
            return None

        return user_id
    except JWTError as e:
        logger.warning(f"JWT verification failed: {e}")
        return None


def get_password_hash(password: str) -> str:
    """
    Hash password using bcrypt

    Args:
        password: Plain text password

    Returns:
        str: Hashed password
    """
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify password against hash

    Args:
        plain_password: Plain text password
        hashed_password: Hashed password

    Returns:
        bool: True if password matches, False otherwise
    """
    return pwd_context.verify(plain_password, hashed_password)


def validate_password_strength(password: str) -> Dict[str, Any]:
    """
    Validate password strength according to security requirements

    Args:
        password: Plain text password to validate

    Returns:
        dict: Validation result with is_valid flag and error messages
    """
    errors = []
    is_valid = True

    if not settings.REQUIRE_STRONG_PASSWORDS:
        return {"is_valid": True, "errors": []}

    # Minimum length
    if len(password) < 8:
        errors.append("Password must be at least 8 characters long")
        is_valid = False

    # Maximum length
    if len(password) > 128:
        errors.append("Password must be less than 128 characters long")
        is_valid = False

    # Must contain uppercase letter
    if not re.search(r'[A-Z]', password):
        errors.append("Password must contain at least one uppercase letter")
        is_valid = False

    # Must contain lowercase letter
    if not re.search(r'[a-z]', password):
        errors.append("Password must contain at least one lowercase letter")
        is_valid = False

    # Must contain digit
    if not re.search(r'\d', password):
        errors.append("Password must contain at least one digit")
        is_valid = False

    # Must contain special character
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        errors.append("Password must contain at least one special character")
        is_valid = False

    # Common password check
    common_passwords = ["password", "123456", "password123", "admin", "letmein"]
    if password.lower() in common_passwords:
        errors.append("Password is too common")
        is_valid = False

    return {"is_valid": is_valid, "errors": errors}


# In-memory storage for when Redis is not available
_in_memory_cache = {}

def track_login_attempt(user_identifier: str, success: bool) -> None:
    """
    Track login attempts for rate limiting

    Args:
        user_identifier: Username, email, or IP address
        success: Whether the login was successful
    """
    if not REDIS_AVAILABLE:
        # Fallback to in-memory storage
        if success:
            _in_memory_cache.pop(f"login_attempts:{user_identifier}", None)
        else:
            key = f"login_attempts:{user_identifier}"
            current = _in_memory_cache.get(key, 0)
            _in_memory_cache[key] = current + 1
        return

    key = f"login_attempts:{user_identifier}"

    if success:
        # Clear failed attempts on successful login
        redis_client.delete(key)
    else:
        # Increment failed attempts
        current_attempts = redis_client.incr(key)
        if current_attempts == 1:
            # Set expiration on first failure
            redis_client.expire(key, settings.LOCKOUT_DURATION_MINUTES * 60)


def is_account_locked(user_identifier: str) -> bool:
    """
    Check if account is locked due to too many failed login attempts

    Args:
        user_identifier: Username, email, or IP address

    Returns:
        bool: True if account is locked, False otherwise
    """
    if not REDIS_AVAILABLE:
        # Fallback to in-memory storage
        key = f"login_attempts:{user_identifier}"
        attempts = _in_memory_cache.get(key, 0)
        return attempts >= settings.MAX_LOGIN_ATTEMPTS

    key = f"login_attempts:{user_identifier}"
    attempts = redis_client.get(key)

    if attempts is None:
        return False

    return int(attempts) >= settings.MAX_LOGIN_ATTEMPTS


def blacklist_token(token: str) -> None:
    """
    Add token to blacklist (for logout)

    Args:
        token: JWT token to blacklist
    """
    if not REDIS_AVAILABLE:
        # Fallback to in-memory storage
        _in_memory_cache[f"blacklisted_token:{token}"] = True
        return

    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        exp = payload.get("exp")
        if exp:
            # Calculate remaining time until expiration
            exp_datetime = datetime.fromtimestamp(exp)
            remaining_time = exp_datetime - datetime.utcnow()
            if remaining_time.total_seconds() > 0:
                redis_client.setex(
                    f"blacklisted_token:{token}",
                    int(remaining_time.total_seconds()),
                    "true"
                )
    except JWTError:
        pass


def is_token_blacklisted(token: str) -> bool:
    """
    Check if token is blacklisted

    Args:
        token: JWT token to check

    Returns:
        bool: True if token is blacklisted, False otherwise
    """
    if not REDIS_AVAILABLE:
        # Fallback to in-memory storage
        return _in_memory_cache.get(f"blacklisted_token:{token}", False)

    return redis_client.exists(f"blacklisted_token:{token}") > 0


def refresh_access_token(refresh_token: str) -> Optional[str]:
    """
    Generate new access token from refresh token

    Args:
        refresh_token: Valid refresh token

    Returns:
        str: New access token if refresh token is valid, None otherwise
    """
    user_id = verify_token(refresh_token, token_type="refresh")
    if user_id:
        return create_access_token(subject=user_id)
    return None


# Simple encryption/decryption for SMTP passwords
# Using base64 encoding for simplicity (in production, use proper encryption like Fernet)
import base64


def encrypt_password(password: str) -> str:
    """
    Encrypt password for storage

    Args:
        password: Plain text password

    Returns:
        str: Encrypted password
    """
    # In production, use proper encryption library like cryptography.fernet
    # For now, using base64 encoding with SECRET_KEY as salt
    key = settings.SECRET_KEY.encode()
    password_bytes = password.encode()

    # Simple XOR encryption with key cycling
    encrypted = bytearray()
    for i, byte in enumerate(password_bytes):
        encrypted.append(byte ^ key[i % len(key)])

    return base64.b64encode(encrypted).decode()


def decrypt_password(encrypted_password: str) -> str:
    """
    Decrypt password from storage

    Args:
        encrypted_password: Encrypted password

    Returns:
        str: Decrypted password
    """
    # Decrypt using same XOR method
    key = settings.SECRET_KEY.encode()
    encrypted_bytes = base64.b64decode(encrypted_password.encode())

    # XOR decryption
    decrypted = bytearray()
    for i, byte in enumerate(encrypted_bytes):
        decrypted.append(byte ^ key[i % len(key)])

    return decrypted.decode()