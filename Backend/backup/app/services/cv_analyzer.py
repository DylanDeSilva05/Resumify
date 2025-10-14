"""
CV Analysis service for matching candidates against job requirements
"""
import logging
from typing import Dict, List, Any, Tuple
from sqlalchemy.orm import Session
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import re
from datetime import datetime

from app.models import Candidate, JobPosting, CVAnalysis
from app.schemas.cv_analysis import CVAnalysisCreate
from app.services.nlp_service import NLPService

logger = logging.getLogger(__name__)


class CVAnalyzer:
    """Service class for analyzing and matching CVs against job requirements"""

    def __init__(self):
        """Initialize CV analyzer with NLP service"""
        self.nlp_service = NLPService()

        # Scoring weights for different criteria
        self.default_weights = {
            'skills': 0.35,
            'experience': 0.25,
            'education': 0.20,
            'soft_skills': 0.20
        }

    def analyze_candidates_for_job(
        self,
        db: Session,
        candidates: List[Candidate],
        job_posting: JobPosting,
        analyzed_by: int,
        custom_weights: Dict[str, float] = None
    ) -> List[CVAnalysisCreate]:
        """
        Analyze multiple candidates against a job posting

        Args:
            db: Database session
            candidates: List of candidates to analyze
            job_posting: Job posting with requirements
            analyzed_by: ID of user performing analysis
            custom_weights: Custom weights for scoring criteria

        Returns:
            List[CVAnalysisCreate]: Analysis results for all candidates
        """
        results = []
        weights = custom_weights or self.default_weights

        logger.info(f"Analyzing {len(candidates)} candidates for job: {job_posting.title}")

        for candidate in candidates:
            try:
                start_time = datetime.now()
                analysis = self._analyze_single_candidate(candidate, job_posting, weights)
                processing_time = int((datetime.now() - start_time).total_seconds() * 1000)

                # Create analysis result
                analysis_data = CVAnalysisCreate(
                    candidate_id=candidate.id,
                    job_posting_id=job_posting.id,
                    overall_score=analysis['overall_score'],
                    match_status=analysis['match_status'],
                    skill_match_score=analysis['skill_match_score'],
                    education_match_score=analysis['education_match_score'],
                    experience_match_score=analysis['experience_match_score'],
                    soft_skills_score=analysis['soft_skills_score'],
                    matched_skills=analysis['matched_skills'],
                    missing_skills=analysis['missing_skills'],
                    matched_education=analysis['matched_education'],
                    experience_analysis=analysis['experience_analysis'],
                    ai_summary=analysis['ai_summary'],
                    strengths=analysis['strengths'],
                    concerns=analysis['concerns'],
                    recommendations=analysis['recommendations'],
                    processing_time_ms=processing_time
                )

                results.append(analysis_data)

            except Exception as e:
                logger.error(f"Failed to analyze candidate {candidate.id}: {str(e)}")
                # Create failed analysis
                results.append(CVAnalysisCreate(
                    candidate_id=candidate.id,
                    job_posting_id=job_posting.id,
                    overall_score=0.0,
                    match_status='rejected',
                    ai_summary=f"Analysis failed: {str(e)}"
                ))

        return results

    def _analyze_single_candidate(
        self,
        candidate: Candidate,
        job_posting: JobPosting,
        weights: Dict[str, float]
    ) -> Dict[str, Any]:
        """Analyze a single candidate against job requirements"""

        # Extract job requirements
        job_requirements = self._extract_job_requirements(job_posting)

        # Extract candidate information
        candidate_info = self._extract_candidate_info(candidate)

        # Perform detailed matching
        skill_analysis = self._analyze_skills_match(candidate_info, job_requirements)
        education_analysis = self._analyze_education_match(candidate_info, job_requirements)
        experience_analysis = self._analyze_experience_match(candidate_info, job_requirements)
        soft_skills_analysis = self._analyze_soft_skills_match(candidate_info, job_requirements)

        # Calculate overall score
        overall_score = (
            skill_analysis['score'] * weights.get('skills', 0.35) +
            education_analysis['score'] * weights.get('education', 0.20) +
            experience_analysis['score'] * weights.get('experience', 0.25) +
            soft_skills_analysis['score'] * weights.get('soft_skills', 0.20)
        )

        logger.info(f"Component scores: Skills={skill_analysis['score']:.1f}, "
                   f"Education={education_analysis['score']:.1f}, "
                   f"Experience={experience_analysis['score']:.1f}, "
                   f"Soft Skills={soft_skills_analysis['score']:.1f}")
        logger.info(f"Overall score: {overall_score:.2f}")

        # Determine match status
        match_status = self._determine_match_status(overall_score)
        logger.info(f"Match status: {match_status}")

        # Generate AI summary and insights
        ai_insights = self._generate_ai_insights(
            candidate, job_posting, overall_score,
            skill_analysis, education_analysis, experience_analysis, soft_skills_analysis
        )

        return {
            'overall_score': round(overall_score, 2),
            'match_status': match_status,
            'skill_match_score': round(skill_analysis['score'], 2),
            'education_match_score': round(education_analysis['score'], 2),
            'experience_match_score': round(experience_analysis['score'], 2),
            'soft_skills_score': round(soft_skills_analysis['score'], 2),
            'matched_skills': skill_analysis['matched'],
            'missing_skills': skill_analysis['missing'],
            'matched_education': education_analysis['matched'],
            'experience_analysis': experience_analysis['details'],
            'ai_summary': ai_insights['summary'],
            'strengths': ai_insights['strengths'],
            'concerns': ai_insights['concerns'],
            'recommendations': ai_insights['recommendations']
        }

    def _extract_job_requirements(self, job_posting: JobPosting) -> Dict[str, Any]:
        """Extract and structure job requirements"""
        return {
            'required_skills': job_posting.required_skills or [],
            'preferred_skills': job_posting.preferred_skills or [],
            'education_requirements': job_posting.education_requirements or [],
            'experience_requirements': job_posting.experience_requirements or [],
            'soft_skills': job_posting.soft_skills or [],
            'min_experience_years': job_posting.min_experience_years or 0,
            'max_experience_years': job_posting.max_experience_years,
            'title': job_posting.title,
            'description': job_posting.description
        }

    def _extract_candidate_info(self, candidate: Candidate) -> Dict[str, Any]:
        """Extract and structure candidate information"""
        skills = candidate.skills or {'technical': [], 'soft': []}
        return {
            'technical_skills': skills.get('technical', []),
            'soft_skills': skills.get('soft', []),
            'education': candidate.education or [],
            'work_experience': candidate.work_experience or [],
            'total_experience_years': candidate.total_experience_years or 0.0,
            'certifications': candidate.certifications or [],
            'languages': candidate.languages or [],
            'raw_text': candidate.raw_text or ''
        }

    def _analyze_skills_match(
        self,
        candidate_info: Dict[str, Any],
        job_requirements: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Dynamic skills analysis using direct keyword matching from job description"""

        # Get the full CV text for direct keyword searching
        cv_text = candidate_info.get('raw_text', '').lower()

        # Get job description for keyword extraction
        job_description = job_requirements.get('description', '').lower()

        logger.info(f"Analyzing CV text length: {len(cv_text)} characters")
        logger.info(f"Job description length: {len(job_description)} characters")

        # Extract keywords dynamically from job description
        job_keywords = self._extract_job_keywords(job_description)
        logger.info(f"Extracted job keywords: {job_keywords[:10]}...")  # Show first 10

        # Search for keywords directly in CV text
        matched_keywords = []
        for keyword in job_keywords:
            if keyword in cv_text:
                matched_keywords.append(keyword)

        logger.info(f"Matched keywords in CV: {matched_keywords}")

        # Also check predefined skills as supplementary
        candidate_skills = [skill.lower() for skill in candidate_info['technical_skills']]
        required_skills = [skill.lower() for skill in job_requirements['required_skills']]
        preferred_skills = [skill.lower() for skill in job_requirements['preferred_skills']]

        matched_predefined = []
        for skill in required_skills + preferred_skills:
            if skill in candidate_skills or skill in cv_text:
                matched_predefined.append(skill)

        # Combine both approaches
        all_matches = list(set(matched_keywords + matched_predefined))
        total_job_terms = len(job_keywords) + len(required_skills) + len(preferred_skills)

        logger.info(f"Total matches found: {len(all_matches)}")
        logger.info(f"Match count: {len(all_matches)} out of {total_job_terms} terms")

        # Calculate score based on keyword density and matches
        if total_job_terms == 0:
            score = 30.0  # Default score when no specific requirements
        else:
            # Calculate match percentage
            match_rate = len(all_matches) / max(total_job_terms, 1)

            # Boost score for relevant keyword matches
            keyword_boost = min(30.0, len(matched_keywords) * 2)

            score = (match_rate * 60) + keyword_boost + 15  # Base 15 points
            score = min(100.0, score)  # Cap at 100

        logger.info(f"Dynamic skills match score: {score}")

        return {
            'score': score,
            'matched': all_matches,
            'missing': [skill for skill in required_skills if skill not in all_matches],
            'details': {
                'keyword_matches': len(matched_keywords),
                'predefined_matches': len(matched_predefined),
                'total_job_terms': total_job_terms,
                'match_rate': len(all_matches) / max(total_job_terms, 1) if total_job_terms > 0 else 0
            }
        }

    def _extract_job_keywords(self, job_description: str) -> List[str]:
        """Extract relevant keywords from job description"""
        import re
        from collections import Counter

        # Remove common stop words
        stop_words = {
            'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'are', 'was', 'were',
            'be', 'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should',
            'may', 'might', 'must', 'can', 'shall', 'a', 'an', 'this', 'that', 'these', 'those', 'we', 'you', 'they',
            'he', 'she', 'it', 'i', 'me', 'my', 'your', 'our', 'their', 'him', 'her', 'us', 'them', 'looking', 'seeking',
            'required', 'preferred', 'experience', 'years', 'work', 'working', 'position', 'role', 'job', 'candidate',
            'responsibilities', 'duties', 'requirements', 'qualifications', 'skills', 'ability', 'knowledge', 'must',
            'should', 'include', 'including', 'such', 'well', 'good', 'strong', 'excellent'
        }

        # Extract words (2+ characters, alphanumeric plus some special chars)
        words = re.findall(r'\b[a-zA-Z][a-zA-Z0-9+#.-]*\b', job_description.lower())

        # Remove stop words and get meaningful terms
        meaningful_words = [word for word in words if word not in stop_words and len(word) >= 2]

        # Count frequency and take top terms
        word_counts = Counter(meaningful_words)

        # Get top 25 most frequent meaningful words
        top_keywords = [word for word, count in word_counts.most_common(25) if count >= 1]

        # Add some pattern-based extraction for technical terms
        # Look for terms that might be technologies, tools, certifications, etc.
        tech_patterns = [
            r'\b[A-Z]{2,10}\b',  # Acronyms like API, SQL, AWS, etc.
            r'\b\w+[.]js\b',     # JavaScript frameworks
            r'\b\w+[-]\w+\b',    # Hyphenated terms
            r'\b\w+[+][+]?\b',   # Programming languages like C++
        ]

        for pattern in tech_patterns:
            matches = re.findall(pattern, job_description)
            top_keywords.extend([match.lower() for match in matches])

        return list(set(top_keywords))  # Remove duplicates

    def _analyze_education_match(
        self,
        candidate_info: Dict[str, Any],
        job_requirements: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Analyze education requirements match"""
        candidate_education = candidate_info['education']
        required_education = job_requirements['education_requirements']

        if not required_education:
            return {'score': 25.0, 'matched': [], 'details': {}}

        # Simplified education matching
        # In production, this would be more sophisticated
        education_keywords = []
        for edu in candidate_education:
            if isinstance(edu, dict):
                education_keywords.extend([
                    edu.get('degree', '').lower(),
                    edu.get('institution', '').lower()
                ])
            else:
                education_keywords.append(str(edu).lower())

        matched = []
        for req in required_education:
            req_lower = req.lower()
            if any(keyword in req_lower or req_lower in keyword
                   for keyword in education_keywords):
                matched.append(req)

        score = (len(matched) / len(required_education)) * 100 if required_education else 50.0

        return {
            'score': score,
            'matched': matched,
            'details': {
                'requirements_met': len(matched),
                'total_requirements': len(required_education)
            }
        }

    def _analyze_experience_match(
        self,
        candidate_info: Dict[str, Any],
        job_requirements: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Analyze experience requirements match"""
        candidate_years = candidate_info['total_experience_years']
        min_required = job_requirements['min_experience_years']
        max_required = job_requirements.get('max_experience_years')

        logger.info(f"Candidate experience: {candidate_years} years")
        logger.info(f"Required experience: {min_required}-{max_required} years")

        # Calculate experience score
        if min_required == 0:
            # No experience requirement specified, neutral score
            score = 40.0
        elif candidate_years >= min_required:
            if max_required and candidate_years > max_required:
                # Overqualified - slightly lower score
                score = 85.0
            else:
                # Good fit
                score = 100.0
        else:
            # Under qualified but give partial credit
            if min_required > 0:
                score = max(40.0, (candidate_years / min_required) * 80)
            else:
                score = 60.0

        logger.info(f"Experience match score: {score}")

        return {
            'score': score,
            'details': {
                'candidate_years': candidate_years,
                'min_required': min_required,
                'max_required': max_required,
                'meets_minimum': candidate_years >= min_required
            }
        }

    def _analyze_soft_skills_match(
        self,
        candidate_info: Dict[str, Any],
        job_requirements: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Analyze soft skills match"""
        candidate_soft_skills = [skill.lower() for skill in candidate_info['soft_skills']]
        required_soft_skills = [skill.lower() for skill in job_requirements['soft_skills']]

        if not required_soft_skills:
            return {'score': 50.0, 'matched': [], 'details': {}}

        matched = [skill for skill in required_soft_skills if skill in candidate_soft_skills]
        score = (len(matched) / len(required_soft_skills)) * 100

        return {
            'score': score,
            'matched': matched,
            'details': {
                'matched_count': len(matched),
                'required_count': len(required_soft_skills)
            }
        }

    def _determine_match_status(self, overall_score: float) -> str:
        """Determine match status based on overall score"""
        if overall_score >= 50:
            return 'shortlisted'
        else:
            return 'rejected'

    def _generate_ai_insights(
        self,
        candidate: Candidate,
        job_posting: JobPosting,
        overall_score: float,
        skill_analysis: Dict[str, Any],
        education_analysis: Dict[str, Any],
        experience_analysis: Dict[str, Any],
        soft_skills_analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate AI-powered insights and recommendations"""

        # Generate summary
        summary = f"Candidate shows {overall_score:.0f}% match for {job_posting.title} position. "

        # Identify strengths
        strengths = []
        if skill_analysis['score'] >= 80:
            strengths.append("Strong technical skill alignment")
        if experience_analysis['score'] >= 80:
            strengths.append("Meets experience requirements")
        if education_analysis['score'] >= 80:
            strengths.append("Educational background aligns well")
        if soft_skills_analysis['score'] >= 80:
            strengths.append("Good soft skills match")

        # Identify concerns
        concerns = []
        if skill_analysis['score'] < 50:
            concerns.append("Missing key technical skills")
        if experience_analysis['score'] < 50:
            concerns.append("Insufficient relevant experience")
        if education_analysis['score'] < 50:
            concerns.append("Education requirements not fully met")

        # Generate recommendations
        recommendations = []
        if overall_score >= 70:
            recommendations.append("Proceed with interview scheduling")
        elif overall_score >= 50:
            recommendations.append("Consider for phone screening")
            if skill_analysis['missing']:
                recommendations.append("Assess missing technical skills during interview")
        else:
            recommendations.append("Not recommended for this position")

        return {
            'summary': summary,
            'strengths': strengths,
            'concerns': concerns,
            'recommendations': recommendations
        }

    def get_analysis_statistics(self, analyses: List[CVAnalysis]) -> Dict[str, Any]:
        """Get statistics from analysis results"""
        if not analyses:
            return {'total': 0, 'shortlisted': 0, 'rejected': 0}

        total = len(analyses)
        shortlisted = sum(1 for a in analyses if a.match_status == 'shortlisted')
        rejected = sum(1 for a in analyses if a.match_status == 'rejected')

        avg_score = sum(a.overall_score for a in analyses) / total if total > 0 else 0

        return {
            'total': total,
            'shortlisted': shortlisted,
            'rejected': rejected,
            'average_score': round(avg_score, 2)
        }