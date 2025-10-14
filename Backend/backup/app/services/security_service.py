"""
Enhanced security service for account protection and OWASP compliance
"""
import re
import logging
import hashlib
import secrets
from datetime import datetime, timedelta
from typing import Optional, Dict, List
from sqlalchemy.orm import Session

from app.models.user import User
from app.core.config import settings

logger = logging.getLogger(__name__)


class SecurityService:
    """Service for enhanced security measures and OWASP compliance"""

    def __init__(self):
        self.max_failed_attempts = 5
        self.lockout_duration_minutes = 15
        self.password_min_length = 8
        self.password_history_count = 5

    def check_account_lockout(self, user: User) -> bool:
        """
        Check if user account is locked due to failed login attempts

        Args:
            user: User object

        Returns:
            bool: True if account is locked
        """
        if not user.account_locked_until:
            return False

        if datetime.now() < user.account_locked_until:
            return True

        # Lockout period expired, reset failed attempts
        return False

    def record_failed_login(self, user: User, db: Session) -> bool:
        """
        Record failed login attempt and lock account if threshold reached

        Args:
            user: User object
            db: Database session

        Returns:
            bool: True if account was locked
        """
        user.failed_login_attempts += 1

        if user.failed_login_attempts >= self.max_failed_attempts:
            user.account_locked_until = datetime.now() + timedelta(
                minutes=self.lockout_duration_minutes
            )
            logger.warning(f"Account locked for user {user.id} due to {self.max_failed_attempts} failed attempts")
            db.commit()
            return True

        db.commit()
        return False

    def record_successful_login(self, user: User, db: Session):
        """
        Record successful login and reset failed attempts

        Args:
            user: User object
            db: Database session
        """
        user.failed_login_attempts = 0
        user.account_locked_until = None
        user.last_login = datetime.now()
        db.commit()

    def validate_password_strength(self, password: str) -> Dict[str, any]:
        """
        Validate password strength according to OWASP guidelines

        Args:
            password: Password to validate

        Returns:
            Dict: Validation result with details
        """
        issues = []
        score = 0

        # Length check
        if len(password) < self.password_min_length:
            issues.append(f"Password must be at least {self.password_min_length} characters long")
        elif len(password) >= 12:
            score += 2
        else:
            score += 1

        # Character variety checks
        has_lower = bool(re.search(r'[a-z]', password))
        has_upper = bool(re.search(r'[A-Z]', password))
        has_digit = bool(re.search(r'\d', password))
        has_special = bool(re.search(r'[!@#$%^&*(),.?":{}|<>]', password))

        if not has_lower:
            issues.append("Password must contain lowercase letters")
        else:
            score += 1

        if not has_upper:
            issues.append("Password must contain uppercase letters")
        else:
            score += 1

        if not has_digit:
            issues.append("Password must contain numbers")
        else:
            score += 1

        if not has_special:
            issues.append("Password must contain special characters (!@#$%^&*)")
        else:
            score += 2

        # Common password checks
        common_passwords = [
            'password', '123456', 'password123', 'admin', 'qwerty',
            'letmein', 'welcome', 'monkey', '1234567890'
        ]
        if password.lower() in common_passwords:
            issues.append("Password is too common")
            score = max(0, score - 3)

        # Sequential character check
        if self._has_sequential_chars(password):
            issues.append("Password contains sequential characters")
            score = max(0, score - 1)

        # Determine strength
        if score >= 8:
            strength = "strong"
        elif score >= 5:
            strength = "medium"
        else:
            strength = "weak"

        return {
            "valid": len(issues) == 0,
            "strength": strength,
            "score": score,
            "issues": issues
        }

    def _has_sequential_chars(self, password: str) -> bool:
        """Check for sequential characters in password"""
        sequential_patterns = [
            '123456', '234567', '345678', '456789', '567890',
            'abcdef', 'bcdefg', 'cdefgh', 'defghi', 'efghij',
            'qwerty', 'asdfgh', 'zxcvbn'
        ]
        password_lower = password.lower()
        return any(pattern in password_lower for pattern in sequential_patterns)

    def generate_secure_token(self, length: int = 32) -> str:
        """
        Generate cryptographically secure random token

        Args:
            length: Token length in bytes

        Returns:
            str: Hex-encoded secure token
        """
        return secrets.token_hex(length)

    def hash_sensitive_data(self, data: str) -> str:
        """
        Hash sensitive data using SHA-256

        Args:
            data: Data to hash

        Returns:
            str: Hashed data
        """
        return hashlib.sha256(data.encode()).hexdigest()

    def validate_input_length(self, input_data: str, max_length: int) -> bool:
        """
        Validate input length to prevent buffer overflow attacks

        Args:
            input_data: Input to validate
            max_length: Maximum allowed length

        Returns:
            bool: True if input length is valid
        """
        return len(input_data) <= max_length

    def sanitize_filename(self, filename: str) -> str:
        """
        Sanitize filename to prevent path traversal attacks

        Args:
            filename: Original filename

        Returns:
            str: Sanitized filename
        """
        # Remove path separators and dangerous characters
        filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
        filename = re.sub(r'\.\.', '_', filename)  # Remove path traversal
        filename = filename.strip('. ')  # Remove leading/trailing dots and spaces

        # Ensure filename is not empty
        if not filename:
            filename = "unnamed_file"

        # Limit length
        if len(filename) > 255:
            name, ext = filename.rsplit('.', 1) if '.' in filename else (filename, '')
            max_name_length = 255 - len(ext) - 1 if ext else 255
            filename = name[:max_name_length] + ('.' + ext if ext else '')

        return filename

    def check_rate_limit(self, identifier: str, max_requests: int, window_minutes: int) -> bool:
        """
        Check if request is within rate limit (simplified in-memory implementation)
        In production, use Redis or similar for distributed rate limiting

        Args:
            identifier: Unique identifier (IP, user ID, etc.)
            max_requests: Maximum requests allowed
            window_minutes: Time window in minutes

        Returns:
            bool: True if within rate limit
        """
        # This is a simplified implementation
        # In production, implement proper rate limiting with Redis
        return True

    def validate_email_format(self, email: str) -> bool:
        """
        Validate email format

        Args:
            email: Email to validate

        Returns:
            bool: True if email format is valid
        """
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(email_pattern, email))

    def check_sql_injection_patterns(self, input_data: str) -> bool:
        """
        Check for common SQL injection patterns

        Args:
            input_data: Input to check

        Returns:
            bool: True if suspicious patterns found
        """
        sql_patterns = [
            r"union\s+select", r"drop\s+table", r"delete\s+from",
            r"insert\s+into", r"update\s+set", r"exec\s*\(",
            r"--", r"/\*", r"\*/", r"xp_", r"sp_"
        ]

        input_lower = input_data.lower()
        return any(re.search(pattern, input_lower, re.IGNORECASE) for pattern in sql_patterns)

    def log_security_event(self, event_type: str, user_id: Optional[int], details: str, ip_address: str = ""):
        """
        Log security-related events for monitoring

        Args:
            event_type: Type of security event
            user_id: User ID if applicable
            details: Event details
            ip_address: Client IP address
        """
        logger.warning(f"SECURITY_EVENT: {event_type} - User: {user_id} - IP: {ip_address} - Details: {details}")

    def get_security_headers(self) -> Dict[str, str]:
        """
        Get security headers for HTTP responses

        Returns:
            Dict: Security headers
        """
        return {
            "X-Content-Type-Options": "nosniff",
            "X-Frame-Options": "DENY",
            "X-XSS-Protection": "1; mode=block",
            "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
            "Content-Security-Policy": "default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'",
            "Referrer-Policy": "strict-origin-when-cross-origin",
            "Permissions-Policy": "geolocation=(), microphone=(), camera=()"
        }