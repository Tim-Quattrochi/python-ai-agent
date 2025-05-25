"""Resume parser tool for extracting structured data from PDF resumes."""

import re
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional
import pdfplumber
import PyPDF2
from dataclasses import dataclass, asdict

from ..base import Tool

logger = logging.getLogger(__name__)


@dataclass
class ContactInfo:
    """Contact information structure."""
    name: str = ""
    email: str = ""
    phone: str = ""
    location: str = ""
    linkedin: str = ""
    github: str = ""
    website: str = ""


@dataclass
class Experience:
    """Work experience structure."""
    title: str = ""
    company: str = ""
    duration: str = ""
    description: str = ""
    technologies: List[str] = None

    def __post_init__(self):
        if self.technologies is None:
            self.technologies = []


@dataclass
class Education:
    """Education structure."""
    degree: str = ""
    institution: str = ""
    graduation_year: str = ""
    gpa: str = ""


@dataclass
class Project:
    """Project structure."""
    name: str = ""
    description: str = ""
    technologies: List[str] = None
    url: str = ""

    def __post_init__(self):
        if self.technologies is None:
            self.technologies = []


@dataclass
class ResumeData:
    """Complete resume data structure."""
    contact_info: ContactInfo = None
    summary: str = ""
    skills: List[str] = None
    experience: List[Experience] = None
    education: List[Education] = None
    projects: List[Project] = None
    certifications: List[str] = None
    raw_text: str = ""

    def __post_init__(self):
        if self.contact_info is None:
            self.contact_info = ContactInfo()
        if self.skills is None:
            self.skills = []
        if self.experience is None:
            self.experience = []
        if self.education is None:
            self.education = []
        if self.projects is None:
            self.projects = []
        if self.certifications is None:
            self.certifications = []


class ResumeParserTool(Tool):
    """A tool for parsing PDF resumes and extracting structured data."""

    def __init__(self):
        super().__init__(
            name="resume_parser",
            description="Parse PDF resumes to extract structured data including contact info, skills, experience, education, and projects."
        )

    def execute(self, operation: str, **kwargs) -> str:
        """Execute a resume parsing operation."""
        try:
            if operation == "parse":
                return self._parse_resume(kwargs.get('file_path'))
            elif operation == "extract_skills":
                return self._extract_skills_only(kwargs.get('file_path'))
            elif operation == "extract_contact":
                return self._extract_contact_only(kwargs.get('file_path'))
            else:
                return f"Error: Unknown operation '{operation}'. Available: parse, extract_skills, extract_contact"
        except Exception as e:
            logger.error(f"Resume parser error: {e}")
            return f"Error executing {operation}: {str(e)}"

    def _parse_resume(self, file_path: str) -> str:
        """Parse a complete resume and return structured data."""
        if not file_path:
            return "❌ Error: file_path is required"

        try:
            # Extract text from PDF
            text = self._extract_text_from_pdf(file_path)
            if not text:
                return "❌ Error: Could not extract text from PDF"

            # Parse structured data
            resume_data = self._parse_text_to_structure(text)

            # Return formatted summary
            return self._format_resume_summary(resume_data)

        except Exception as e:
            logger.error(f"Error parsing resume: {e}")
            return f"❌ Error parsing resume: {str(e)}"

    def _extract_text_from_pdf(self, file_path: str) -> str:
        """Extract text from PDF using multiple methods for reliability."""
        file_path_obj = Path(file_path)

        if not file_path_obj.exists():
            raise FileNotFoundError(f"Resume file not found: {file_path}")

        if not file_path_obj.suffix.lower() == '.pdf':
            raise ValueError("Only PDF files are supported")

        text = ""

        # Try pdfplumber first (better for complex layouts)
        try:
            with pdfplumber.open(file_path) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"

            if text.strip():
                logger.info("Successfully extracted text using pdfplumber")
                return text

        except Exception as e:
            logger.warning(f"pdfplumber failed: {e}")

        # Fallback to PyPDF2
        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"

            if text.strip():
                logger.info("Successfully extracted text using PyPDF2")
                return text

        except Exception as e:
            logger.warning(f"PyPDF2 failed: {e}")

        raise Exception("Could not extract text from PDF using any method")

    def _parse_text_to_structure(self, text: str) -> ResumeData:
        """Parse raw text into structured resume data."""
        resume_data = ResumeData()
        resume_data.raw_text = text

        # Extract contact information
        resume_data.contact_info = self._extract_contact_info(text)

        # Extract skills
        resume_data.skills = self._extract_skills(text)

        # Extract experience
        resume_data.experience = self._extract_experience(text)

        # Extract education
        resume_data.education = self._extract_education(text)

        # Extract projects
        resume_data.projects = self._extract_projects(text)

        # Extract summary
        resume_data.summary = self._extract_summary(text)

        # Extract certifications
        resume_data.certifications = self._extract_certifications(text)

        return resume_data

    def _extract_contact_info(self, text: str) -> ContactInfo:
        """Extract contact information from resume text."""
        contact = ContactInfo()

        # Email pattern
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        emails = re.findall(email_pattern, text)
        if emails:
            contact.email = emails[0]

        # Phone pattern (various formats: (555) 123-4567, 555-123-4567, 555.123.4567, +1-555-123-4567)
        phone_pattern = r'(?:\+?1[-.\s]?)?\(?[0-9]{3}\)?[-.\s]?[0-9]{3}[-.\s]?[0-9]{4}'
        phones = re.findall(phone_pattern, text)
        if phones:
            contact.phone = phones[0]

        # LinkedIn pattern
        linkedin_pattern = r'(?:linkedin\.com/in/|linkedin\.com/pub/)([A-Za-z0-9\-_]+)'
        linkedin_matches = re.findall(linkedin_pattern, text, re.IGNORECASE)
        if linkedin_matches:
            contact.linkedin = f"linkedin.com/in/{linkedin_matches[0]}"

        # GitHub pattern
        github_pattern = r'(?:github\.com/)([A-Za-z0-9\-_]+)'
        github_matches = re.findall(github_pattern, text, re.IGNORECASE)
        if github_matches:
            contact.github = f"github.com/{github_matches[0]}"

        # Name extraction (first few lines, exclude email/phone)
        lines = text.split('\n')[:5]
        for line in lines:
            line = line.strip()
            if line and len(line.split()) <= 4 and len(line) < 50:
                if not re.search(email_pattern, line) and not re.search(phone_pattern, line):
                    if line and not contact.name:
                        contact.name = line
                        break

        return contact

    def _extract_skills(self, text: str) -> List[str]:
        """Extract technical skills from resume text."""
        # Common technical skills and tools
        tech_skills = [
            # Programming Languages
            'python', 'javascript', 'java', 'c++', 'c#', 'go', 'rust', 'php', 'ruby',
            'typescript', 'kotlin', 'swift', 'scala', 'r', 'matlab', 'sql', 'html',
            'css', 'bash', 'powershell',

            # Frameworks & Libraries
            'react', 'angular', 'vue', 'nodejs', 'express', 'django', 'flask',
            'spring', 'laravel', 'rails', 'asp.net', 'bootstrap', 'jquery',
            'nextjs', 'nuxt', 'gatsby', 'svelte',

            # Databases
            'mysql', 'postgresql', 'mongodb', 'redis', 'elasticsearch',
            'oracle', 'sqlite', 'cassandra', 'dynamodb',

            # Cloud & DevOps
            'aws', 'azure', 'gcp', 'docker', 'kubernetes', 'jenkins', 'terraform',
            'ansible', 'chef', 'puppet', 'gitlab', 'github', 'bitbucket',

            # Data & ML
            'pandas', 'numpy', 'scikit-learn', 'tensorflow', 'pytorch', 'keras',
            'spark', 'hadoop', 'tableau', 'powerbi', 'jupyter',

            # Other Tools
            'git', 'jira', 'confluence', 'slack', 'trello', 'figma', 'sketch'
        ]

        found_skills = []
        text_lower = text.lower()

        # Skill name mappings for proper capitalization
        skill_mappings = {
            'javascript': 'JavaScript',
            'typescript': 'TypeScript',
            'nodejs': 'Node.js',
            'nextjs': 'Next.js',
            'reactjs': 'React.js',
            'angularjs': 'Angular.js',
            'vuejs': 'Vue.js',
            'asp.net': 'ASP.NET',
            'c++': 'C++',
            'c#': 'C#',
            'mysql': 'MySQL',
            'postgresql': 'PostgreSQL',
            'mongodb': 'MongoDB',
            'redis': 'Redis',
            'elasticsearch': 'Elasticsearch',
            'dynamodb': 'DynamoDB',
            'aws': 'AWS',
            'gcp': 'GCP',
            'powerbi': 'Power BI',
            'github': 'GitHub',
            'gitlab': 'GitLab',
            'bitbucket': 'Bitbucket',
            'tensorflow': 'TensorFlow',
            'pytorch': 'PyTorch'
        }

        for skill in tech_skills:
            # Use word boundaries to avoid partial matches
            pattern = r'\b' + re.escape(skill.lower()) + r'\b'
            if re.search(pattern, text_lower):
                # Use proper mapping if available, otherwise title case
                proper_name = skill_mappings.get(skill.lower(), skill.title())
                found_skills.append(proper_name)

        # Remove duplicates and sort
        return sorted(list(set(found_skills)))

    def _extract_experience(self, text: str) -> List[Experience]:
        """Extract work experience from resume text."""
        # This is a simplified implementation
        # In practice, you'd want more sophisticated parsing
        experiences = []

        # Look for common experience section headers
        exp_sections = re.split(
            r'(?i)(experience|work history|employment|professional experience)', text)

        if len(exp_sections) > 1:
            # Take the last section after "experience"
            exp_text = exp_sections[-1]

            # Split by lines and look for patterns
            lines = exp_text.split('\n')
            current_exp = None

            for line in lines:
                line = line.strip()
                if not line:
                    continue

                # Look for job titles (usually start with uppercase and contain common titles)
                title_keywords = ['engineer', 'developer', 'analyst', 'manager', 'consultant',
                                  'specialist', 'coordinator', 'lead', 'senior', 'junior']

                if any(keyword in line.lower() for keyword in title_keywords):
                    if current_exp:
                        experiences.append(current_exp)

                    current_exp = Experience()
                    current_exp.title = line

                elif current_exp and ('•' in line or '-' in line):
                    # This looks like a description bullet point
                    current_exp.description += line + ' '

            if current_exp:
                experiences.append(current_exp)

        return experiences

    def _extract_education(self, text: str) -> List[Education]:
        """Extract education information from resume text."""
        education_list = []

        # Look for education section
        edu_sections = re.split(
            r'(?i)(education|academic|university|college)', text)

        if len(edu_sections) > 1:
            edu_text = edu_sections[-1]

            # Look for degree patterns
            degree_patterns = [
                r'(bachelor|master|phd|b\.?s\.?|m\.?s\.?|b\.?a\.?|m\.?a\.?|ph\.?d\.?).*?(?:in|of)\s+([^\n]+)',
                r'([^\n]*(?:bachelor|master|phd|degree)[^\n]*)'
            ]

            for pattern in degree_patterns:
                matches = re.findall(pattern, edu_text, re.IGNORECASE)
                for match in matches:
                    edu = Education()
                    if isinstance(match, tuple):
                        edu.degree = ' '.join(match).strip()
                    else:
                        edu.degree = match.strip()
                    education_list.append(edu)

        return education_list

    def _extract_projects(self, text: str) -> List[Project]:
        """Extract project information from resume text."""
        projects = []

        # Look for projects section
        project_sections = re.split(
            r'(?i)(projects|personal projects|side projects)', text)

        if len(project_sections) > 1:
            project_text = project_sections[-1]
            lines = project_text.split('\\n')

            current_project = None
            for line in lines:
                line = line.strip()
                if not line:
                    continue

                # Project names are often in title case or start with bullets
                if (line[0].isupper() or line.startswith('•') or line.startswith('-')) and len(line) < 100:
                    if current_project:
                        projects.append(current_project)

                    current_project = Project()
                    current_project.name = line.lstrip('•-').strip()

                elif current_project:
                    current_project.description += line + ' '

            if current_project:
                projects.append(current_project)

        return projects

    def _extract_summary(self, text: str) -> str:
        """Extract professional summary from resume text."""
        # Look for summary section
        summary_sections = re.split(
            r'(?i)(summary|objective|profile|about)', text)

        if len(summary_sections) > 1:
            summary_text = summary_sections[1]
            lines = summary_text.split('\\n')[:5]  # Take first few lines
            summary = ' '.join(line.strip() for line in lines if line.strip())

            # Limit length
            if len(summary) > 500:
                summary = summary[:500] + '...'

            return summary

        return ""

    def _extract_certifications(self, text: str) -> List[str]:
        """Extract certifications from resume text."""
        certifications = []

        # Look for certifications section
        cert_sections = re.split(
            r'(?i)(certifications?|certificates?|licenses?)', text)

        if len(cert_sections) > 1:
            cert_text = cert_sections[-1]
            lines = cert_text.split('\\n')[:10]  # Limit lines

            for line in lines:
                line = line.strip()
                if line and len(line) < 200:
                    certifications.append(line)

        return certifications

    def _format_resume_summary(self, resume_data: ResumeData) -> str:
        """Format resume data into a readable summary."""
        summary = "📄 Resume Parsing Results\\n"
        summary += "=" * 40 + "\\n\\n"

        # Contact Info
        contact = resume_data.contact_info
        if contact.name or contact.email:
            summary += "👤 Contact Information:\\n"
            if contact.name:
                summary += f"   Name: {contact.name}\\n"
            if contact.email:
                summary += f"   Email: {contact.email}\\n"
            if contact.phone:
                summary += f"   Phone: {contact.phone}\\n"
            if contact.linkedin:
                summary += f"   LinkedIn: {contact.linkedin}\\n"
            if contact.github:
                summary += f"   GitHub: {contact.github}\\n"
            summary += "\\n"

        # Skills
        if resume_data.skills:
            summary += f"🛠️ Technical Skills ({len(resume_data.skills)}):\\n"
            skills_text = ", ".join(resume_data.skills[:20])  # Limit display
            if len(resume_data.skills) > 20:
                skills_text += f" ... and {len(resume_data.skills) - 20} more"
            summary += f"   {skills_text}\\n\\n"

        # Experience
        if resume_data.experience:
            summary += f"💼 Work Experience ({len(resume_data.experience)} entries):\\n"
            # Show first 3
            for i, exp in enumerate(resume_data.experience[:3], 1):
                summary += f"   {i}. {exp.title or 'Position'}\\n"
                if exp.company:
                    summary += f"      Company: {exp.company}\\n"
                if exp.description:
                    desc = exp.description[:100] + "..." if len(
                        exp.description) > 100 else exp.description
                    summary += f"      Description: {desc}\\n"
            if len(resume_data.experience) > 3:
                summary += f"   ... and {len(resume_data.experience) - 3} more positions\\n"
            summary += "\\n"

        # Education
        if resume_data.education:
            summary += f"🎓 Education ({len(resume_data.education)} entries):\\n"
            for edu in resume_data.education:
                summary += f"   • {edu.degree}\\n"
            summary += "\\n"

        # Projects
        if resume_data.projects:
            summary += f"🚀 Projects ({len(resume_data.projects)} entries):\\n"
            for project in resume_data.projects[:3]:  # Show first 3
                summary += f"   • {project.name}\\n"
            summary += "\\n"

        summary += f"📊 Total text length: {len(resume_data.raw_text)} characters\\n"
        summary += "✅ Resume parsing completed successfully!"

        return summary

    def _extract_skills_only(self, file_path: str) -> str:
        """Extract only skills from a resume."""
        try:
            text = self._extract_text_from_pdf(file_path)
            skills = self._extract_skills(text)

            if skills:
                return f"🛠️ Extracted Skills ({len(skills)}):\\n" + "\\n".join(f"• {skill}" for skill in skills)
            else:
                return "No technical skills detected in the resume."

        except Exception as e:
            return f"❌ Error extracting skills: {str(e)}"

    def _extract_contact_only(self, file_path: str) -> str:
        """Extract only contact information from a resume."""
        try:
            text = self._extract_text_from_pdf(file_path)
            contact = self._extract_contact_info(text)

            result = "👤 Contact Information:\\n"
            result += f"Name: {contact.name or 'Not found'}\\n"
            result += f"Email: {contact.email or 'Not found'}\\n"
            result += f"Phone: {contact.phone or 'Not found'}\\n"
            result += f"LinkedIn: {contact.linkedin or 'Not found'}\\n"
            result += f"GitHub: {contact.github or 'Not found'}\\n"

            return result

        except Exception as e:
            return f"❌ Error extracting contact info: {str(e)}"

    def get_schema(self) -> Dict[str, Any]:
        """Get the JSON schema for this tool's parameters."""
        return {
            "type": "object",
            "properties": {
                "operation": {
                    "type": "string",
                    "enum": ["parse", "extract_skills", "extract_contact"],
                    "description": "Operation: parse (full resume analysis), extract_skills (skills only), extract_contact (contact info only)"
                },
                "file_path": {
                    "type": "string",
                    "description": "Path to the PDF resume file to parse"
                }
            },
            "required": ["operation", "file_path"]
        }
