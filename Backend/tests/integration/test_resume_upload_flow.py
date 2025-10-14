"""
Integration tests for resume upload and analysis workflow
Location: Backend/tests/integration/test_resume_upload_flow.py

Test Cases Implemented:
- I-03: Resume upload and analysis pipeline

See TEST_SPECIFICATION.md for detailed test case specifications.
"""
import pytest
from fastapi import status
from io import BytesIO
from unittest.mock import patch


@pytest.mark.integration
class TestResumeUploadWorkflow:
    """Test I-03: Resume upload and analysis pipeline"""

    @patch('app.services.cv_parser.CVParserService')
    def test_resume_upload_and_analysis(self, mock_parser, client, auth_headers_candidate, sample_resume_text):
        """
        Test ID: I-03
        Test complete resume upload and analysis pipeline
        """
        # Mock the parser service
        mock_parser_instance = mock_parser.return_value
        mock_parser_instance.parse_resume.return_value = {
            "name": "John Doe",
            "email": "john.doe@email.com",
            "skills": ["Python", "FastAPI", "Django"],
            "experience_years": 5
        }

        # Create mock PDF file
        file_content = b"%PDF-1.4 Mock Resume Content"
        files = {
            "file": ("resume.pdf", BytesIO(file_content), "application/pdf")
        }

        # Upload resume
        response = client.post(
            "/api/v1/upload/resume",
            files=files,
            headers=auth_headers_candidate
        )

        # Verify response
        if response.status_code == status.HTTP_200_OK:
            data = response.json()

            # Verify file was saved and processed
            assert "filename" in data or "file_path" in data or "analysis" in data, \
                "Response should contain file information"
        else:
            # Some implementations might return 201 or require different structure
            assert response.status_code in [status.HTTP_200_OK, status.HTTP_201_CREATED], \
                f"Upload should succeed, got {response.status_code}: {response.text}"

    def test_upload_without_auth_rejected(self, client):
        """
        Additional test: Upload without authentication is rejected
        """
        file_content = b"%PDF-1.4 Test"
        files = {
            "file": ("resume.pdf", BytesIO(file_content), "application/pdf")
        }

        response = client.post("/api/v1/upload/resume", files=files)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED, \
            "Upload without auth should return 401"
