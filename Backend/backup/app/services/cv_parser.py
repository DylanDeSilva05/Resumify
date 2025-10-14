"""
CV Parsing service for extracting structured information from CV files
"""
import os
import re
import json
import logging
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path
import PyPDF2
from docx import Document
import spacy
from sklearn.feature_extraction.text import TfidfVectorizer
import pandas as pd
from datetime import datetime
import email_validator

from app.core.config import settings

logger = logging.getLogger(__name__)


class CVParser:
    """Service class for parsing CV files and extracting structured information"""

    def __init__(self):
        """Initialize CV parser with NLP model"""
        try:
            self.nlp = spacy.load(settings.SPACY_MODEL)
        except OSError:
            logger.warning(f"SpaCy model '{settings.SPACY_MODEL}' not found. Using basic parsing.")
            self.nlp = None

        # Import the comprehensive skills database from NLP service
        from app.services.nlp_service import NLPService
        nlp_service = NLPService()

        # Use the same comprehensive skill databases as NLP service
        self.technical_skills = nlp_service.technical_skills_db
        self.soft_skills = nlp_service.soft_skills_db

        # Flatten technical skills for easier searching
        self.all_technical_skills = nlp_service.all_technical_skills

        # Education keywords
        self.education_keywords = [
            'bachelor', 'master', 'phd', 'doctorate', 'degree', 'university', 'college',
            'institute', 'school', 'education', 'graduated', 'gpa'
        ]

        # Experience keywords
        self.experience_keywords = [
            'work', 'experience', 'employment', 'position', 'job', 'role', 'company',
            'organization', 'years', 'months', 'present', 'current'
        ]

    def parse_cv_file(self, file_path: str) -> Dict[str, Any]:
        """
        Parse CV file and extract structured information

        Args:
            file_path: Path to the CV file

        Returns:
            Dict: Structured CV information
        """
        try:
            # Extract text from file
            raw_text = self._extract_text_from_file(file_path)
            if not raw_text:
                raise ValueError("Could not extract text from file")

            # Parse structured information
            parsed_data = self._parse_text_content(raw_text)
            parsed_data['raw_text'] = raw_text
            parsed_data['parsing_status'] = 'completed'

            logger.info(f"Successfully parsed CV: {file_path}")
            return parsed_data

        except Exception as e:
            logger.error(f"Failed to parse CV {file_path}: {str(e)}")
            return {
                'raw_text': '',
                'parsing_status': 'failed',
                'parsing_error': str(e),
                'personal_info': {},
                'education': [],
                'work_experience': [],
                'skills': {'technical': [], 'soft': []},
                'certifications': [],
                'languages': [],
                'total_experience_years': 0.0
            }

    def _extract_text_from_file(self, file_path: str) -> str:
        """Extract raw text from CV file"""
        file_extension = Path(file_path).suffix.lower()

        if file_extension == '.pdf':
            return self._extract_from_pdf(file_path)
        elif file_extension in ['.doc', '.docx']:
            return self._extract_from_docx(file_path)
        else:
            raise ValueError(f"Unsupported file format: {file_extension}")

    def _extract_from_pdf(self, file_path: str) -> str:
        """Extract text from PDF file"""
        text = ""
        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"
        except Exception as e:
            logger.error(f"Failed to extract text from PDF {file_path}: {str(e)}")
            raise
        return text.strip()

    def _extract_from_docx(self, file_path: str) -> str:
        """Extract text from DOCX file"""
        try:
            doc = Document(file_path)
            text = "\n".join([paragraph.text for paragraph in doc.paragraphs])
        except Exception as e:
            logger.error(f"Failed to extract text from DOCX {file_path}: {str(e)}")
            raise
        return text.strip()

    def _parse_text_content(self, text: str) -> Dict[str, Any]:
        """Parse raw text and extract structured information"""
        lines = [line.strip() for line in text.split('\n') if line.strip()]

        return {
            'personal_info': self._extract_personal_info(text),
            'education': self._extract_education(text),
            'work_experience': self._extract_work_experience(text, lines),
            'skills': self._extract_skills(text),
            'certifications': self._extract_certifications(text),
            'languages': self._extract_languages(text),
            'total_experience_years': self._calculate_experience_years(text)
        }

    def _extract_personal_info(self, text: str) -> Dict[str, Any]:
        """Extract personal information from CV text"""
        info = {}

        # Extract email
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        emails = re.findall(email_pattern, text)
        if emails:
            info['email'] = emails[0]

        # Extract phone number
        phone_patterns = [
            r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b',
            r'\(\d{3}\)\s*\d{3}[-.]?\d{4}',
            r'\+\d{1,3}[-.\s]?\d{1,14}',
        ]
        for pattern in phone_patterns:
            phones = re.findall(pattern, text)
            if phones:
                info['phone'] = phones[0]
                break

        # Extract location (basic implementation)
        location_keywords = ['city', 'state', 'country', 'address']
        for keyword in location_keywords:
            if keyword in text.lower():
                # This is a simplified implementation
                # In production, you'd use more sophisticated NLP
                info['location'] = "Location extracted"  # Placeholder
                break

        return info

    def _extract_education(self, text: str) -> List[Dict[str, Any]]:
        """Extract education information from CV text"""
        education = []
        text_lower = text.lower()

        # Look for degree keywords
        degree_patterns = [
            r'(bachelor|master|phd|doctorate|b\.s\.|m\.s\.|b\.a\.|m\.a\.|b\.tech|m\.tech)[\s\w]*',
            r'(university|college|institute)[\s\w]*',
        ]

        for pattern in degree_patterns:
            matches = re.findall(pattern, text_lower, re.IGNORECASE)
            for match in matches:
                education.append({
                    'degree': match.strip(),
                    'institution': 'Institution extracted',  # Placeholder
                    'year': self._extract_years_from_context(text, match)
                })

        return education

    def _extract_work_experience(self, text: str, lines: List[str]) -> List[Dict[str, Any]]:
        """Extract work experience from CV text"""
        experience = []

        # Look for job titles and companies
        job_indicators = ['experience', 'work', 'employment', 'position', 'job']
        company_indicators = ['company', 'corporation', 'inc', 'ltd', 'llc']

        # This is a simplified implementation
        # In production, you'd use more sophisticated parsing
        years = self._extract_all_years(text)
        if years:
            experience.append({
                'position': 'Position extracted',
                'company': 'Company extracted',
                'start_date': min(years) if years else None,
                'end_date': max(years) if years else None,
                'description': 'Description extracted',
                'duration_months': 12  # Placeholder
            })

        return experience

    def _extract_skills(self, text: str) -> Dict[str, List[str]]:
        """Extract technical and soft skills from CV text"""
        text_lower = text.lower()

        # Extract technical skills
        technical_skills = []
        for skill in self.all_technical_skills:
            # Use word boundaries to avoid partial matches
            pattern = rf'\b{re.escape(skill.lower())}\b'
            if re.search(pattern, text_lower):
                technical_skills.append(skill)

        # Extract soft skills
        soft_skills = []
        for skill in self.soft_skills:
            # Handle multi-word skills properly
            pattern = rf'\b{re.escape(skill.lower())}\b'
            if re.search(pattern, text_lower):
                soft_skills.append(skill)

        logger.info(f"Extracted {len(technical_skills)} technical skills: {technical_skills}")
        logger.info(f"Extracted {len(soft_skills)} soft skills: {soft_skills}")

        return {
            'technical': list(set(technical_skills)),
            'soft': list(set(soft_skills))
        }

    def _extract_certifications(self, text: str) -> List[Dict[str, Any]]:
        """Extract certifications from CV text"""
        certifications = []
        cert_keywords = ['certificate', 'certification', 'certified', 'license']

        for keyword in cert_keywords:
            if keyword.lower() in text.lower():
                certifications.append({
                    'name': 'Certification extracted',
                    'issuer': 'Issuer extracted',
                    'year': self._extract_years_from_context(text, keyword)
                })

        return certifications

    def _extract_languages(self, text: str) -> List[Dict[str, str]]:
        """Extract language skills from CV text"""
        languages = []
        common_languages = [
            'english', 'spanish', 'french', 'german', 'chinese', 'japanese',
            'portuguese', 'russian', 'arabic', 'hindi', 'italian'
        ]

        for language in common_languages:
            if language.lower() in text.lower():
                languages.append({
                    'language': language.title(),
                    'proficiency': 'Native/Fluent'  # Simplified
                })

        return languages

    def _calculate_experience_years(self, text: str) -> float:
        """Calculate total years of experience from CV text"""
        # Look for experience patterns
        experience_patterns = [
            r'(\d+)\s*years?\s*(of\s*)?experience',
            r'experience\s*:\s*(\d+)\s*years?',
            r'(\d+)\+?\s*years?\s*experience'
        ]

        years = []
        for pattern in experience_patterns:
            matches = re.findall(pattern, text.lower())
            for match in matches:
                try:
                    years.append(float(match[0] if isinstance(match, tuple) else match))
                except (ValueError, IndexError):
                    continue

        if years:
            return max(years)  # Return the highest experience mentioned

        # Fallback: calculate from work experience dates
        all_years = self._extract_all_years(text)
        if len(all_years) >= 2:
            return float(max(all_years) - min(all_years))

        return 0.0

    def _extract_years_from_context(self, text: str, context: str) -> Optional[int]:
        """Extract year from text context"""
        # Look for 4-digit years near the context
        context_index = text.lower().find(context.lower())
        if context_index != -1:
            context_area = text[max(0, context_index-50):context_index+50]
            years = re.findall(r'\b(19|20)\d{2}\b', context_area)
            if years:
                return int(years[0])
        return None

    def _extract_all_years(self, text: str) -> List[int]:
        """Extract all 4-digit years from text"""
        years = re.findall(r'\b(19|20)\d{2}\b', text)
        return [int(year) for year in years]

    def extract_candidate_name(self, text: str) -> str:
        """Extract candidate name from CV text (simplified)"""
        lines = [line.strip() for line in text.split('\n') if line.strip()]

        if not lines:
            return "Unknown"

        # First non-empty line is often the name
        first_line = lines[0]

        # Remove common headers
        headers_to_remove = ['curriculum vitae', 'resume', 'cv']
        first_line_lower = first_line.lower()

        if any(header in first_line_lower for header in headers_to_remove):
            # Try second line if first line is a header
            if len(lines) > 1:
                first_line = lines[1]

        # Basic name validation (contains only letters and spaces)
        if re.match(r'^[A-Za-z\s]+$', first_line) and len(first_line.split()) <= 5:
            return first_line.title()

        return "Unknown"