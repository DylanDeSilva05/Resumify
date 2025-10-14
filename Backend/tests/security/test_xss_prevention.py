"""
Security tests for XSS prevention
Location: Backend/tests/security/test_xss_prevention.py

Test Cases Implemented:
- S-02: XSS prevention in user profile update

See TEST_SPECIFICATION.md for detailed test case specifications.
"""
import pytest
from fastapi import status


@pytest.mark.security
class TestXSSPrevention:
    """Test S-02: XSS prevention in user profile update"""

    def test_xss_in_profile_update(self, client, auth_headers_candidate, sample_candidate_user, db_session):
        """
        Test ID: S-02
        Test that XSS payloads are sanitized or escaped
        """
        xss_payloads = [
            "<script>alert('XSS')</script>",
            "<img src=x onerror=alert('XSS')>",
            "<svg onload=alert('XSS')>",
            "javascript:alert('XSS')",
            "<iframe src='javascript:alert(\"XSS\")'>"
        ]

        for payload in xss_payloads:
            profile_data = {
                "full_name": payload
            }

            response = client.put(
                "/api/v1/profile/me",
                json=profile_data,
                headers=auth_headers_candidate
            )

            # Request should be accepted (sanitization happens server-side)
            if response.status_code == status.HTTP_200_OK:
                # Verify XSS payload is sanitized in database
                db_session.expire_all()
                from app.models.user import User
                user = db_session.query(User).filter(User.id == sample_candidate_user.id).first()

                # Check that dangerous script tags are removed or escaped
                assert "<script>" not in user.full_name, \
                    f"Script tags should be removed/escaped, got: {user.full_name}"
                assert "javascript:" not in user.full_name.lower(), \
                    f"JavaScript protocol should be removed, got: {user.full_name}"

    def test_xss_in_job_description(self, client, auth_headers_company_admin, sample_company):
        """
        Additional test: XSS in job description
        """
        xss_payload = "<script>steal_cookies()</script>"

        job_data = {
            "title": "Test Job",
            "description": xss_payload,
            "company_id": sample_company.id,
            "requirements": ["Python"]
        }

        response = client.post(
            "/api/v1/jobs/",
            json=job_data,
            headers=auth_headers_company_admin
        )

        # Verify script tags are sanitized if job is created
        if response.status_code in [200, 201]:
            data = response.json()
            if "description" in data:
                assert "<script>" not in data["description"], \
                    "Script tags should be sanitized in response"
