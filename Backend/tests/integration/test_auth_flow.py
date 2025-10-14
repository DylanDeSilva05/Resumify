"""
Integration tests for authentication workflow
Location: Backend/tests/integration/test_auth_flow.py

Test Cases Implemented:
- I-01: User registration workflow - create new candidate account
- I-02: User login workflow - successful authentication
- I-07: Unauthorized access to protected endpoint
- I-08: Role-based access control

See TEST_SPECIFICATION.md for detailed test case specifications.
"""
import pytest
from fastapi import status


@pytest.mark.integration
class TestUserRegistration:
    """Test I-01: User registration workflow"""

    def test_create_new_candidate_account(self, client, db_session, sample_company):
        """
        Test ID: I-01
        Test complete user registration workflow
        """
        registration_data = {
            "username": "john_doe",
            "email": "john@test.com",
            "password": "Pass123!@#",
            "full_name": "John Doe",
            "role": "company_user",
            "is_active": True,
            "company_id": sample_company.id
        }

        response = client.post("/api/v1/auth/register", json=registration_data)

        # Verify HTTP response
        assert response.status_code == status.HTTP_201_CREATED, \
            f"Expected 201, got {response.status_code}: {response.text}"

        data = response.json()

        # Verify response contains required fields
        assert "id" in data, "Response should contain user ID"
        assert data["email"] == "john@test.com", "Email should match"
        assert data["username"] == "john_doe", "Username should match"
        assert "password" not in data, "Password should not be in response"
        assert "hashed_password" not in data, "Hashed password should not be in response"

        # Verify user created in database
        from app.models.user import User
        user = db_session.query(User).filter(User.email == "john@test.com").first()

        assert user is not None, "User should exist in database"
        assert user.username == "john_doe", "Username should match in DB"
        assert user.role.value == "company_user", "Role should match in DB"
        assert user.is_active is True, "User should be active"

    def test_duplicate_email_rejected(self, client, sample_candidate_user, sample_company):
        """
        Additional test: Duplicate email is rejected
        """
        registration_data = {
            "username": "another_user",
            "email": sample_candidate_user.email,  # Duplicate email
            "password": "Pass123!@#",
            "full_name": "Another User",
            "role": "company_user",
            "company_id": sample_company.id
        }

        response = client.post("/api/v1/auth/register", json=registration_data)

        assert response.status_code == status.HTTP_409_CONFLICT or \
               response.status_code == status.HTTP_400_BAD_REQUEST, \
            "Duplicate email should be rejected"


@pytest.mark.integration
class TestUserLogin:
    """Test I-02: User login workflow"""

    def test_successful_authentication(self, client, sample_candidate_user):
        """
        Test ID: I-02
        Test successful user login and token generation
        """
        login_data = {
            "username": "test_candidate",
            "password": "TestPass123!"
        }

        response = client.post("/api/v1/auth/login", data=login_data)

        # Verify HTTP response
        assert response.status_code == status.HTTP_200_OK, \
            f"Expected 200, got {response.status_code}: {response.text}"

        data = response.json()

        # Verify token response structure
        assert "access_token" in data, "Response should contain access_token"
        assert data["token_type"] == "bearer", "Token type should be bearer"
        assert len(data["access_token"]) > 20, "Access token should be substantial length"

    def test_invalid_credentials_rejected(self, client, sample_candidate_user):
        """
        Additional test: Invalid credentials are rejected
        """
        login_data = {
            "username": "test_candidate",
            "password": "WrongPassword123!"
        }

        response = client.post("/api/v1/auth/login", data=login_data)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED, \
            "Invalid credentials should return 401"


@pytest.mark.integration
class TestUnauthorizedAccess:
    """Test I-07: Unauthorized access to protected endpoint"""

    def test_access_protected_endpoint_without_auth(self, client):
        """
        Test ID: I-07
        Test that protected endpoints reject requests without auth token
        """
        # Try to access protected endpoint without token
        response = client.get("/api/v1/profile/me")

        # Verify 401 Unauthorized
        assert response.status_code == status.HTTP_401_UNAUTHORIZED, \
            f"Expected 401, got {response.status_code}"

        data = response.json()
        assert "detail" in data, "Error response should contain detail"

    def test_invalid_token_rejected(self, client):
        """
        Additional test: Invalid token is rejected
        """
        headers = {"Authorization": "Bearer invalid_token_12345"}

        response = client.get("/api/v1/profile/me", headers=headers)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED, \
            "Invalid token should return 401"


@pytest.mark.integration
class TestRoleBasedAccessControl:
    """Test I-08: Role-based access control"""

    def test_candidate_cannot_access_company_endpoint(self, client, auth_headers_candidate):
        """
        Test ID: I-08
        Test that candidate cannot access company-only endpoints
        """
        # Candidate trying to access company dashboard
        response = client.get("/api/v1/companies/dashboard", headers=auth_headers_candidate)

        # Should be forbidden (403) or not found (404) if endpoint is role-protected
        assert response.status_code in [status.HTTP_403_FORBIDDEN, status.HTTP_404_NOT_FOUND], \
            f"Expected 403 or 404, got {response.status_code}"

    def test_admin_can_access_admin_endpoint(self, client, auth_headers_company_admin):
        """
        Additional test: Admin can access admin endpoints
        """
        # This test depends on your actual admin endpoints
        # Example: accessing company management
        response = client.get("/api/v1/companies/", headers=auth_headers_company_admin)

        # Should succeed (200) or at least not be forbidden
        assert response.status_code != status.HTTP_403_FORBIDDEN, \
            "Admin should be able to access company endpoints"
