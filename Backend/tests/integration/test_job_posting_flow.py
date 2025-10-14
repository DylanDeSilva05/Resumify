"""
Integration tests for job posting workflow
Location: Backend/tests/integration/test_job_posting_flow.py

Test Cases Implemented:
- I-04: Job posting creation by company user
- I-09: Database transaction rollback on validation error

See TEST_SPECIFICATION.md for detailed test case specifications.
"""
import pytest
from fastapi import status


@pytest.mark.integration
class TestJobPostingCreation:
    """Test I-04: Job posting creation by company user"""

    def test_create_job_posting(self, client, auth_headers_company_admin, sample_company):
        """
        Test ID: I-04
        Test job posting creation workflow
        """
        job_data = {
            "title": "Senior Python Developer",
            "description": "Looking for experienced Python developer",
            "company_id": sample_company.id,
            "requirements": ["Python", "FastAPI", "PostgreSQL"],
            "location": "Remote",
            "salary_range": "100k-150k",
            "employment_type": "Full-time"
        }

        response = client.post(
            "/api/v1/jobs/",
            json=job_data,
            headers=auth_headers_company_admin
        )

        # Verify response
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_201_CREATED], \
            f"Job creation should succeed, got {response.status_code}: {response.text}"

        if response.status_code in [200, 201]:
            data = response.json()
            assert "id" in data or "job_id" in data, "Response should contain job ID"


@pytest.mark.integration
class TestDatabaseTransactionRollback:
    """Test I-09: Database transaction rollback on validation error"""

    def test_invalid_data_rollback(self, client, auth_headers_company_admin, db_session):
        """
        Test ID: I-09
        Test that invalid data doesn't create partial records
        """
        # Get initial job count
        from app.models.job_posting import JobPosting
        initial_count = db_session.query(JobPosting).count()

        # Try to create job with invalid data
        invalid_job_data = {
            "title": "",  # Empty title (invalid)
            "company_id": 9999,  # Non-existent company
            "requirements": []
        }

        response = client.post(
            "/api/v1/jobs/",
            json=invalid_job_data,
            headers=auth_headers_company_admin
        )

        # Verify request failed
        assert response.status_code in [status.HTTP_422_UNPROCESSABLE_ENTITY, status.HTTP_400_BAD_REQUEST], \
            "Invalid data should be rejected"

        # Verify no job was created (transaction rolled back)
        db_session.expire_all()
        final_count = db_session.query(JobPosting).count()
        assert final_count == initial_count, "No job should be created on validation error"
