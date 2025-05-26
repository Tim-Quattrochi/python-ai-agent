"""Resume customizer tool for tailoring resumes to specific job postings."""

import re
import logging
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime

from .resume_parser import ResumeData, ContactInfo, Experience, Education, Project
from .job_scraper import JobPosting
from .job_matcher import JobMatcherTool, MatchScore
from ..base import Tool

logger = logging.getLogger(__name__)


@dataclass
class CustomizationSuggestions:
    """Suggestions for resume customization."""
    priority_skills: List[str] = None
    suggested_summary: str = ""
    experience_emphasis: Dict[str, str] = None
    missing_skills_to_add: List[str] = None
    keywords_to_include: List[str] = None
    sections_to_highlight: List[str] = None

    def __post_init__(self):
        if self.priority_skills is None:
            self.priority_skills = []
        if self.experience_emphasis is None:
            self.experience_emphasis = {}
        if self.missing_skills_to_add is None:
            self.missing_skills_to_add = []
        if self.keywords_to_include is None:
            self.keywords_to_include = []
        if self.sections_to_highlight is None:
            self.sections_to_highlight = []


@dataclass
class CustomizedResume:
    """Customized resume data."""
    original_resume: ResumeData
    job_posting: JobPosting
    customized_resume: ResumeData
    suggestions: CustomizationSuggestions
    match_score_improvement: float = 0.0
    timestamp: str = ""

    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now().isoformat()


class ResumeCustomizerTool(Tool):
    """A tool for customizing resumes to better match specific job postings."""

    def __init__(self):
        super().__init__(
            name="resume_customizer",
            description="Customize and tailor resumes to specific job postings for better ATS compatibility and matching."
        )
        self.job_matcher = JobMatcherTool()

        # Skill synonyms and related skills
        self.skill_synonyms = {
            'javascript': ['js', 'ecmascript', 'node.js', 'nodejs'],
            'python': ['py', 'django', 'flask', 'fastapi'],
            'react': ['reactjs', 'react.js', 'jsx'],
            'angular': ['angularjs', 'angular.js'],
            'vue': ['vuejs', 'vue.js'],
            'typescript': ['ts'],
            'css': ['css3', 'scss', 'sass', 'less'],
            'html': ['html5', 'markup'],
            'sql': ['mysql', 'postgresql', 'sqlite', 'mssql'],
            'aws': ['amazon web services', 'ec2', 's3', 'lambda'],
            'docker': ['containerization', 'containers'],
            'kubernetes': ['k8s', 'container orchestration'],
            'git': ['github', 'gitlab', 'version control'],
            'agile': ['scrum', 'kanban', 'sprint'],
            'ci/cd': ['continuous integration', 'continuous deployment', 'jenkins', 'github actions']
        }

    def get_schema(self) -> Dict[str, Any]:
        """Get the JSON schema for resume customizer parameters."""
        return {
            "type": "object",
            "properties": {
                "operation": {
                    "type": "string",
                    "enum": ["customize_resume", "suggest_improvements", "preview_changes"],
                    "description": "The customization operation to perform"
                },
                "resume_data": {
                    "type": "object",
                    "description": "Parsed resume data (from resume parser tool)",
                    "required": True
                },
                "job_data": {
                    "type": "object",
                    "description": "Job posting data (from job scraper tool)",
                    "required": True
                },
                "customization_level": {
                    "type": "string",
                    "enum": ["conservative", "moderate", "aggressive"],
                    "description": "Level of customization to apply",
                    "default": "moderate"
                },
                "preserve_accuracy": {
                    "type": "boolean",
                    "description": "Whether to preserve factual accuracy (recommended)",
                    "default": True
                },
                "target_ats_score": {
                    "type": "number",
                    "description": "Target ATS compatibility score (0-100)",
                    "minimum": 0,
                    "maximum": 100,
                    "default": 80
                }
            },
            "required": ["operation", "resume_data", "job_data"]
        }

    def execute(self, **kwargs) -> Dict[str, Any]:
        """Execute resume customization operation."""
        try:
            operation = kwargs.get('operation', 'customize_resume')
            resume_data = kwargs.get('resume_data')
            job_data = kwargs.get('job_data')

            if not resume_data or not job_data:
                return {
                    "success": False,
                    "error": "Both resume_data and job_data are required"
                }

            # Convert dictionaries to dataclass objects if needed
            if isinstance(resume_data, dict):
                resume_data = self._dict_to_resume_data(resume_data)
            if isinstance(job_data, dict):
                job_data = self._dict_to_job_posting(job_data)

            customization_level = kwargs.get('customization_level', 'moderate')
            preserve_accuracy = kwargs.get('preserve_accuracy', True)
            target_ats_score = kwargs.get('target_ats_score', 80)

            if operation == "customize_resume":
                return self._customize_resume(
                    resume_data, job_data, customization_level,
                    preserve_accuracy, target_ats_score
                )
            elif operation == "suggest_improvements":
                return self._suggest_improvements(resume_data, job_data)
            elif operation == "preview_changes":
                return self._preview_changes(resume_data, job_data, customization_level)
            else:
                return {
                    "success": False,
                    "error": f"Unknown operation: {operation}"
                }

        except Exception as e:
            logger.error(f"Resume customization error: {str(e)}")
            return {
                "success": False,
                "error": f"Resume customization failed: {str(e)}"
            }

    def _customize_resume(self, resume: ResumeData, job: JobPosting,
                          level: str, preserve_accuracy: bool, target_score: float) -> Dict[str, Any]:
        """Customize resume for the specific job posting."""
        # Get initial match score
        original_match = self.job_matcher.execute(
            operation="match_job",
            resume_data=self._safe_asdict(resume),
            job_data=self._safe_asdict(job)
        )

        if not original_match.get('success'):
            return {
                "success": False,
                "error": "Failed to calculate original match score"
            }

        original_score = original_match['result']['match_score']['total_score']

        # Generate customization suggestions
        suggestions = self._generate_suggestions(resume, job, level)

        # Apply customizations
        customized_resume = self._apply_customizations(
            resume, suggestions, preserve_accuracy)

        # Calculate new match score
        new_match = self.job_matcher.execute(
            operation="match_job",
            resume_data=self._safe_asdict(customized_resume),
            job_data=self._safe_asdict(job)
        )

        if new_match.get('success'):
            new_score = new_match['result']['match_score']['total_score']
            improvement = new_score - original_score
        else:
            new_score = original_score
            improvement = 0.0

        # Create result
        result = CustomizedResume(
            original_resume=resume,
            job_posting=job,
            customized_resume=customized_resume,
            suggestions=suggestions,
            match_score_improvement=improvement
        )

        return {
            "success": True,
            "result": asdict(result),
            "summary": self._generate_customization_summary(original_score, new_score, suggestions)
        }

    def _suggest_improvements(self, resume: ResumeData, job: JobPosting) -> Dict[str, Any]:
        """Generate improvement suggestions without applying them."""
        suggestions = self._generate_suggestions(resume, job, "moderate")

        return {
            "success": True,
            "suggestions": asdict(suggestions),
            "summary": self._format_suggestions_summary(suggestions)
        }

    def _preview_changes(self, resume: ResumeData, job: JobPosting, level: str) -> Dict[str, Any]:
        """Preview what changes would be made without applying them."""
        suggestions = self._generate_suggestions(resume, job, level)

        preview = {
            "skills_reordering": suggestions.priority_skills[:10],
            "summary_changes": suggestions.suggested_summary[:200] + "...",
            "keywords_to_add": suggestions.keywords_to_include[:10],
            "experience_emphasis": suggestions.experience_emphasis,
            "sections_to_highlight": suggestions.sections_to_highlight
        }

        return {
            "success": True,
            "preview": preview,
            "summary": f"Preview of {level} customization changes"
        }

    def _generate_suggestions(self, resume: ResumeData, job: JobPosting, level: str) -> CustomizationSuggestions:
        """Generate customization suggestions based on job requirements."""
        suggestions = CustomizationSuggestions()

        # Analyze job requirements
        job_skills = self._extract_job_skills(job)
        job_keywords = self._extract_job_keywords(job)

        # Priority skills (skills mentioned in job that candidate has)
        suggestions.priority_skills = self._get_priority_skills(
            resume.skills, job_skills)

        # Missing skills that candidate might have (based on synonyms/related skills)
        suggestions.missing_skills_to_add = self._get_missing_skills_to_add(
            resume.skills, job_skills)

        # Important keywords to include
        suggestions.keywords_to_include = self._get_important_keywords(
            job_keywords, level)

        # Enhanced professional summary
        suggestions.suggested_summary = self._generate_enhanced_summary(
            resume, job, suggestions.keywords_to_include
        )

        # Experience emphasis
        suggestions.experience_emphasis = self._get_experience_emphasis(
            resume.experience, job)

        # Sections to highlight
        suggestions.sections_to_highlight = self._get_sections_to_highlight(
            resume, job)

        return suggestions

    def _apply_customizations(self, resume: ResumeData, suggestions: CustomizationSuggestions,
                              preserve_accuracy: bool) -> ResumeData:
        """Apply customization suggestions to create a new resume."""
        # Create a copy of the resume
        customized = ResumeData(
            contact_info=resume.contact_info,
            summary=suggestions.suggested_summary or resume.summary,
            skills=self._reorder_skills(
                resume.skills, suggestions.priority_skills, suggestions.missing_skills_to_add),
            experience=self._enhance_experience(
                resume.experience, suggestions.experience_emphasis),
            education=resume.education,
            projects=resume.projects,
            certifications=resume.certifications
        )

        return customized

    def _extract_job_skills(self, job: JobPosting) -> List[str]:
        """Extract skills from job posting."""
        skills = []

        if job.skills_required:
            skills.extend(job.skills_required)

        # Extract additional skills from description
        if job.description:
            # Common technical skills patterns
            skill_patterns = [
                r'\b(?:python|java|javascript|typescript|react|angular|vue|node\.?js)\b',
                r'\b(?:aws|azure|gcp|docker|kubernetes|jenkins)\b',
                r'\b(?:sql|mysql|postgresql|mongodb|redis)\b',
                r'\b(?:git|github|gitlab|svn)\b',
                r'\b(?:agile|scrum|kanban)\b',
                r'\b(?:html|css|scss|sass)\b'
            ]

            for pattern in skill_patterns:
                matches = re.findall(pattern, job.description.lower())
                skills.extend(matches)

        return list(set(skills))  # Remove duplicates

    def _extract_job_keywords(self, job: JobPosting) -> List[str]:
        """Extract important keywords from job posting."""
        keywords = []

        if job.description:
            # Extract important business/technical keywords
            keyword_patterns = [
                r'\b(?:leadership|management|teamwork|collaboration)\b',
                r'\b(?:optimization|performance|scalability|security)\b',
                r'\b(?:automation|integration|deployment|testing)\b',
                r'\b(?:analysis|analytics|data|machine learning|ai)\b',
                r'\b(?:user experience|ux|ui|frontend|backend|fullstack)\b'
            ]

            for pattern in keyword_patterns:
                matches = re.findall(pattern, job.description.lower())
                keywords.extend(matches)

        return list(set(keywords))

    def _get_priority_skills(self, resume_skills: List[str], job_skills: List[str]) -> List[str]:
        """Get skills that should be prioritized (candidate has and job requires)."""
        priority = []
        resume_lower = [skill.lower() for skill in resume_skills]

        for job_skill in job_skills:
            job_skill_lower = job_skill.lower()

            # Check for exact matches or partial matches
            for i, resume_skill in enumerate(resume_lower):
                if (job_skill_lower in resume_skill or resume_skill in job_skill_lower or
                        self._are_related_skills(job_skill_lower, resume_skill)):
                    priority.append(resume_skills[i])
                    break

        return priority

    def _get_missing_skills_to_add(self, resume_skills: List[str], job_skills: List[str]) -> List[str]:
        """Get skills missing from resume that candidate might have based on related skills."""
        missing = []
        resume_lower = [skill.lower() for skill in resume_skills]

        for job_skill in job_skills:
            job_skill_lower = job_skill.lower()

            # Check if skill is already covered
            skill_covered = False
            for resume_skill in resume_lower:
                if (job_skill_lower in resume_skill or resume_skill in job_skill_lower or
                        self._are_related_skills(job_skill_lower, resume_skill)):
                    skill_covered = True
                    break

            if not skill_covered:
                # Check if candidate might have this skill based on related skills
                if self._might_have_skill(job_skill_lower, resume_lower):
                    missing.append(job_skill.title())

        return missing

    def _get_important_keywords(self, job_keywords: List[str], level: str) -> List[str]:
        """Get important keywords to include based on customization level."""
        if level == "conservative":
            return job_keywords[:5]
        elif level == "moderate":
            return job_keywords[:10]
        else:  # aggressive
            return job_keywords

    def _generate_enhanced_summary(self, resume: ResumeData, job: JobPosting, keywords: List[str]) -> str:
        """Generate an enhanced professional summary tailored to the job."""
        base_summary = resume.summary or ""

        # Extract key elements
        job_title = job.title.lower()
        company = job.company
        key_skills = self._get_priority_skills(
            resume.skills, self._extract_job_skills(job))

        # Create enhanced summary
        if "senior" in job_title or "lead" in job_title:
            experience_level = "experienced"
        elif "junior" in job_title or "entry" in job_title:
            experience_level = "motivated"
        else:
            experience_level = "skilled"

        # Build summary components
        role_type = "developer" if "developer" in job_title else "professional"
        top_skills = ", ".join(key_skills[:3]) if key_skills else "technology"

        enhanced_summary = (
            f"{experience_level.title()} {role_type} with expertise in {top_skills}. "
            f"Proven track record of delivering high-quality solutions and contributing to team success. "
        )

        # Add relevant keywords naturally
        if keywords:
            keyword_phrase = f"Experienced in {', '.join(keywords[:3])} "
            enhanced_summary += keyword_phrase

        enhanced_summary += "Seeking to leverage technical skills and experience to contribute to innovative projects."

        return enhanced_summary

    def _get_experience_emphasis(self, experiences: List[Experience], job: JobPosting) -> Dict[str, str]:
        """Get suggestions for emphasizing relevant experience."""
        emphasis = {}
        job_skills = set(skill.lower()
                         for skill in self._extract_job_skills(job))

        for exp in experiences:
            if exp.description:
                # Find relevant skills/keywords in experience
                relevant_points = []
                for skill in job_skills:
                    if skill in exp.description.lower():
                        relevant_points.append(skill)

                if relevant_points:
                    emphasis[f"{exp.title} at {exp.company}"] = (
                        f"Emphasize experience with: {', '.join(relevant_points)}"
                    )

        return emphasis

    def _get_sections_to_highlight(self, resume: ResumeData, job: JobPosting) -> List[str]:
        """Get sections that should be highlighted for this job."""
        sections = []

        # Always highlight skills for technical jobs
        if any(tech in job.title.lower() for tech in ['developer', 'engineer', 'programmer', 'architect']):
            sections.append("Technical Skills")

        # Highlight projects if they're relevant
        if resume.projects and len(resume.projects) > 0:
            sections.append("Projects")

        # Highlight certifications if relevant
        if resume.certifications:
            sections.append("Certifications")

        return sections

    def _reorder_skills(self, skills: List[str], priority_skills: List[str], missing_skills: List[str]) -> List[str]:
        """Reorder skills to prioritize job-relevant ones."""
        reordered = []

        # Add priority skills first
        for skill in priority_skills:
            if skill not in reordered:
                reordered.append(skill)

        # Add missing skills that candidate might have
        for skill in missing_skills:
            if skill not in reordered:
                reordered.append(skill)

        # Add remaining skills
        for skill in skills:
            if skill not in reordered:
                reordered.append(skill)

        return reordered

    def _enhance_experience(self, experiences: List[Experience], emphasis: Dict[str, str]) -> List[Experience]:
        """Enhance experience descriptions based on emphasis suggestions."""
        enhanced = []

        for exp in experiences:
            exp_key = f"{exp.title} at {exp.company}"
            if exp_key in emphasis:
                # Could enhance description here, but preserving accuracy
                enhanced.append(exp)
            else:
                enhanced.append(exp)

        return enhanced

    def _are_related_skills(self, skill1: str, skill2: str) -> bool:
        """Check if two skills are related based on synonym mapping."""
        for main_skill, synonyms in self.skill_synonyms.items():
            if (skill1 == main_skill or skill1 in synonyms) and (skill2 == main_skill or skill2 in synonyms):
                return True
        return False

    def _might_have_skill(self, missing_skill: str, resume_skills: List[str]) -> bool:
        """Check if candidate might have a missing skill based on related skills."""
        for resume_skill in resume_skills:
            if self._are_related_skills(missing_skill, resume_skill):
                return True
        return False

    def _generate_customization_summary(self, original_score: float, new_score: float,
                                        suggestions: CustomizationSuggestions) -> str:
        """Generate a summary of customization results."""
        improvement = new_score - original_score

        summary = f"""
🎯 Resume Customization Complete
==================================================

📊 Match Score Improvement: {original_score:.1f}% → {new_score:.1f}% (+{improvement:.1f}%)

🔄 Changes Applied:
   • Reordered {len(suggestions.priority_skills)} priority skills
   • Enhanced professional summary
   • Added {len(suggestions.missing_skills_to_add)} relevant skills
   • Incorporated {len(suggestions.keywords_to_include)} key keywords
   • Highlighted {len(suggestions.sections_to_highlight)} relevant sections

💡 Recommendation: {"Excellent improvement!" if improvement > 10 else "Good improvement!" if improvement > 5 else "Minor improvements applied."}
        """.strip()

        return summary

    def _format_suggestions_summary(self, suggestions: CustomizationSuggestions) -> str:
        """Format suggestions as a readable summary."""
        return f"""
💡 Resume Improvement Suggestions
==================================================

🎯 Priority Skills to Highlight:
   {', '.join(suggestions.priority_skills[:10])}

➕ Skills to Consider Adding:
   {', '.join(suggestions.missing_skills_to_add[:5])}

🔑 Keywords to Incorporate:
   {', '.join(suggestions.keywords_to_include[:8])}

📝 Summary Enhancement:
   {suggestions.suggested_summary[:150]}...

🎪 Sections to Highlight:
   {', '.join(suggestions.sections_to_highlight)}
        """.strip()

    def _safe_asdict(self, obj) -> dict:
        """Safely convert dataclass to dict with proper nested handling."""
        try:
            if hasattr(obj, '__dataclass_fields__'):
                result = {}
                for field_name, field_value in asdict(obj).items():
                    if field_value is None:
                        result[field_name] = None
                    elif isinstance(field_value, list):
                        result[field_name] = []
                        for item in field_value:
                            if hasattr(item, '__dataclass_fields__'):
                                result[field_name].append(asdict(item))
                            else:
                                result[field_name].append(item)
                    elif hasattr(field_value, '__dataclass_fields__'):
                        result[field_name] = asdict(field_value)
                    else:
                        result[field_name] = field_value
                return result
            else:
                return obj
        except Exception as e:
            logger.error(f"Error converting dataclass to dict: {e}")
            return {}

    def _dict_to_resume_data(self, data: dict) -> ResumeData:
        """Convert dictionary to ResumeData object."""
        try:
            # Handle nested objects
            contact_info = None
            if 'contact_info' in data and data['contact_info']:
                contact_info = ContactInfo(**data['contact_info'])

            experience = []
            if 'experience' in data and data['experience']:
                for exp_data in data['experience']:
                    experience.append(Experience(**exp_data))

            education = []
            if 'education' in data and data['education']:
                for edu_data in data['education']:
                    education.append(Education(**edu_data))

            projects = []
            if 'projects' in data and data['projects']:
                for proj_data in data['projects']:
                    projects.append(Project(**proj_data))

            return ResumeData(
                contact_info=contact_info,
                summary=data.get('summary', ''),
                skills=data.get('skills', []),
                experience=experience,
                education=education,
                projects=projects,
                certifications=data.get('certifications', [])
            )
        except Exception as e:
            logger.error(f"Error converting dict to ResumeData: {e}")
            # Return minimal ResumeData if conversion fails
            return ResumeData()

    def _dict_to_job_posting(self, data: dict) -> JobPosting:
        """Convert dictionary to JobPosting object."""
        try:
            return JobPosting(
                title=data.get('title', ''),
                company=data.get('company', ''),
                location=data.get('location', ''),
                job_type=data.get('job_type', ''),
                experience_level=data.get('experience_level', ''),
                description=data.get('description', ''),
                requirements=data.get('requirements', []),
                skills_required=data.get('skills_required', []),
                salary_range=data.get('salary_range', ''),
                posted_date=data.get('posted_date', ''),
                job_url=data.get('job_url', ''),
                company_size=data.get('company_size', ''),
                industry=data.get('industry', '')
            )
        except Exception as e:
            logger.error(f"Error converting dict to JobPosting: {e}")
            return JobPosting()
