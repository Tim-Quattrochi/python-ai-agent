"""Job application orchestrator that coordinates all automation tools."""

import logging
import os
import json
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime
import time

from .resume_parser import ResumeParserTool, ResumeData
from .job_scraper import JobScraperTool, JobPosting, JobSearchFilters
from .job_matcher import JobMatcherTool, JobMatchResult
from .resume_customizer import ResumeCustomizerTool
from .company_research import CompanyResearchTool, CompanyInfo
from .cover_letter_generator import CoverLetterGeneratorTool
from ..email_sender import EmailSenderTool
from ..base import Tool

logger = logging.getLogger(__name__)


@dataclass
class ApplicationConfig:
    """Configuration for job application automation."""
    # Resume and applicant info
    resume_file_path: str = ""
    applicant_email: str = ""
    applicant_name: str = ""

    # Job search criteria
    keywords: str = ""
    location: str = ""
    job_type: str = "fulltime"  # fulltime, parttime, contract, etc.
    experience_level: str = ""  # entry, mid, senior, executive
    salary_min: str = ""

    # Application settings
    max_applications: int = 5
    min_match_score: float = 0.6
    auto_send_emails: bool = False
    delay_between_applications: int = 300  # seconds (5 minutes)

    # Email settings
    email_host: str = ""
    email_port: int = 587
    email_username: str = ""
    email_password: str = ""

    # Customization preferences
    template_style: str = "auto"  # professional, technical, creative, executive, auto
    cover_letter_tone: str = "professional"
    include_salary_expectations: bool = False
    include_availability: bool = True

    # Output settings
    save_applications: bool = True
    output_directory: str = "./job_applications"


@dataclass
class ApplicationResult:
    """Result of a single job application."""
    job_posting: JobPosting
    match_score: float
    company_info: Optional[CompanyInfo] = None
    customized_resume_path: str = ""
    cover_letter_path: str = ""
    email_sent: bool = False
    email_subject: str = ""
    application_timestamp: str = ""
    error_message: str = ""

    def __post_init__(self):
        if not self.application_timestamp:
            self.application_timestamp = datetime.now().isoformat()


@dataclass
class OrchestrationSummary:
    """Summary of the complete job application process."""
    total_jobs_found: int = 0
    jobs_above_threshold: int = 0
    applications_attempted: int = 0
    applications_successful: int = 0
    applications_failed: int = 0
    total_time_taken: float = 0.0
    results: List[ApplicationResult] = None
    errors: List[str] = None

    def __post_init__(self):
        if self.results is None:
            self.results = []
        if self.errors is None:
            self.errors = []


class JobApplicationOrchestrator(Tool):
    """Orchestrates the complete job application automation workflow."""

    def __init__(self):
        super().__init__(
            name="job_application_orchestrator",
            description="Automate the complete job application process from job search to email submission."
        )

        # Initialize all tools
        self.resume_parser = ResumeParserTool()
        self.job_scraper = JobScraperTool()
        self.job_matcher = JobMatcherTool()
        self.resume_customizer = ResumeCustomizerTool()
        self.company_researcher = CompanyResearchTool()
        self.cover_letter_generator = CoverLetterGeneratorTool()
        self.email_sender = EmailSenderTool()

    def get_schema(self) -> Dict[str, Any]:
        """Get the JSON schema for orchestrator parameters."""
        return {
            "type": "object",
            "properties": {
                "operation": {
                    "type": "string",
                    "enum": ["run_application_process", "preview_applications", "test_configuration"],
                    "description": "The operation to perform"
                },
                "config": {
                    "type": "object",
                    "description": "Application configuration settings",
                    "required": True
                },
                "dry_run": {
                    "type": "boolean",
                    "description": "If true, process applications but don't send emails",
                    "default": True
                }
            },
            "required": ["operation", "config"]
        }

    def execute(self, **kwargs) -> Dict[str, Any]:
        """Execute job application orchestration."""
        try:
            operation = kwargs.get('operation', 'run_application_process')

            if operation == "run_application_process":
                return self._run_application_process(**kwargs)
            elif operation == "preview_applications":
                return self._preview_applications(**kwargs)
            elif operation == "test_configuration":
                return self._test_configuration(**kwargs)
            else:
                return {
                    "success": False,
                    "error": f"Unknown operation: {operation}"
                }

        except Exception as e:
            logger.error(f"Orchestration error: {str(e)}")
            return {
                "success": False,
                "error": f"Job application orchestration failed: {str(e)}"
            }

    def _run_application_process(self, **kwargs) -> Dict[str, Any]:
        """Run the complete job application process."""
        start_time = time.time()

        # Parse configuration
        config_dict = kwargs.get('config', {})
        config = self._parse_config(config_dict)
        dry_run = kwargs.get('dry_run', True)

        summary = OrchestrationSummary()

        try:
            # Step 1: Parse resume
            logger.info("Step 1: Parsing resume...")
            resume_result = self._parse_resume(config)
            if not resume_result['success']:
                summary.errors.append(
                    f"Resume parsing failed: {resume_result['error']}")
                return self._format_failure_result(summary, "Resume parsing failed")

            resume_data = resume_result['resume_data']

            # Step 2: Search for jobs
            logger.info("Step 2: Searching for jobs...")
            jobs_result = self._search_jobs(config)
            if not jobs_result['success']:
                summary.errors.append(
                    f"Job search failed: {jobs_result['error']}")
                return self._format_failure_result(summary, "Job search failed")

            jobs = jobs_result['jobs']
            summary.total_jobs_found = len(jobs)

            # Step 3: Match and rank jobs
            logger.info("Step 3: Matching and ranking jobs...")
            matches_result = self._match_jobs(resume_data, jobs, config)
            if not matches_result['success']:
                summary.errors.append(
                    f"Job matching failed: {matches_result['error']}")
                return self._format_failure_result(summary, "Job matching failed")

            job_matches = matches_result['matches']

            # Filter by minimum match score
            qualified_matches = [
                match for match in job_matches
                if match.overall_score >= config.min_match_score
            ]
            summary.jobs_above_threshold = len(qualified_matches)

            # Limit to max applications
            selected_matches = qualified_matches[:config.max_applications]
            summary.applications_attempted = len(selected_matches)

            # Step 4: Process each selected job
            logger.info(
                f"Step 4: Processing {len(selected_matches)} job applications...")
            for i, match in enumerate(selected_matches):
                logger.info(
                    f"Processing application {i+1}/{len(selected_matches)}: {match.job.title} at {match.job.company}")

                try:
                    app_result = self._process_single_application(
                        resume_data, match, config, dry_run
                    )
                    summary.results.append(app_result)

                    if app_result.email_sent or dry_run:
                        summary.applications_successful += 1
                    else:
                        summary.applications_failed += 1

                except Exception as e:
                    logger.error(f"Application processing failed: {str(e)}")
                    summary.errors.append(
                        f"Application {i+1} failed: {str(e)}")
                    summary.applications_failed += 1

                # Add delay between applications
                if i < len(selected_matches) - 1 and not dry_run:
                    logger.info(
                        f"Waiting {config.delay_between_applications} seconds before next application...")
                    time.sleep(config.delay_between_applications)

            summary.total_time_taken = time.time() - start_time

            return {
                "success": True,
                "summary": asdict(summary),
                "message": self._format_success_message(summary, dry_run),
                "dry_run": dry_run
            }

        except Exception as e:
            summary.total_time_taken = time.time() - start_time
            summary.errors.append(str(e))
            logger.error(f"Application process failed: {str(e)}")
            return self._format_failure_result(summary, str(e))

    def _process_single_application(self, resume_data: ResumeData, match: JobMatchResult,
                                    config: ApplicationConfig, dry_run: bool) -> ApplicationResult:
        """Process a single job application."""
        job = match.job
        app_result = ApplicationResult(
            job_posting=job,
            match_score=match.overall_score
        )

        try:
            # Research company
            logger.info(f"Researching {job.company}...")
            company_info = self._research_company(job)
            app_result.company_info = company_info

            # Customize resume
            logger.info("Customizing resume...")
            customized_resume_path = self._customize_resume(
                resume_data, job, config)
            app_result.customized_resume_path = customized_resume_path

            # Generate cover letter
            logger.info("Generating cover letter...")
            cover_letter_result = self._generate_cover_letter(
                resume_data, job, company_info, config
            )
            app_result.cover_letter_path = cover_letter_result['path']
            app_result.email_subject = cover_letter_result['subject']

            # Send email (if not dry run)
            if not dry_run and config.auto_send_emails:
                logger.info("Sending application email...")
                email_result = self._send_application_email(
                    job, cover_letter_result, customized_resume_path, config
                )
                app_result.email_sent = email_result['success']
                if not email_result['success']:
                    app_result.error_message = email_result['error']
            else:
                app_result.email_sent = False  # Dry run or manual sending

        except Exception as e:
            app_result.error_message = str(e)
            logger.error(f"Single application processing failed: {str(e)}")

        return app_result

    def _parse_resume(self, config: ApplicationConfig) -> Dict[str, Any]:
        """Parse the resume file."""
        try:
            # Extract text first
            text = self.resume_parser._extract_text_from_pdf(
                config.resume_file_path)

            # Parse into structured data
            resume_data = self.resume_parser._parse_text_to_structure(text)

            return {
                "success": True,
                "resume_data": resume_data,
                "raw_text": text[:500] + "..." if len(text) > 500 else text
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "resume_data": None
            }

    def _search_jobs(self, config: ApplicationConfig) -> Dict[str, Any]:
        """Search for jobs based on criteria."""
        filters = JobSearchFilters(
            keywords=config.keywords,
            location=config.location,
            job_type=config.job_type,
            experience_level=config.experience_level,
            salary_min=config.salary_min
        )

        return self.job_scraper.execute(
            operation="search_jobs",
            filters=asdict(filters),
            # Search more than needed for better selection
            max_results=config.max_applications * 3
        )

    def _match_jobs(self, resume_data: ResumeData, jobs: List[JobPosting],
                    config: ApplicationConfig) -> Dict[str, Any]:
        """Match resume to jobs and rank them."""
        return self.job_matcher.execute(
            operation="batch_match",
            resume_data=asdict(resume_data),
            job_postings=[asdict(job) for job in jobs],
            sort_by="overall_score"
        )

    def _research_company(self, job: JobPosting) -> Optional[CompanyInfo]:
        """Research company information."""
        try:
            result = self.company_researcher.execute(
                operation="research_company",
                company_name=job.company,
                job_posting=asdict(job)
            )

            if result['success']:
                return result['company_info']
            else:
                logger.warning(
                    f"Company research failed for {job.company}: {result['error']}")
                return None

        except Exception as e:
            logger.warning(
                f"Company research error for {job.company}: {str(e)}")
            return None

    def _customize_resume(self, resume_data: ResumeData, job: JobPosting,
                          config: ApplicationConfig) -> str:
        """Customize resume for the specific job."""
        try:
            result = self.resume_customizer.execute(
                operation="customize_resume",
                resume_data=asdict(resume_data),
                job_posting=asdict(job)
            )

            if result['success']:
                # Save customized resume to file
                output_dir = self._ensure_output_directory(config)
                filename = f"resume_{job.company}_{job.title}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
                file_path = os.path.join(
                    output_dir, filename.replace(" ", "_").replace("/", "_"))

                with open(file_path, 'w', encoding='utf-8') as f:
                    customized_resume = result['customized_resume']

                    # Format resume content
                    f.write(
                        f"# {customized_resume['contact_info']['name']}\n\n")
                    f.write(
                        f"Email: {customized_resume['contact_info']['email']}\n")
                    f.write(
                        f"Phone: {customized_resume['contact_info']['phone']}\n")
                    if customized_resume['contact_info']['location']:
                        f.write(
                            f"Location: {customized_resume['contact_info']['location']}\n")

                    f.write(
                        f"\n## Professional Summary\n{customized_resume['summary']}\n")

                    f.write(
                        f"\n## Skills\n{', '.join(customized_resume['skills'])}\n")

                    f.write(f"\n## Experience\n")
                    for exp in customized_resume['experience']:
                        f.write(
                            f"### {exp['title']} - {exp['company']} ({exp['duration']})\n")
                        f.write(f"{exp['description']}\n\n")

                    if customized_resume['education']:
                        f.write(f"## Education\n")
                        for edu in customized_resume['education']:
                            f.write(
                                f"### {edu['degree']} - {edu['institution']} ({edu['graduation_year']})\n")
                            if 'gpa' in edu and edu['gpa']:
                                f.write(f"GPA: {edu['gpa']}\n")
                            f.write("\n")

                return file_path
            else:
                logger.warning(
                    f"Resume customization failed: {result['error']}")
                return config.resume_file_path  # Fall back to original resume

        except Exception as e:
            logger.warning(f"Resume customization error: {str(e)}")
            return config.resume_file_path

    def _generate_cover_letter(self, resume_data: ResumeData, job: JobPosting,
                               company_info: Optional[CompanyInfo], config: ApplicationConfig) -> Dict[str, str]:
        """Generate cover letter for the job."""
        result = self.cover_letter_generator.execute(
            operation="generate_cover_letter",
            resume_data=asdict(resume_data),
            job_posting=asdict(job),
            company_info=asdict(company_info) if company_info else None,
            template_style=config.template_style,
            tone=config.cover_letter_tone,
            include_salary=config.include_salary_expectations,
            include_availability=config.include_availability
        )

        if result['success']:
            # Save cover letter to file
            output_dir = self._ensure_output_directory(config)
            filename = f"cover_letter_{job.company}_{job.title}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
            file_path = os.path.join(
                output_dir, filename.replace(" ", "_").replace("/", "_"))

            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(result['cover_letter'])

            return {
                'path': file_path,
                'content': result['cover_letter'],
                'subject': result['result']['content']['subject_line']
            }
        else:
            raise Exception(
                f"Cover letter generation failed: {result['error']}")

    def _send_application_email(self, job: JobPosting, cover_letter_result: Dict[str, str],
                                resume_path: str, config: ApplicationConfig) -> Dict[str, Any]:
        """Send the application email with attachments."""
        # Determine recipient email
        recipient_email = self._get_recipient_email(job)

        # Prepare attachments
        attachments = [
            {
                'file_path': resume_path,
                # Will need to convert to PDF
                'filename': f"{config.applicant_name}_Resume.pdf"
            },
            {
                'file_path': cover_letter_result['path'],
                'filename': f"{config.applicant_name}_CoverLetter.txt"
            }
        ]

        return self.email_sender.execute(
            to_email=recipient_email,
            subject=cover_letter_result['subject'],
            body=cover_letter_result['content'],
            attachments=attachments,
            host=config.email_host,
            port=config.email_port,
            username=config.email_username,
            password=config.email_password
        )

    def _get_recipient_email(self, job: JobPosting) -> str:
        """Get recipient email for the job application."""
        # This is a simplified approach - in real implementation,
        # you might want to research HR contacts or use company domain patterns
        if hasattr(job, 'contact_email') and job.contact_email:
            return job.contact_email

        # Generic fallback patterns
        company_domain = job.company.lower().replace(
            " ", "").replace("inc", "").replace("corp", "") + ".com"
        return f"hr@{company_domain}"

    def _ensure_output_directory(self, config: ApplicationConfig) -> str:
        """Ensure output directory exists."""
        os.makedirs(config.output_directory, exist_ok=True)
        return config.output_directory

    def _parse_config(self, config_dict: Dict[str, Any]) -> ApplicationConfig:
        """Parse configuration dictionary into ApplicationConfig object."""
        return ApplicationConfig(**config_dict)

    def _preview_applications(self, **kwargs) -> Dict[str, Any]:
        """Preview applications without sending them."""
        # Same as run_application_process but always with dry_run=True
        kwargs['dry_run'] = True
        return self._run_application_process(**kwargs)

    def _test_configuration(self, **kwargs) -> Dict[str, Any]:
        """Test the configuration without running full process."""
        config_dict = kwargs.get('config', {})
        config = self._parse_config(config_dict)

        tests = []

        # Test resume file access
        if config.resume_file_path and os.path.exists(config.resume_file_path):
            tests.append(("Resume file", True, "File exists and accessible"))
        else:
            tests.append(
                ("Resume file", False, f"File not found: {config.resume_file_path}"))

        # Test email configuration
        if config.email_host and config.email_username:
            tests.append(("Email config", True, "Email settings provided"))
        else:
            tests.append(
                ("Email config", False, "Missing email host or username"))

        # Test output directory
        try:
            os.makedirs(config.output_directory, exist_ok=True)
            tests.append(("Output directory", True,
                         f"Directory ready: {config.output_directory}"))
        except Exception as e:
            tests.append(("Output directory", False,
                         f"Cannot create directory: {str(e)}"))

        # Test job search criteria
        if config.keywords and config.location:
            tests.append(("Search criteria", True,
                         "Keywords and location provided"))
        else:
            tests.append(("Search criteria", False,
                         "Missing keywords or location"))

        all_passed = all(test[1] for test in tests)

        return {
            "success": all_passed,
            "tests": tests,
            "summary": f"Configuration test: {'PASSED' if all_passed else 'FAILED'}",
            "recommendation": "Configuration ready for job application automation" if all_passed else "Please fix failing tests before running automation"
        }

    def _format_success_message(self, summary: OrchestrationSummary, dry_run: bool) -> str:
        """Format success message."""
        mode = "DRY RUN" if dry_run else "LIVE RUN"

        return f"""
🎉 Job Application Automation Complete ({mode})
===============================================

📊 Summary:
   • Jobs found: {summary.total_jobs_found}
   • Jobs above threshold: {summary.jobs_above_threshold}
   • Applications processed: {summary.applications_attempted}
   • Successful: {summary.applications_successful}
   • Failed: {summary.applications_failed}
   • Time taken: {summary.total_time_taken:.1f} seconds

📧 Applications:
""" + "\n".join([
            f"   • {result.job_posting.title} at {result.job_posting.company} (Score: {result.match_score:.2f}) - {'✓' if result.email_sent or dry_run else '✗'}"
            for result in summary.results
        ]) + (f"\n\n⚠️  Errors: {len(summary.errors)}" if summary.errors else "\n\n✅ No errors encountered")

    def _format_failure_result(self, summary: OrchestrationSummary, error: str) -> Dict[str, Any]:
        """Format failure result."""
        return {
            "success": False,
            "error": error,
            "summary": asdict(summary),
            "message": f"Job application automation failed: {error}"
        }
