"""Cover letter generator tool for creating personalized cover letters."""

import re
import logging
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, asdict
from datetime import datetime

from .resume_parser import ResumeData, Experience
from .job_scraper import JobPosting
from .company_research import CompanyInfo, ResearchSummary
from .job_matcher import JobMatcherTool
from ..base import Tool

logger = logging.getLogger(__name__)


@dataclass
class CoverLetterTemplate:
    """Cover letter template structure."""
    name: str = ""
    style: str = ""  # professional, creative, technical, executive
    tone: str = ""   # formal, conversational, enthusiastic, confident
    # paragraph types: intro, value_prop, experience, company_fit, closing
    structure: List[str] = None
    placeholders: Dict[str, str] = None

    def __post_init__(self):
        if self.structure is None:
            self.structure = ["intro", "value_prop",
                              "experience", "company_fit", "closing"]
        if self.placeholders is None:
            self.placeholders = {}


@dataclass
class CoverLetterContent:
    """Generated cover letter content."""
    subject_line: str = ""
    greeting: str = ""
    introduction: str = ""
    value_proposition: str = ""
    experience_highlight: str = ""
    company_fit: str = ""
    closing: str = ""
    signature: str = ""
    full_letter: str = ""
    word_count: int = 0
    key_points_covered: List[str] = None

    def __post_init__(self):
        if self.key_points_covered is None:
            self.key_points_covered = []


@dataclass
class CoverLetterResult:
    """Complete cover letter generation result."""
    job_posting: JobPosting
    resume_data: ResumeData
    company_info: Optional[CompanyInfo]
    template_used: CoverLetterTemplate
    content: CoverLetterContent
    personalization_score: float = 0.0
    generation_timestamp: str = ""

    def __post_init__(self):
        if not self.generation_timestamp:
            self.generation_timestamp = datetime.now().isoformat()


class CoverLetterGeneratorTool(Tool):
    """A tool for generating personalized cover letters based on resume, job posting, and company research."""

    def __init__(self):
        super().__init__(
            name="cover_letter_generator",
            description="Generate personalized cover letters that match job requirements and company culture."
        )

        # Predefined templates
        self.templates = {
            "professional": CoverLetterTemplate(
                name="Professional",
                style="professional",
                tone="formal",
                structure=["intro", "value_prop",
                           "experience", "company_fit", "closing"]
            ),
            "technical": CoverLetterTemplate(
                name="Technical",
                style="technical",
                tone="confident",
                structure=["intro", "technical_skills",
                           "project_experience", "problem_solving", "closing"]
            ),
            "creative": CoverLetterTemplate(
                name="Creative",
                style="creative",
                tone="enthusiastic",
                structure=["engaging_intro", "unique_value",
                           "creative_experience", "culture_fit", "memorable_closing"]
            ),
            "executive": CoverLetterTemplate(
                name="Executive",
                style="executive",
                tone="confident",
                structure=["leadership_intro", "strategic_value",
                           "leadership_experience", "vision_alignment", "action_closing"]
            )
        }

    def get_schema(self) -> Dict[str, Any]:
        """Get the JSON schema for cover letter generator parameters."""
        return {
            "type": "object",
            "properties": {
                "operation": {
                    "type": "string",
                    "enum": ["generate_cover_letter", "customize_template", "analyze_requirements"],
                    "description": "The operation to perform"
                },
                "resume_data": {
                    "type": "object",
                    "description": "Parsed resume data (from resume parser tool)",
                    "required": True
                },
                "job_posting": {
                    "type": "object",
                    "description": "Job posting data (from job scraper tool)",
                    "required": True
                },
                "company_info": {
                    "type": "object",
                    "description": "Company research data (from company research tool)"
                },
                "template_style": {
                    "type": "string",
                    "enum": ["professional", "technical", "creative", "executive", "auto"],
                    "description": "Cover letter template style",
                    "default": "auto"
                },
                "tone": {
                    "type": "string",
                    "enum": ["formal", "conversational", "enthusiastic", "confident"],
                    "description": "Tone of the cover letter",
                    "default": "professional"
                },
                "length": {
                    "type": "string",
                    "enum": ["concise", "standard", "detailed"],
                    "description": "Desired length of cover letter",
                    "default": "standard"
                },
                "focus_areas": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Areas to emphasize in the cover letter",
                    "default": ["skills", "experience", "company_fit"]
                },
                "include_salary": {
                    "type": "boolean",
                    "description": "Whether to include salary expectations",
                    "default": False
                },
                "include_availability": {
                    "type": "boolean",
                    "description": "Whether to include availability information",
                    "default": True
                }
            },
            "required": ["operation", "resume_data", "job_posting"]
        }

    def execute(self, **kwargs) -> Dict[str, Any]:
        """Execute cover letter generation operation."""
        try:
            operation = kwargs.get('operation', 'generate_cover_letter')

            if operation == "generate_cover_letter":
                return self._generate_cover_letter(**kwargs)
            elif operation == "customize_template":
                return self._customize_template(**kwargs)
            elif operation == "analyze_requirements":
                return self._analyze_requirements(**kwargs)
            else:
                return {
                    "success": False,
                    "error": f"Unknown operation: {operation}"
                }

        except Exception as e:
            logger.error(f"Cover letter generation error: {str(e)}")
            return {
                "success": False,
                "error": f"Cover letter generation failed: {str(e)}"
            }

    def _generate_cover_letter(self, **kwargs) -> Dict[str, Any]:
        """Generate a complete cover letter."""
        # Extract parameters
        resume_data = kwargs.get('resume_data')
        job_posting = kwargs.get('job_posting')
        company_info = kwargs.get('company_info')

        if not resume_data or not job_posting:
            return {
                "success": False,
                "error": "Both resume_data and job_posting are required"
            }

        # Convert dictionaries to objects if needed
        if isinstance(resume_data, dict):
            resume_data = self._dict_to_resume_data(resume_data)
        if isinstance(job_posting, dict):
            job_posting = self._dict_to_job_posting(job_posting)
        if isinstance(company_info, dict):
            company_info = self._dict_to_company_info(company_info)

        # Determine template
        template_style = kwargs.get('template_style', 'auto')
        if template_style == 'auto':
            template = self._select_best_template(job_posting, resume_data)
        else:
            template = self.templates.get(
                template_style, self.templates['professional'])

        # Generate content
        content = self._generate_content(
            resume_data, job_posting, company_info, template, kwargs
        )

        # Calculate personalization score
        personalization_score = self._calculate_personalization_score(
            content, job_posting, company_info
        )

        # Create result
        result = CoverLetterResult(
            job_posting=job_posting,
            resume_data=resume_data,
            company_info=company_info,
            template_used=template,
            content=content,
            personalization_score=personalization_score
        )

        return {
            "success": True,
            "result": asdict(result),
            "cover_letter": content.full_letter,
            "summary": self._format_generation_summary(result)
        }

    def _customize_template(self, **kwargs) -> Dict[str, Any]:
        """Customize a template for specific requirements."""
        template_style = kwargs.get('template_style', 'professional')
        customizations = kwargs.get('customizations', {})

        base_template = self.templates.get(
            template_style, self.templates['professional'])

        # Apply customizations
        customized_template = CoverLetterTemplate(
            name=customizations.get('name', base_template.name),
            style=customizations.get('style', base_template.style),
            tone=customizations.get('tone', base_template.tone),
            structure=customizations.get('structure', base_template.structure),
            placeholders=customizations.get(
                'placeholders', base_template.placeholders)
        )

        return {
            "success": True,
            "template": asdict(customized_template),
            "summary": f"Customized {template_style} template with {len(customizations)} modifications"
        }

    def _analyze_requirements(self, **kwargs) -> Dict[str, Any]:
        """Analyze job requirements for cover letter strategy."""
        job_posting = kwargs.get('job_posting')

        if isinstance(job_posting, dict):
            job_posting = self._dict_to_job_posting(job_posting)

        analysis = {
            "recommended_template": self._select_best_template(job_posting, None).name,
            "key_skills_to_highlight": self._extract_key_skills(job_posting),
            "tone_recommendations": self._recommend_tone(job_posting),
            "length_recommendation": self._recommend_length(job_posting),
            "focus_areas": self._identify_focus_areas(job_posting)
        }

        return {
            "success": True,
            "analysis": analysis,
            "summary": self._format_analysis_summary(analysis, job_posting)
        }

    def _select_best_template(self, job_posting: JobPosting, resume_data: Optional[ResumeData]) -> CoverLetterTemplate:
        """Select the best template based on job posting and resume."""
        job_title = job_posting.title.lower()
        job_description = job_posting.description.lower() if job_posting.description else ""

        # Technical roles
        if any(tech in job_title for tech in ['developer', 'engineer', 'programmer', 'architect', 'devops']):
            return self.templates['technical']

        # Executive roles
        if any(exec_role in job_title for exec_role in ['director', 'vp', 'president', 'ceo', 'cto', 'manager', 'lead']):
            return self.templates['executive']

        # Creative roles
        if any(creative in job_title for creative in ['designer', 'creative', 'marketing', 'content', 'writer']):
            return self.templates['creative']

        # Default to professional
        return self.templates['professional']

    def _generate_content(self, resume: ResumeData, job: JobPosting, company: Optional[CompanyInfo],
                          template: CoverLetterTemplate, options: dict) -> CoverLetterContent:
        """Generate the actual cover letter content."""
        content = CoverLetterContent()

        # Generate subject line
        content.subject_line = self._generate_subject_line(job, resume)

        # Generate greeting
        content.greeting = self._generate_greeting(job, company)

        # Generate sections based on template structure
        sections = []
        for section_type in template.structure:
            section_content = self._generate_section(
                section_type, resume, job, company, template, options)
            sections.append(section_content)

            # Store sections in appropriate fields
            if section_type in ['intro', 'engaging_intro', 'leadership_intro']:
                content.introduction = section_content
            elif section_type in ['value_prop', 'unique_value', 'strategic_value']:
                content.value_proposition = section_content
            elif section_type in ['experience', 'project_experience', 'leadership_experience']:
                content.experience_highlight = section_content
            elif section_type in ['company_fit', 'culture_fit', 'vision_alignment']:
                content.company_fit = section_content
            elif section_type in ['closing', 'memorable_closing', 'action_closing']:
                content.closing = section_content

        # Generate signature
        content.signature = self._generate_signature(resume)

        # Assemble full letter
        content.full_letter = self._assemble_full_letter(content, sections)
        content.word_count = len(content.full_letter.split())

        # Track key points covered
        content.key_points_covered = self._identify_key_points_covered(
            content, job)

        return content

    def _generate_subject_line(self, job: JobPosting, resume: ResumeData) -> str:
        """Generate an effective subject line."""
        applicant_name = resume.contact_info.name if resume.contact_info else "Application"

        subject_options = [
            f"Application for {job.title} - {applicant_name}",
            f"{job.title} Position - {applicant_name}",
            f"Experienced {job.title.split()[-1]} Seeking {job.title} Role",
            f"{applicant_name} - {job.title} Application"
        ]

        # Choose based on job level
        if any(level in job.title.lower() for level in ['senior', 'lead', 'principal']):
            return subject_options[2]  # Emphasize experience
        else:
            return subject_options[0]  # Standard format

    def _generate_greeting(self, job: JobPosting, company: Optional[CompanyInfo]) -> str:
        """Generate appropriate greeting."""
        if company and company.key_people:
            # If we know specific people (e.g., hiring manager)
            return f"Dear {company.key_people[0]},"
        elif job.company:
            return f"Dear {job.company} Hiring Team,"
        else:
            return "Dear Hiring Manager,"

    def _generate_section(self, section_type: str, resume: ResumeData, job: JobPosting,
                          company: Optional[CompanyInfo], template: CoverLetterTemplate, options: dict) -> str:
        """Generate content for a specific section."""
        if section_type in ['intro', 'engaging_intro', 'leadership_intro']:
            return self._generate_introduction(resume, job, company, template.tone)

        elif section_type in ['value_prop', 'unique_value', 'strategic_value']:
            return self._generate_value_proposition(resume, job, template.tone)

        elif section_type in ['experience', 'project_experience', 'leadership_experience', 'technical_skills']:
            return self._generate_experience_section(resume, job, section_type)

        elif section_type in ['company_fit', 'culture_fit', 'vision_alignment', 'problem_solving']:
            return self._generate_company_fit_section(resume, job, company, section_type)

        elif section_type in ['closing', 'memorable_closing', 'action_closing']:
            return self._generate_closing(resume, job, template.tone, options)

        else:
            return f"[{section_type.replace('_', ' ').title()} section]"

    def _generate_introduction(self, resume: ResumeData, job: JobPosting,
                               company: Optional[CompanyInfo], tone: str) -> str:
        """Generate introduction paragraph."""
        name = resume.contact_info.name if resume.contact_info else "I"
        years_exp = self._estimate_years_experience(resume)

        if tone == "enthusiastic":
            return f"I am thrilled to apply for the {job.title} position at {job.company}. As a passionate professional with {years_exp} years of experience, I am excited about the opportunity to contribute to your innovative team."

        elif tone == "confident":
            return f"I am writing to express my strong interest in the {job.title} role at {job.company}. With {years_exp} years of proven experience and a track record of delivering exceptional results, I am confident I would be a valuable addition to your team."

        else:  # formal/professional
            return f"I am writing to formally apply for the {job.title} position at {job.company}. With {years_exp} years of relevant experience and a strong background in the field, I believe I would be an excellent fit for this role."

    def _generate_value_proposition(self, resume: ResumeData, job: JobPosting, tone: str) -> str:
        """Generate value proposition paragraph."""
        # Extract top skills that match job requirements
        job_skills = self._extract_job_skills(job)
        matching_skills = self._find_matching_skills(resume.skills, job_skills)

        top_skills = ", ".join(
            matching_skills[:3]) if matching_skills else "relevant technical skills"

        if tone == "enthusiastic":
            return f"What sets me apart is my expertise in {top_skills}, combined with my passion for innovation and problem-solving. I thrive in challenging environments and am always eager to learn new technologies and methodologies."

        elif tone == "confident":
            return f"My core strengths lie in {top_skills}, where I have consistently delivered high-impact solutions. I bring a unique combination of technical expertise and strategic thinking that drives results."

        else:  # formal/professional
            return f"My professional experience encompasses {top_skills}, with a focus on delivering quality solutions that meet business objectives. I have a proven ability to work effectively both independently and as part of a team."

    def _generate_experience_section(self, resume: ResumeData, job: JobPosting, section_type: str) -> str:
        """Generate experience highlight section."""
        if not resume.experience:
            return "My background includes relevant experience that aligns well with the requirements of this position."

        # Find most relevant experience
        relevant_exp = self._find_most_relevant_experience(
            resume.experience, job)

        if relevant_exp:
            return f"In my role as {relevant_exp.title} at {relevant_exp.company}, {relevant_exp.description[:150]}... This experience has prepared me well for the challenges and opportunities in the {job.title} role."
        else:
            return f"Throughout my career, I have developed strong expertise in areas directly relevant to the {job.title} position, including hands-on experience with key technologies and methodologies."

    def _generate_company_fit_section(self, resume: ResumeData, job: JobPosting,
                                      company: Optional[CompanyInfo], section_type: str) -> str:
        """Generate company fit section."""
        company_name = job.company

        if company and company.values:
            values_text = f"I am particularly drawn to {company_name}'s commitment to {company.values[0]}"
            if len(company.values) > 1:
                values_text += f" and {company.values[1]}"
            return f"{values_text}. These values align perfectly with my own professional philosophy and approach to work."

        elif company and company.mission:
            return f"I am inspired by {company_name}'s mission and vision. {company.mission[:100]}... This resonates strongly with my own professional goals and values."

        else:
            return f"I am excited about the opportunity to contribute to {company_name}'s continued success and growth. The company's reputation for excellence and innovation makes this an ideal next step in my career."

    def _generate_closing(self, resume: ResumeData, job: JobPosting, tone: str, options: dict) -> str:
        """Generate closing paragraph."""
        base_closing = "I would welcome the opportunity to discuss how my experience and skills can contribute to your team's success."

        # Add availability if requested
        if options.get('include_availability', True):
            base_closing += " I am available for an interview at your convenience."

        # Add salary mention if requested
        if options.get('include_salary', False):
            base_closing += " I am open to discussing compensation based on the role's requirements and responsibilities."

        if tone == "enthusiastic":
            return f"{base_closing} Thank you for considering my application, and I look forward to hearing from you soon!"

        elif tone == "confident":
            return f"{base_closing} I am confident that my background and passion make me an ideal candidate for this position."

        else:  # formal/professional
            return f"{base_closing} Thank you for your time and consideration."

    def _generate_signature(self, resume: ResumeData) -> str:
        """Generate email signature."""
        if resume.contact_info:
            name = resume.contact_info.name or "Best regards"
            phone = f"\n{resume.contact_info.phone}" if resume.contact_info.phone else ""
            email = f"\n{resume.contact_info.email}" if resume.contact_info.email else ""
            return f"Sincerely,\n{name}{phone}{email}"
        else:
            return "Sincerely,\n[Your Name]"

    def _assemble_full_letter(self, content: CoverLetterContent, sections: List[str]) -> str:
        """Assemble the complete cover letter."""
        letter_parts = [
            content.greeting,
            "",  # Empty line
            content.introduction,
            "",
            content.value_proposition,
            "",
            content.experience_highlight,
            "",
            content.company_fit,
            "",
            content.closing,
            "",
            content.signature
        ]

        # Filter out empty sections
        letter_parts = [part for part in letter_parts if part]

        return "\n".join(letter_parts)

    # Helper methods
    def _extract_job_skills(self, job: JobPosting) -> List[str]:
        """Extract skills from job posting."""
        skills = []
        if job.skills_required:
            skills.extend(job.skills_required)

        # Extract from description
        if job.description:
            # Simple skill extraction patterns
            tech_patterns = [
                r'\b(?:Python|Java|JavaScript|React|Angular|Node\.js|SQL|AWS|Docker)\b',
                r'\b(?:Git|Agile|Scrum|DevOps|CI/CD|REST|API)\b'
            ]

            for pattern in tech_patterns:
                matches = re.findall(pattern, job.description, re.IGNORECASE)
                skills.extend(matches)

        return list(set(skills))

    def _extract_key_skills(self, job: JobPosting) -> List[str]:
        """Extract key skills from job posting for highlighting."""
        return self._extract_job_skills(job)[:10]  # Return top 10 skills

    def _find_matching_skills(self, resume_skills: List[str], job_skills: List[str]) -> List[str]:
        """Find skills that match between resume and job."""
        matching = []
        resume_lower = [skill.lower() for skill in resume_skills]

        for job_skill in job_skills:
            for resume_skill in resume_skills:
                if job_skill.lower() in resume_skill.lower() or resume_skill.lower() in job_skill.lower():
                    matching.append(resume_skill)
                    break

        return matching

    def _find_most_relevant_experience(self, experiences: List[Experience], job: JobPosting) -> Optional[Experience]:
        """Find the most relevant experience for the job."""
        if not experiences:
            return None

        # Simple heuristic: find experience with most matching keywords
        job_keywords = job.description.lower().split() if job.description else []
        best_match = None
        best_score = 0

        for exp in experiences:
            if exp.description:
                exp_words = exp.description.lower().split()
                score = sum(
                    1 for keyword in job_keywords if keyword in exp_words)
                if score > best_score:
                    best_score = score
                    best_match = exp

        return best_match or experiences[0]  # Return first if no good match

    def _estimate_years_experience(self, resume: ResumeData) -> str:
        """Estimate years of experience from resume."""
        if not resume.experience:
            return "several"

        # Simple estimation based on number of jobs
        num_jobs = len(resume.experience)
        if num_jobs >= 4:
            return "8+"
        elif num_jobs >= 3:
            return "5-7"
        elif num_jobs >= 2:
            return "3-5"
        else:
            return "2-3"

    def _calculate_personalization_score(self, content: CoverLetterContent,
                                         job: JobPosting, company: Optional[CompanyInfo]) -> float:
        """Calculate how personalized the cover letter is."""
        score = 0.0

        # Company name mentioned
        if job.company.lower() in content.full_letter.lower():
            score += 20

        # Job title mentioned
        if job.title.lower() in content.full_letter.lower():
            score += 20

        # Company values/culture mentioned
        if company and company.values:
            for value in company.values:
                if value.lower() in content.full_letter.lower():
                    score += 10
                    break

        # Skills matching
        job_skills = self._extract_job_skills(job)
        for skill in job_skills:
            if skill.lower() in content.full_letter.lower():
                score += 5

        # Length appropriate (not too short/long)
        if 150 <= content.word_count <= 400:
            score += 15

        return min(100.0, score)

    def _identify_key_points_covered(self, content: CoverLetterContent, job: JobPosting) -> List[str]:
        """Identify key points covered in the cover letter."""
        points = []
        letter_lower = content.full_letter.lower()

        if "experience" in letter_lower:
            points.append("Relevant Experience")
        if "skill" in letter_lower:
            points.append("Technical Skills")
        if job.company.lower() in letter_lower:
            points.append("Company Specific")
        if any(word in letter_lower for word in ["passion", "excited", "interested"]):
            points.append("Enthusiasm")
        if any(word in letter_lower for word in ["team", "collaborate", "work with"]):
            points.append("Teamwork")

        return points

    # Additional helper methods for template selection and analysis
    def _recommend_tone(self, job: JobPosting) -> str:
        """Recommend appropriate tone based on job posting."""
        job_desc = job.description.lower() if job.description else ""
        job_title = job.title.lower()

        if any(word in job_desc for word in ["innovative", "creative", "dynamic"]):
            return "enthusiastic"
        elif any(word in job_title for word in ["senior", "lead", "director", "manager"]):
            return "confident"
        else:
            return "professional"

    def _recommend_length(self, job: JobPosting) -> str:
        """Recommend appropriate length based on job posting."""
        if "senior" in job.title.lower() or "director" in job.title.lower():
            return "detailed"
        elif "entry" in job.title.lower() or "junior" in job.title.lower():
            return "concise"
        else:
            return "standard"

    def _identify_focus_areas(self, job: JobPosting) -> List[str]:
        """Identify what areas to focus on in the cover letter."""
        focus_areas = ["skills", "experience"]

        job_desc = job.description.lower() if job.description else ""

        if any(word in job_desc for word in ["team", "collaborate", "communication"]):
            focus_areas.append("teamwork")

        if any(word in job_desc for word in ["leadership", "manage", "lead"]):
            focus_areas.append("leadership")

        if any(word in job_desc for word in ["innovation", "creative", "problem-solving"]):
            focus_areas.append("innovation")

        focus_areas.append("company_fit")  # Always include

        return focus_areas

    def _format_generation_summary(self, result: CoverLetterResult) -> str:
        """Format the generation summary."""
        return f"""
✉️ Cover Letter Generated Successfully
==================================================

📋 Job: {result.job_posting.title} at {result.job_posting.company}
📝 Template: {result.template_used.name} ({result.template_used.style})
📊 Word Count: {result.content.word_count}
🎯 Personalization Score: {result.personalization_score:.1f}%

🔑 Key Points Covered:
   {', '.join(result.content.key_points_covered)}

📧 Subject Line: {result.content.subject_line}

💡 Recommendation: {"Excellent personalization!" if result.personalization_score >= 80 else "Good personalization!" if result.personalization_score >= 60 else "Consider adding more specific details about the company and role."}
        """.strip()

    def _format_analysis_summary(self, analysis: dict, job: JobPosting) -> str:
        """Format the analysis summary."""
        return f"""
📊 Cover Letter Strategy Analysis
==================================================

📋 Job: {job.title} at {job.company}

🎨 Recommended Template: {analysis['recommended_template']}
📢 Recommended Tone: {analysis['tone_recommendations']}
📏 Recommended Length: {analysis['length_recommendation']}

🎯 Focus Areas:
   {', '.join(analysis['focus_areas'])}

🛠️ Key Skills to Highlight:
   {', '.join(analysis['key_skills_to_highlight'][:5])}
        """.strip()

    # Conversion methods
    def _dict_to_resume_data(self, data: dict):
        """Convert dictionary to ResumeData object."""
        # Import here to avoid circular imports
        from .resume_parser import ResumeData, ContactInfo, Experience

        contact_info = None
        if 'contact_info' in data and data['contact_info']:
            contact_info = ContactInfo(**data['contact_info'])

        return ResumeData(
            contact_info=contact_info,
            summary=data.get('summary', ''),
            skills=data.get('skills', []),
            experience=[Experience(**exp)
                        for exp in data.get('experience', [])],
            education=data.get('education', []),
            projects=data.get('projects', []),
            certifications=data.get('certifications', [])
        )

    def _dict_to_job_posting(self, data: dict):
        """Convert dictionary to JobPosting object."""
        return JobPosting(**data)

    def _dict_to_company_info(self, data: dict):
        """Convert dictionary to CompanyInfo object."""
        return CompanyInfo(**data) if data else None
