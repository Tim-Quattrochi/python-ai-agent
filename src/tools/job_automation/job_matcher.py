"""Job matching algorithm for scoring resume-job compatibility."""

import re
import logging
from typing import Dict, Any, List, Tuple, Optional
from dataclasses import dataclass, asdict
from datetime import datetime

from .resume_parser import ResumeData, Experience
from .job_scraper import JobPosting
from ..base import Tool

logger = logging.getLogger(__name__)


@dataclass
class MatchScore:
    """Job match scoring results."""
    total_score: float = 0.0
    skills_score: float = 0.0
    experience_score: float = 0.0
    keyword_score: float = 0.0
    location_score: float = 0.0

    skills_matched: List[str] = None
    skills_missing: List[str] = None
    experience_years: float = 0.0
    experience_level_match: bool = False
    keywords_found: List[str] = None

    explanation: str = ""
    recommendation: str = ""

    def __post_init__(self):
        if self.skills_matched is None:
            self.skills_matched = []
        if self.skills_missing is None:
            self.skills_missing = []
        if self.keywords_found is None:
            self.keywords_found = []


@dataclass
class JobMatchResult:
    """Complete job matching result."""
    job: JobPosting
    resume: ResumeData
    match_score: MatchScore
    timestamp: str = ""

    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now().isoformat()


class JobMatcherTool(Tool):
    """A tool for matching resumes to job requirements and calculating compatibility scores."""

    def __init__(self):
        super().__init__(
            name="job_matcher",
            description="Match resumes to job postings and calculate compatibility scores based on skills, experience, and requirements."
        )

        # Scoring weights (should total 1.0)
        self.weights = {
            'skills': 0.4,        # 40% - Most important
            'experience': 0.3,    # 30% - Very important
            'keywords': 0.2,      # 20% - Important for ATS
            'location': 0.1       # 10% - Less important (remote work)
        }

    def get_schema(self) -> Dict[str, Any]:
        """Get the JSON schema for job matcher parameters."""
        return {
            "type": "object",
            "properties": {
                "operation": {
                    "type": "string",
                    "enum": ["match_job", "batch_match", "analyze_fit"],
                    "description": "The matching operation to perform"
                },
                "resume_data": {
                    "type": "object",
                    "description": "Parsed resume data (from resume parser tool)"
                },
                "job_data": {
                    "type": "object",
                    "description": "Job posting data (from job scraper tool)"
                },
                "jobs_list": {
                    "type": "array",
                    "description": "List of job postings for batch matching",
                    "items": {"type": "object"}
                },
                "threshold": {
                    "type": "number",
                    "description": "Minimum match score threshold (0-100)",
                    "minimum": 0,
                    "maximum": 100,
                    "default": 60
                },
                "custom_weights": {
                    "type": "object",
                    "description": "Custom scoring weights",
                    "properties": {
                        "skills": {"type": "number", "minimum": 0, "maximum": 1},
                        "experience": {"type": "number", "minimum": 0, "maximum": 1},
                        "keywords": {"type": "number", "minimum": 0, "maximum": 1},
                        "location": {"type": "number", "minimum": 0, "maximum": 1}
                    }
                }
            },
            "required": ["operation"],
            "additionalProperties": False
        }

    def execute(self, operation: str, **kwargs) -> str:
        """Execute a job matching operation."""
        try:
            if operation == "match_job":
                return self._match_single_job(
                    kwargs.get('resume_data'),
                    kwargs.get('job_data'),
                    kwargs.get('custom_weights')
                )
            elif operation == "batch_match":
                return self._batch_match_jobs(
                    kwargs.get('resume_data'),
                    kwargs.get('jobs_list', []),
                    kwargs.get('threshold', 60),
                    kwargs.get('custom_weights')
                )
            elif operation == "analyze_fit":
                return self._analyze_job_fit(
                    kwargs.get('resume_data'),
                    kwargs.get('job_data')
                )
            else:
                return f"Error: Unknown operation '{operation}'. Available: match_job, batch_match, analyze_fit"
        except Exception as e:
            logger.error(f"Job matcher error: {e}")
            return f"Error executing {operation}: {str(e)}"

    def _match_single_job(self, resume_data: Dict, job_data: Dict, custom_weights: Dict = None) -> str:
        """Match a single resume to a job posting."""
        if not resume_data or not job_data:
            return "❌ Error: Both resume_data and job_data are required"

        try:
            # Convert dict data to dataclass objects
            resume = self._dict_to_resume_data(resume_data)
            job = self._dict_to_job_posting(job_data)

            # Apply custom weights if provided
            if custom_weights:
                self._update_weights(custom_weights)

            # Calculate match score
            match_score = self._calculate_match_score(resume, job)

            # Create result
            result = JobMatchResult(
                job=job, resume=resume, match_score=match_score)

            return self._format_match_result(result)

        except Exception as e:
            logger.error(f"Error in single job matching: {e}")
            return f"❌ Error matching job: {str(e)}"

    def _batch_match_jobs(self, resume_data: Dict, jobs_list: List[Dict], threshold: float = 60, custom_weights: Dict = None) -> str:
        """Match a resume to multiple job postings and rank them."""
        if not resume_data or not jobs_list:
            return "❌ Error: Both resume_data and jobs_list are required"

        try:
            resume = self._dict_to_resume_data(resume_data)

            if custom_weights:
                self._update_weights(custom_weights)

            matches = []
            for job_dict in jobs_list:
                try:
                    job = self._dict_to_job_posting(job_dict)
                    match_score = self._calculate_match_score(resume, job)

                    if match_score.total_score >= threshold:
                        result = JobMatchResult(
                            job=job, resume=resume, match_score=match_score)
                        matches.append(result)
                except Exception as e:
                    logger.warning(f"Error processing job: {e}")
                    continue

            # Sort by match score (highest first)
            matches.sort(key=lambda x: x.match_score.total_score, reverse=True)

            return self._format_batch_results(matches, threshold)

        except Exception as e:
            logger.error(f"Error in batch job matching: {e}")
            return f"❌ Error in batch matching: {str(e)}"

    def _analyze_job_fit(self, resume_data: Dict, job_data: Dict) -> str:
        """Provide detailed analysis of job fit with improvement recommendations."""
        if not resume_data or not job_data:
            return "❌ Error: Both resume_data and job_data are required"

        try:
            resume = self._dict_to_resume_data(resume_data)
            job = self._dict_to_job_posting(job_data)

            match_score = self._calculate_match_score(resume, job)

            # Generate detailed analysis
            analysis = self._generate_detailed_analysis(
                resume, job, match_score)

            return analysis

        except Exception as e:
            logger.error(f"Error in job fit analysis: {e}")
            return f"❌ Error analyzing job fit: {str(e)}"

    def _calculate_match_score(self, resume: ResumeData, job: JobPosting) -> MatchScore:
        """Calculate comprehensive match score between resume and job."""
        match_score = MatchScore()

        # 1. Skills matching (40% weight)
        match_score.skills_score, match_score.skills_matched, match_score.skills_missing = self._calculate_skills_score(
            resume, job)

        # 2. Experience matching (30% weight)
        match_score.experience_score, match_score.experience_years, match_score.experience_level_match = self._calculate_experience_score(
            resume, job)

        # 3. Keyword matching (20% weight)
        match_score.keyword_score, match_score.keywords_found = self._calculate_keyword_score(
            resume, job)

        # 4. Location matching (10% weight)
        match_score.location_score = self._calculate_location_score(
            resume, job)

        # Calculate weighted total score
        match_score.total_score = (
            match_score.skills_score * self.weights['skills'] +
            match_score.experience_score * self.weights['experience'] +
            match_score.keyword_score * self.weights['keywords'] +
            match_score.location_score * self.weights['location']
        )

        # Generate explanation and recommendation
        match_score.explanation = self._generate_score_explanation(match_score)
        match_score.recommendation = self._generate_recommendation(match_score)

        return match_score

    def _calculate_skills_score(self, resume: ResumeData, job: JobPosting) -> Tuple[float, List[str], List[str]]:
        """Calculate skills matching score."""
        if not job.skills_required:
            return 100.0, [], []  # No specific skills required

        resume_skills = [skill.lower() for skill in resume.skills]
        job_skills = [skill.lower() for skill in job.skills_required]

        matched_skills = []
        missing_skills = []

        for job_skill in job_skills:
            # Check for exact match or partial match
            skill_found = False
            for resume_skill in resume_skills:
                if job_skill in resume_skill or resume_skill in job_skill:
                    matched_skills.append(job_skill.title())
                    skill_found = True
                    break

            if not skill_found:
                missing_skills.append(job_skill.title())

        # Calculate score: (matched skills / total required skills) * 100
        if job_skills:
            score = (len(matched_skills) / len(job_skills)) * 100
        else:
            score = 100.0

        return score, matched_skills, missing_skills

    def _calculate_experience_score(self, resume: ResumeData, job: JobPosting) -> Tuple[float, float, bool]:
        """Calculate experience matching score."""
        # Extract years of experience from resume
        total_years = self._calculate_total_experience_years(resume.experience)

        # Extract required experience from job description
        required_years = self._extract_required_experience(job.description)

        # Calculate score based on experience adequacy
        if required_years == 0:
            score = 100.0  # No specific experience requirement
        elif total_years >= required_years:
            # Give bonus for exceeding requirements (up to 100%)
            score = min(100.0, 80.0 + (total_years - required_years) * 5)
        else:
            # Penalty for insufficient experience
            score = max(0.0, (total_years / required_years) * 80.0)

        # Check experience level match
        level_match = self._check_experience_level_match(
            total_years, job.experience_level)

        return score, total_years, level_match

    def _calculate_keyword_score(self, resume: ResumeData, job: JobPosting) -> Tuple[float, List[str]]:
        """Calculate keyword matching score (important for ATS systems)."""
        if not job.description:
            return 100.0, []

        # Extract important keywords from job description
        job_keywords = self._extract_job_keywords(job.description)

        if not job_keywords:
            return 100.0, []

        # Check which keywords appear in resume
        resume_text = self._get_resume_text(resume).lower()
        found_keywords = []

        for keyword in job_keywords:
            if keyword.lower() in resume_text:
                found_keywords.append(keyword)

        # Calculate score
        score = (len(found_keywords) / len(job_keywords)) * \
            100 if job_keywords else 100.0

        return score, found_keywords

    def _calculate_location_score(self, resume: ResumeData, job: JobPosting) -> float:
        """Calculate location matching score."""
        if not job.location:
            return 100.0  # No location specified

        job_location = job.location.lower()

        # Check for remote work
        if 'remote' in job_location:
            return 100.0

        # Check if resume location matches job location
        if resume.contact_info and resume.contact_info.location:
            resume_location = resume.contact_info.location.lower()

            # Exact match
            if resume_location in job_location or job_location in resume_location:
                return 100.0

            # Same state/region (simplified check)
            if self._same_region(resume_location, job_location):
                return 80.0

        # Default score for location mismatch
        return 60.0

    def _calculate_total_experience_years(self, experiences: List[Experience]) -> float:
        """Calculate total years of professional experience."""
        total_years = 0.0

        for exp in experiences:
            years = self._parse_experience_duration(exp.duration)
            total_years += years

        return total_years

    def _parse_experience_duration(self, duration: str) -> float:
        """Parse experience duration string to years."""
        if not duration:
            return 0.0

        duration = duration.lower()
        years = 0.0

        # Handle date ranges first (e.g., "2020-2023" or "2020-present")
        year_range_patterns = [
            r'(\d{4})\s*-\s*(\d{4})',      # 2020-2023
            r'(\d{4})\s*-\s*present'        # 2020-present
        ]

        for pattern in year_range_patterns:
            matches = re.findall(pattern, duration)
            for match in matches:
                if isinstance(match, tuple) and len(match) == 2:
                    start_year = int(match[0])
                    end_year = int(
                        match[1]) if match[1] != 'present' else datetime.now().year
                    years += end_year - start_year
                    return years  # Return immediately for date ranges
                elif isinstance(match, str) and match != 'present':
                    # Handle single match like "2020-present"
                    start_year = int(match)
                    end_year = datetime.now().year
                    years += end_year - start_year
                    return years

        # Handle compound durations like "2 years 6 months"
        # Extract years
        year_matches = re.findall(r'(\d+)\s*(?:years?|yrs?)', duration)
        for match in year_matches:
            years += float(match)

        # Extract months and convert to years
        month_matches = re.findall(r'(\d+)\s*(?:months?|mos?)', duration)
        for match in month_matches:
            years += float(match) / 12.0

        return years

    def _extract_required_experience(self, job_description: str) -> float:
        """Extract required years of experience from job description."""
        if not job_description:
            return 0.0

        desc = job_description.lower()

        # Common experience requirement patterns
        patterns = [
            r'(\d+)\+?\s*(?:years?|yrs?)\s*(?:of\s*)?(?:experience|exp)',
            r'minimum\s*(?:of\s*)?(\d+)\s*(?:years?|yrs?)',
            r'(\d+)\s*(?:years?|yrs?)\s*(?:minimum|min)',
            r'(\d+)\s*to\s*(\d+)\s*(?:years?|yrs?)'
        ]

        for pattern in patterns:
            matches = re.findall(pattern, desc)
            if matches:
                if isinstance(matches[0], tuple):
                    # Range pattern
                    return float(matches[0][0])
                else:
                    # Single number
                    return float(matches[0])

        return 0.0

    def _check_experience_level_match(self, years: float, job_level: str) -> bool:
        """Check if experience years match job level requirements."""
        if not job_level:
            return True

        level = job_level.lower()

        if 'entry' in level or 'junior' in level:
            return years <= 3
        elif 'mid' in level or 'intermediate' in level:
            return 2 <= years <= 7
        elif 'senior' in level:
            return years >= 5
        elif 'lead' in level or 'principal' in level:
            return years >= 7
        elif 'director' in level or 'manager' in level:
            return years >= 10

        return True

    def _extract_job_keywords(self, job_description: str) -> List[str]:
        """Extract important keywords from job description."""
        keywords = []

        # Common important keywords to look for
        keyword_categories = {
            'methodologies': ['agile', 'scrum', 'kanban', 'waterfall', 'devops', 'ci/cd'],
            'practices': ['tdd', 'bdd', 'pair programming', 'code review', 'unit testing'],
            'concepts': ['microservices', 'api', 'rest', 'graphql', 'mvc', 'orm'],
            'domains': ['machine learning', 'data science', 'web development', 'mobile', 'blockchain']
        }

        desc_lower = job_description.lower()

        for category, terms in keyword_categories.items():
            for term in terms:
                if term in desc_lower:
                    keywords.append(term.title())

        return keywords

    def _get_resume_text(self, resume: ResumeData) -> str:
        """Get all text content from resume for keyword matching."""
        text_parts = [
            resume.summary,
            ' '.join(resume.skills),
            ' '.join([exp.description for exp in resume.experience]),
            ' '.join([proj.description for proj in resume.projects]),
            ' '.join(resume.certifications)
        ]

        return ' '.join(filter(None, text_parts))

    def _same_region(self, location1: str, location2: str) -> bool:
        """Check if two locations are in the same region (simplified)."""
        # Simplified region checking - could be enhanced with real geo data
        common_regions = [
            ['california', 'ca', 'san francisco', 'los angeles', 'san diego'],
            ['new york', 'ny', 'nyc', 'new york city'],
            ['texas', 'tx', 'austin', 'dallas', 'houston'],
            ['washington', 'wa', 'seattle'],
            ['massachusetts', 'ma', 'boston']
        ]

        for region in common_regions:
            if any(term in location1 for term in region) and any(term in location2 for term in region):
                return True

        return False

    def _generate_score_explanation(self, match_score: MatchScore) -> str:
        """Generate explanation for the match score."""
        explanations = []

        explanations.append(
            f"Skills Match: {match_score.skills_score:.1f}% ({len(match_score.skills_matched)}/{len(match_score.skills_matched) + len(match_score.skills_missing)} required skills)")
        explanations.append(
            f"Experience: {match_score.experience_score:.1f}% ({match_score.experience_years:.1f} years)")
        explanations.append(
            f"Keywords: {match_score.keyword_score:.1f}% ({len(match_score.keywords_found)} key terms found)")
        explanations.append(f"Location: {match_score.location_score:.1f}%")

        return " | ".join(explanations)

    def _generate_recommendation(self, match_score: MatchScore) -> str:
        """Generate recommendation based on match score."""
        score = match_score.total_score

        if score >= 90:
            return "🎯 Excellent match! Strong candidate - highly recommended to apply."
        elif score >= 80:
            return "✅ Very good match! Good candidate - recommended to apply."
        elif score >= 70:
            return "👍 Good match! Decent candidate - consider applying."
        elif score >= 60:
            return "⚠️ Fair match. Consider improving skills or gaining more experience."
        else:
            return "❌ Poor match. Significant skill/experience gaps need to be addressed."

    def _dict_to_resume_data(self, data: Dict) -> ResumeData:
        """Convert dictionary to ResumeData object."""
        # This is a simplified conversion - in practice you'd want more robust handling
        resume = ResumeData()

        if 'skills' in data:
            resume.skills = data['skills']
        if 'experience' in data:
            resume.experience = [Experience(
                **exp) if isinstance(exp, dict) else exp for exp in data['experience']]
        if 'summary' in data:
            resume.summary = data['summary']
        # Add other fields as needed

        return resume

    def _dict_to_job_posting(self, data: Dict) -> JobPosting:
        """Convert dictionary to JobPosting object."""
        return JobPosting(**data)

    def _update_weights(self, custom_weights: Dict) -> None:
        """Update scoring weights with custom values."""
        for key, value in custom_weights.items():
            if key in self.weights:
                self.weights[key] = value

    def _format_match_result(self, result: JobMatchResult) -> str:
        """Format single match result for display."""
        lines = [
            "🎯 Job Match Analysis",
            "=" * 50,
            "",
            f"📋 Job: {result.job.title} at {result.job.company}",
            f"📍 Location: {result.job.location}",
            "",
            f"🏆 Overall Match Score: {result.match_score.total_score:.1f}%",
            "",
            "📊 Detailed Scores:",
            f"   🛠️  Skills: {result.match_score.skills_score:.1f}%",
            f"   💼 Experience: {result.match_score.experience_score:.1f}%",
            f"   🔑 Keywords: {result.match_score.keyword_score:.1f}%",
            f"   📍 Location: {result.match_score.location_score:.1f}%",
            "",
            f"✅ Skills Matched ({len(result.match_score.skills_matched)}):",
        ]

        for skill in result.match_score.skills_matched:
            lines.append(f"   • {skill}")

        if result.match_score.skills_missing:
            lines.append(
                f"\n❌ Skills Missing ({len(result.match_score.skills_missing)}):")
            for skill in result.match_score.skills_missing:
                lines.append(f"   • {skill}")

        lines.extend([
            "",
            f"💡 {result.match_score.recommendation}",
            "",
            f"📝 Analysis: {result.match_score.explanation}"
        ])

        return "\n".join(lines)

    def _format_batch_results(self, matches: List[JobMatchResult], threshold: float) -> str:
        """Format batch match results for display."""
        if not matches:
            return f"❌ No jobs found matching threshold of {threshold}%"

        lines = [
            "🎯 Batch Job Matching Results",
            "=" * 50,
            f"Found {len(matches)} jobs above {threshold}% threshold:",
            ""
        ]

        for i, result in enumerate(matches, 1):
            lines.extend([
                f"#{i}. {result.job.title} at {result.job.company}",
                f"    Score: {result.match_score.total_score:.1f}% | {result.match_score.recommendation.split('!')[0]}",
                f"    Skills: {result.match_score.skills_score:.1f}% | Experience: {result.match_score.experience_score:.1f}%",
                ""
            ])

        return "\n".join(lines)

    def _generate_detailed_analysis(self, resume: ResumeData, job: JobPosting, match_score: MatchScore) -> str:
        """Generate detailed job fit analysis with recommendations."""
        lines = [
            "🔍 Detailed Job Fit Analysis",
            "=" * 50,
            "",
            f"📋 Position: {job.title} at {job.company}",
            f"🏆 Overall Compatibility: {match_score.total_score:.1f}%",
            "",
            "📈 Strengths:",
        ]

        # Identify strengths
        if match_score.skills_score >= 80:
            lines.append(
                f"   ✅ Strong skills match ({match_score.skills_score:.1f}%)")
        if match_score.experience_score >= 80:
            lines.append(
                f"   ✅ Excellent experience level ({match_score.experience_years:.1f} years)")
        if match_score.keyword_score >= 80:
            lines.append(
                f"   ✅ Good keyword alignment ({match_score.keyword_score:.1f}%)")

        lines.append("\n📉 Areas for Improvement:")

        # Identify improvement areas
        if match_score.skills_score < 70:
            lines.append(
                f"   ⚠️ Skills gap: Missing {len(match_score.skills_missing)} key skills")
            lines.append(
                f"      Consider learning: {', '.join(match_score.skills_missing[:3])}")

        if match_score.experience_score < 70:
            required_exp = self._extract_required_experience(job.description)
            if required_exp > match_score.experience_years:
                gap = required_exp - match_score.experience_years
                lines.append(
                    f"   ⚠️ Experience gap: Need {gap:.1f} more years")

        if match_score.keyword_score < 70:
            lines.append(f"   ⚠️ Keyword optimization needed for ATS systems")

        lines.extend([
            "",
            f"🎯 Recommendation: {match_score.recommendation}",
            "",
            "💡 Next Steps:",
            "   1. Focus on missing skills through courses/projects",
            "   2. Tailor resume keywords to job description",
            "   3. Highlight relevant experience more prominently"
        ])

        return "\n".join(lines)
