"""
Unit tests for authentication service
Location: Backend/tests/unit/test_auth_service.py

Test Cases Implemented:
- U-01: Valid password hashing - verify bcrypt hash generation
- U-02: Invalid password verification - reject wrong password
- U-03: Valid JWT token generation for authenticated user
- U-04: Expired JWT token validation - reject expired token

See TEST_SPECIFICATION.md for detailed test case specifications.
"""
import pytest
from datetime import datetime, timedelta
from jose import jwt, JWTError

from app.core.security import get_password_hash, verify_password, create_access_token
from app.core.config import settings


@pytest.mark.unit
class TestPasswordHashing:
    """Test U-01: Valid password hashing"""

    def test_password_hash_generation(self):
        """
        Test ID: U-01
        Test valid password hashing with bcrypt
        """
        password = "SecurePass123!"
        hashed = get_password_hash(password)

        # Verify bcrypt format
        assert hashed.startswith("$2b$"), "Hash should start with $2b$ (bcrypt format)"
        assert len(hashed) == 60, "Bcrypt hash should be 60 characters"

        # Verify password can be verified against hash
        assert verify_password(password, hashed) is True, "Password should verify successfully"

    def test_password_hash_uniqueness(self):
        """
        Additional test: Same password generates different hashes (salt)
        """
        password = "SecurePass123!"
        hash1 = get_password_hash(password)
        hash2 = get_password_hash(password)

        # Different hashes due to unique salt
        assert hash1 != hash2, "Same password should generate different hashes"

        # But both should verify
        assert verify_password(password, hash1) is True
        assert verify_password(password, hash2) is True


@pytest.mark.unit
class TestPasswordVerification:
    """Test U-02: Invalid password verification"""

    def test_reject_wrong_password(self):
        """
        Test ID: U-02
        Test that wrong password is rejected
        """
        password = "SecurePass123!"
        hashed = get_password_hash(password)
        wrong_password = "WrongPass"

        # Verify wrong password is rejected
        assert verify_password(wrong_password, hashed) is False, "Wrong password should be rejected"

    def test_reject_empty_password(self):
        """
        Additional test: Reject empty password
        """
        password = "SecurePass123!"
        hashed = get_password_hash(password)

        assert verify_password("", hashed) is False, "Empty password should be rejected"

    def test_reject_case_sensitive(self):
        """
        Additional test: Password verification is case-sensitive
        """
        password = "SecurePass123!"
        hashed = get_password_hash(password)

        assert verify_password("securepass123!", hashed) is False, "Case sensitivity should be enforced"


@pytest.mark.unit
class TestJWTTokenGeneration:
    """Test U-03: Valid JWT token generation"""

    def test_create_access_token_valid(self):
        """
        Test ID: U-03
        Test valid JWT token generation for authenticated user
        """
        user_id = 1
        token = create_access_token(subject=user_id)

        # Verify token is a non-empty string
        assert isinstance(token, str), "Token should be a string"
        assert len(token) > 20, "Token should be a substantial length"

        # Decode and verify claims
        decoded = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )

        assert decoded["sub"] == str(user_id), "Subject should match user_id"
        assert "exp" in decoded, "Token should have expiration claim"
        assert "type" in decoded, "Token should have type claim"
        assert decoded["type"] == "access", "Token type should be 'access'"

    def test_token_expiration_time(self):
        """
        Additional test: Token has correct expiration time
        """
        user_id = 1
        before_creation = datetime.utcnow()
        token = create_access_token(subject=user_id)
        after_creation = datetime.utcnow()

        decoded = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )

        exp_time = datetime.fromtimestamp(decoded["exp"])

        # Calculate expected expiration range
        expected_min = before_creation + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        expected_max = after_creation + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

        # Allow 2 second tolerance
        assert expected_min <= exp_time <= expected_max + timedelta(seconds=2), \
            "Token expiration should match configured time"


@pytest.mark.unit
class TestJWTTokenValidation:
    """Test U-04: Expired JWT token validation"""

    def test_expired_token_rejected(self):
        """
        Test ID: U-04
        Test that expired JWT token is rejected
        """
        user_id = 1

        # Create token that expired 1 hour ago
        expired_time = datetime.utcnow() - timedelta(hours=1)
        token = jwt.encode(
            {
                "sub": str(user_id),
                "exp": expired_time,
                "iat": datetime.utcnow() - timedelta(hours=2)
            },
            settings.SECRET_KEY,
            algorithm=settings.ALGORITHM
        )

        # Verify token is rejected with proper exception
        with pytest.raises(JWTError):
            jwt.decode(
                token,
                settings.SECRET_KEY,
                algorithms=[settings.ALGORITHM]
            )

    def test_tampered_token_rejected(self):
        """
        Additional test: Tampered token signature is rejected
        """
        user_id = 1
        token = create_access_token(subject=user_id)

        # Tamper with token by changing last character
        tampered_token = token[:-1] + ("a" if token[-1] != "a" else "b")

        # Verify tampered token is rejected
        with pytest.raises(JWTError):
            jwt.decode(
                tampered_token,
                settings.SECRET_KEY,
                algorithms=[settings.ALGORITHM]
            )

    def test_invalid_signature_rejected(self):
        """
        Additional test: Token signed with wrong key is rejected
        """
        user_id = 1
        wrong_secret = "wrong_secret_key_12345"

        # Create token with wrong secret
        token = jwt.encode(
            {
                "sub": str(user_id),
                "exp": datetime.utcnow() + timedelta(minutes=15)
            },
            wrong_secret,
            algorithm=settings.ALGORITHM
        )

        # Verify token is rejected when verified with correct secret
        with pytest.raises(JWTError):
            jwt.decode(
                token,
                settings.SECRET_KEY,
                algorithms=[settings.ALGORITHM]
            )
