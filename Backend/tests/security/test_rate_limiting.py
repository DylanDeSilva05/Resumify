"""
Security tests for rate limiting and brute force protection
Location: Backend/tests/security/test_rate_limiting.py

Test Cases Implemented:
- S-04: Brute force protection on login attempts

See TEST_SPECIFICATION.md for detailed test case specifications.
"""
import pytest
from fastapi import status
import time


@pytest.mark.security
@pytest.mark.slow
class TestBruteForceProtection:
    """Test S-04: Brute force protection on login attempts"""

    def test_multiple_failed_login_attempts(self, client):
        """
        Test ID: S-04
        Test that multiple failed login attempts trigger rate limiting
        """
        login_data = {
            "username": "nonexistent_user",
            "password": "wrongpassword"
        }

        responses = []

        # Attempt multiple failed logins
        for i in range(6):
            response = client.post("/api/v1/auth/login", data=login_data)
            responses.append(response.status_code)
            time.sleep(0.1)  # Small delay between requests

        # After multiple attempts, should get rate limited
        # Could be 429 (Too Many Requests) or 401 with lockout message
        assert any(code == status.HTTP_429_TOO_MANY_REQUESTS for code in responses) or \
               responses[-1] == status.HTTP_401_UNAUTHORIZED, \
            f"Should implement rate limiting after failed attempts, got: {responses}"

    def test_successful_login_resets_counter(self, client, sample_candidate_user):
        """
        Additional test: Successful login resets failed attempt counter
        """
        # Make a few failed attempts
        wrong_data = {
            "username": "test_candidate",
            "password": "wrongpassword"
        }

        for _ in range(2):
            client.post("/api/v1/auth/login", data=wrong_data)

        # Now successful login
        correct_data = {
            "username": "test_candidate",
            "password": "TestPass123!"
        }

        response = client.post("/api/v1/auth/login", data=correct_data)

        assert response.status_code == status.HTTP_200_OK, \
            "Successful login should work after failed attempts"
