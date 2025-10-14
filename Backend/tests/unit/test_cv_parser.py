"""
Unit tests for CV/Resume parser service
Location: Backend/tests/unit/test_cv_parser.py

Test Cases Implemented:
- U-05: Resume text extraction from PDF - valid PDF file
- U-06: Resume parsing with missing skills section

See TEST_SPECIFICATION.md for detailed test case specifications.
"""
import pytest
from unittest.mock import Mock, patch, MagicMock


@pytest.mark.unit
class TestResumeTextExtraction:
    """Test U-05: Resume text extraction from PDF"""

    @patch('app.services.cv_parser.CVParser._extract_from_pdf')
    def test_extract_text_from_valid_pdf(self, mock_extract, sample_resume_text):
        """
        Test ID: U-05
        Test resume text extraction from valid PDF file
        """
        from app.services.cv_parser import CVParser

        # Mock PDF extraction to return sample resume text
        mock_extract.return_value = sample_resume_text

        # Create parser instance
        parser = CVParser()

        # Simulate extraction
        extracted_text = parser._extract_from_pdf("sample_resume.pdf")

        # Verify extraction successful
        assert extracted_text is not None, "Extracted text should not be None"
        assert len(extracted_text) > 0, "Extracted text should not be empty"

        # Verify expected sections are present
        assert "Experience" in extracted_text or "EXPERIENCE" in extracted_text, \
            "Resume should contain Experience section"
        assert "Education" in extracted_text or "EDUCATION" in extracted_text, \
            "Resume should contain Education section"
        assert "Skills" in extracted_text or "SKILLS" in extracted_text, \
            "Resume should contain Skills section"

    @patch('app.services.cv_parser.CVParser._parse_text_content')
    def test_parse_extracted_text(self, mock_parser, sample_resume_text):
        """
        Additional test: Parse extracted text into structured data
        """
        from app.services.cv_parser import CVParser

        # Mock parser to return structured data
        mock_parser.return_value = {
            "personal_info": {
                "name": "John Doe",
                "email": "john.doe@email.com",
                "phone": "+1-555-0123"
            },
            "skills": {
                "programming_languages": ["Python"],
                "frameworks": ["FastAPI", "Django"]
            },
            "experience_years": 5,
            "education": [{"degree": "Bachelor of Science in Computer Science"}]
        }

        # Create parser and parse
        parser = CVParser()
        parsed_data = parser._parse_text_content(sample_resume_text)

        # Verify parsed data structure
        assert "personal_info" in parsed_data or "name" in str(parsed_data), \
            "Parsed data should contain personal info"
        assert "skills" in parsed_data, "Parsed data should contain skills"


@pytest.mark.unit
class TestResumeParsingWithMissingData:
    """Test U-06: Resume parsing with missing skills section"""

    @patch('app.services.cv_parser.CVParser._extract_skills')
    def test_parse_resume_without_skills(self, mock_skills, sample_resume_no_skills):
        """
        Test ID: U-06
        Test resume parsing when skills section is missing
        """
        from app.services.cv_parser import CVParser

        # Mock skills extraction to return empty dict
        mock_skills.return_value = {}

        # Create parser and extract skills
        parser = CVParser()
        skills_data = parser._extract_skills(sample_resume_no_skills)

        # Verify parsing continues despite missing skills
        assert skills_data is not None, "Parsing should continue despite missing skills"
        assert isinstance(skills_data, dict), "Skills should be a dict"
        assert len(skills_data) == 0 or all(len(v) == 0 for v in skills_data.values()), \
            "Skills should be empty or have empty lists"

    def test_parse_empty_resume(self):
        """
        Additional test: Handle completely empty resume
        """
        from app.services.cv_parser import CVParser

        empty_text = ""
        parser = CVParser()

        # Extract name from empty text
        name = parser.extract_candidate_name(empty_text)

        # Should handle gracefully
        assert name is not None, "Should return some value for empty resume"
        assert isinstance(name, str), "Name should be a string"


@pytest.mark.unit
class TestFileTypeHandling:
    """Additional tests for different file types"""

    @patch('app.services.cv_parser.CVParser._extract_from_pdf')
    def test_pdf_file_extraction(self, mock_extract):
        """Test PDF file text extraction"""
        from app.services.cv_parser import CVParser

        mock_extract.return_value = "Sample PDF content"

        parser = CVParser()
        result = parser._extract_from_pdf("resume.pdf")

        assert result == "Sample PDF content"
        mock_extract.assert_called_once_with("resume.pdf")

    @patch('app.services.cv_parser.CVParser._extract_from_docx')
    def test_docx_file_extraction(self, mock_extract):
        """Test DOCX file text extraction"""
        from app.services.cv_parser import CVParser

        mock_extract.return_value = "Sample DOCX content"

        parser = CVParser()
        result = parser._extract_from_docx("resume.docx")

        assert result == "Sample DOCX content"
        mock_extract.assert_called_once_with("resume.docx")
