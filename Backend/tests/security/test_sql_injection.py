"""
Security tests for SQL injection prevention
Location: Backend/tests/security/test_sql_injection.py

Test Cases Implemented:
- S-01: SQL Injection prevention in login endpoint

See TEST_SPECIFICATION.md for detailed test case specifications.
"""
import pytest
from fastapi import status


@pytest.mark.security
class TestSQLInjectionPrevention:
    """Test S-01: SQL Injection prevention in login endpoint"""

    def test_login_sql_injection_attempt(self, client):
        """
        Test ID: S-01
        Test that SQL injection attacks are prevented
        """
        # Common SQL injection payloads
        injection_payloads = [
            {"username": "admin' OR '1'='1", "password": "anything"},
            {"username": "admin'--", "password": ""},
            {"username": "' OR '1'='1' /*", "password": "test"},
            {"username": "admin'; DROP TABLE users;--", "password": "test"},
            {"username": "admin' OR 1=1--", "password": ""},
            {"username": "' UNION SELECT NULL, NULL, NULL--", "password": "test"}
        ]

        for payload in injection_payloads:
            response = client.post("/api/v1/auth/login", data=payload)

            # Should reject with 401, not 500 (which would indicate SQL error)
            assert response.status_code == status.HTTP_401_UNAUTHORIZED, \
                f"SQL injection attempt should return 401, got {response.status_code} for payload: {payload}"

            # Verify no authentication occurred
            data = response.json()
            assert "access_token" not in data, \
                f"SQL injection should not grant access for payload: {payload}"

    def test_sql_injection_in_search(self, client, auth_headers_company_admin):
        """
        Additional test: SQL injection in search endpoints
        """
        injection_payloads = [
            "?name=test' OR '1'='1",
            "?email=admin@test.com'; DROP TABLE users;--",
            "?skills=Python' UNION SELECT password FROM users--"
        ]

        for payload in injection_payloads:
            response = client.get(
                f"/api/v1/candidates/search{payload}",
                headers=auth_headers_company_admin
            )

            # Should not cause server error
            assert response.status_code != status.HTTP_500_INTERNAL_SERVER_ERROR, \
                f"SQL injection should not cause server error for: {payload}"
