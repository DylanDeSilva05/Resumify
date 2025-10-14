"""
Unit tests for input validators
Location: Backend/tests/unit/test_validators.py

Test Cases Implemented:
- U-07: Email validation - valid email format
- U-08: Email validation - invalid email format

See TEST_SPECIFICATION.md for detailed test case specifications.
"""
import pytest
from pydantic import EmailStr, ValidationError
from pydantic import BaseModel


class EmailModel(BaseModel):
    """Simple model for email validation"""
    email: EmailStr


@pytest.mark.unit
class TestEmailValidation:
    """Test U-07: Email validation - valid email format"""

    def test_valid_email_formats(self):
        """
        Test ID: U-07
        Test that valid email formats are accepted
        """
        valid_emails = [
            "candidate@resumify.com",
            "user.name@example.com",
            "test+tag@domain.co.uk",
            "firstname.lastname@company.org",
            "email123@test-domain.com"
        ]

        for email in valid_emails:
            try:
                model = EmailModel(email=email)
                assert model.email == email, f"Email {email} should be valid"
            except ValidationError:
                pytest.fail(f"Valid email {email} was rejected")

    def test_email_case_insensitive(self):
        """
        Additional test: Email validation is case-insensitive
        """
        email = "User@Example.COM"

        try:
            model = EmailModel(email=email)
            # Pydantic normalizes email to lowercase
            assert model.email.lower() == email.lower()
        except ValidationError:
            pytest.fail(f"Email {email} should be valid")


@pytest.mark.unit
class TestEmailValidationInvalid:
    """Test U-08: Email validation - invalid email format"""

    def test_invalid_email_formats(self):
        """
        Test ID: U-08
        Test that invalid email formats are rejected
        """
        invalid_emails = [
            "invalid-email",  # No @ symbol
            "@example.com",  # Missing local part
            "user@",  # Missing domain
            "user @example.com",  # Space in local part
            "user@.com",  # Missing domain name
            "user..name@example.com",  # Consecutive dots
            "user@example",  # Missing TLD
            "",  # Empty string
            "user@exam ple.com",  # Space in domain
        ]

        for email in invalid_emails:
            with pytest.raises(ValidationError) as exc_info:
                EmailModel(email=email)

            # Verify error message mentions email or validation
            error_message = str(exc_info.value).lower()
            assert "email" in error_message or "value" in error_message, \
                f"Error message should mention email validation for: {email}"

    def test_none_email_rejected(self):
        """
        Additional test: None value is rejected
        """
        with pytest.raises(ValidationError):
            EmailModel(email=None)

    def test_numeric_email_rejected(self):
        """
        Additional test: Numeric value is rejected
        """
        with pytest.raises(ValidationError):
            EmailModel(email=12345)


@pytest.mark.unit
class TestPasswordValidation:
    """Additional tests for password validation"""

    def test_password_complexity_valid(self):
        """
        Test valid password complexity
        """
        from app.core.security import validate_password_strength

        valid_passwords = [
            "SecurePass123!",
            "MyP@ssw0rd",
            "Strong#Pass99",
            "C0mpl3x!ty"
        ]

        for password in valid_passwords:
            result = validate_password_strength(password)
            assert result["is_valid"] is True, f"Password {password} should be valid"
            assert len(result["errors"]) == 0, "No errors should be present"

    def test_password_complexity_invalid(self):
        """
        Test invalid password complexity
        """
        from app.core.security import validate_password_strength

        invalid_passwords = [
            "12345",  # Too short, no letters
            "password",  # No numbers or special chars
            "PASSWORD123",  # No special chars
            "Pass1!",  # Too short
        ]

        for password in invalid_passwords:
            result = validate_password_strength(password)
            assert result["is_valid"] is False, f"Password {password} should be invalid"
            assert len(result["errors"]) > 0, "Errors should be present"


@pytest.mark.unit
class TestUsernameValidation:
    """Additional tests for username validation"""

    def test_valid_usernames(self):
        """Test valid username formats"""
        valid_usernames = [
            "user123",
            "john_doe",
            "testuser",
            "candidate_2023"
        ]

        # Username validation logic (alphanumeric and underscore)
        import re
        username_pattern = r'^[a-zA-Z0-9_]{3,30}$'

        for username in valid_usernames:
            assert re.match(username_pattern, username), \
                f"Username {username} should be valid"

    def test_invalid_usernames(self):
        """Test invalid username formats"""
        invalid_usernames = [
            "ab",  # Too short
            "user with spaces",  # Spaces
            "user@name",  # Special chars
            "a" * 31,  # Too long
        ]

        import re
        username_pattern = r'^[a-zA-Z0-9_]{3,30}$'

        for username in invalid_usernames:
            assert not re.match(username_pattern, username), \
                f"Username {username} should be invalid"
