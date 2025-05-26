"""LinkedIn job scraper tool for extracting job postings and requirements."""

import re
import time
import logging
import os
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, asdict
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from bs4 import BeautifulSoup
import requests

from ..base import Tool

logger = logging.getLogger(__name__)


@dataclass
class JobPosting:
    """Job posting data structure."""
    title: str = ""
    company: str = ""
    location: str = ""
    job_type: str = ""  # Full-time, Part-time, Contract, etc.
    experience_level: str = ""  # Entry, Mid, Senior, etc.
    description: str = ""
    requirements: List[str] = None
    skills_required: List[str] = None
    salary_range: str = ""
    posted_date: str = ""
    job_url: str = ""
    company_size: str = ""
    industry: str = ""

    def __post_init__(self):
        if self.requirements is None:
            self.requirements = []
        if self.skills_required is None:
            self.skills_required = []


@dataclass
class JobSearchFilters:
    """Job search filter criteria."""
    keywords: str = ""
    location: str = ""
    job_type: str = ""  # fulltime, parttime, contract, temporary, internship
    experience_level: str = ""  # internship, entry_level, associate, mid_senior, director
    remote: bool = False
    date_posted: str = ""  # past_24_hours, past_week, past_month
    salary_min: int = 0
    company_size: str = ""  # startup, small, medium, large


class JobScraperTool(Tool):
    """A tool for scraping job postings from LinkedIn and other job sites."""

    def __init__(self, use_scrapingant: bool = True, scrapingant_api_key: str = None):
        super().__init__(
            name="job_scraper",
            description="Scrape job postings from LinkedIn and other job sites with filtering options."
        )
        self.use_scrapingant = use_scrapingant
        self.scrapingant_api_key = scrapingant_api_key or os.getenv(
            'SCRAPINGANT_API_KEY')
        self.driver = None
        self.wait_time = 10

        # Initialize ScrapingAnt scraper if requested
        if self.use_scrapingant:
            try:
                from .scrapingant_scraper import ScrapingAntJobScraper
                self.scrapingant_scraper = ScrapingAntJobScraper(
                    api_key=self.scrapingant_api_key)
                logger.info("ScrapingAnt scraper initialized")
            except ImportError:
                logger.warning(
                    "ScrapingAnt not available, falling back to Selenium")
                self.use_scrapingant = False
                self.scrapingant_scraper = ScrapingAntJobScraper(
                    api_key=scrapingant_api_key)
                logger.info("ScrapingAnt scraper initialized")
            except ImportError:
                logger.warning(
                    "ScrapingAnt not available, falling back to Selenium")
                self.use_scrapingant = False

    def execute(self, operation: str, **kwargs) -> str:
        """Execute a job scraping operation."""
        try:
            # Use ScrapingAnt if available and enabled
            if self.use_scrapingant and hasattr(self, 'scrapingant_scraper'):
                logger.info("Using ScrapingAnt for job scraping")
                return self.scrapingant_scraper.execute(operation, **kwargs)

            # Fall back to Selenium scraping
            logger.info("Using Selenium for job scraping")
            if operation == "search_jobs":
                return self._search_jobs(
                    keywords=kwargs.get('keywords', ''),
                    location=kwargs.get('location', ''),
                    limit=kwargs.get('limit', 10),
                    filters=kwargs.get('filters')
                )
            elif operation == "get_job_details":
                return self._get_job_details(kwargs.get('job_url'))
            elif operation == "search_linkedin":
                return self._search_linkedin_jobs(
                    keywords=kwargs.get('keywords', ''),
                    location=kwargs.get('location', ''),
                    limit=kwargs.get('limit', 10)
                )
            else:
                return f"Error: Unknown operation '{operation}'. Available: search_jobs, get_job_details, search_linkedin"
        except Exception as e:
            logger.error(f"Job scraper error: {e}")
            return f"Error executing {operation}: {str(e)}"
        finally:
            if not self.use_scrapingant:
                self._cleanup_driver()

    def _setup_driver(self, headless: bool = True) -> None:
        """Setup Chrome WebDriver with appropriate options."""
        if self.driver:
            return

        chrome_options = Options()
        if headless:
            chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument(
            "--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")

        try:
            self.driver = webdriver.Chrome(options=chrome_options)
            logger.info("Chrome WebDriver initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Chrome WebDriver: {e}")
            raise

    def _cleanup_driver(self) -> None:
        """Clean up WebDriver resources."""
        if self.driver:
            try:
                self.driver.quit()
                self.driver = None
                logger.info("WebDriver cleaned up successfully")
            except Exception as e:
                logger.warning(f"Error cleaning up WebDriver: {e}")

    def _search_linkedin_jobs(self, keywords: str, location: str = "", limit: int = 10) -> str:
        """Search for jobs on LinkedIn."""
        if not keywords:
            return "❌ Error: keywords parameter is required"

        try:
            self._setup_driver()

            # Build LinkedIn search URL
            base_url = "https://www.linkedin.com/jobs/search"
            params = {
                'keywords': keywords,
                'location': location,
                'f_TPR': 'r604800',  # Past week
                'f_JT': 'F',  # Full-time
                'position': 1,
                'pageNum': 0
            }

            # Construct URL
            url_params = "&".join([f"{k}={v}" for k, v in params.items() if v])
            search_url = f"{base_url}?{url_params}"

            logger.info(f"Searching LinkedIn jobs: {search_url}")

            # Navigate to LinkedIn jobs
            self.driver.get(search_url)
            time.sleep(3)

            # Wait for job listings to load
            try:
                WebDriverWait(self.driver, self.wait_time).until(
                    EC.presence_of_element_located(
                        (By.CLASS_NAME, "jobs-search__results-list"))
                )
            except TimeoutException:
                # Try alternative selector
                WebDriverWait(self.driver, self.wait_time).until(
                    EC.presence_of_element_located(
                        (By.CSS_SELECTOR, "[data-testid='jobs-search-results-list']"))
                )

            # Extract job listings
            jobs = self._extract_linkedin_job_listings(limit)

            if not jobs:
                return f"⚠️ No jobs found for keywords: '{keywords}' in location: '{location}'"

            return self._format_job_results(jobs, f"LinkedIn Jobs: {keywords}")

        except Exception as e:
            logger.error(f"LinkedIn job search failed: {e}")
            return f"❌ Error searching LinkedIn jobs: {str(e)}"

    def _extract_linkedin_job_listings(self, limit: int) -> List[JobPosting]:
        """Extract job listings from LinkedIn search results."""
        jobs = []

        try:
            # Get job cards using multiple selectors
            job_selectors = [
                ".jobs-search__results-list li",
                "[data-testid='job-card']",
                ".job-card-container",
                ".jobs-search-results__list-item"
            ]

            job_cards = []
            for selector in job_selectors:
                try:
                    job_cards = self.driver.find_elements(
                        By.CSS_SELECTOR, selector)
                    if job_cards:
                        logger.info(
                            f"Found {len(job_cards)} job cards using selector: {selector}")
                        break
                except NoSuchElementException:
                    continue

            if not job_cards:
                logger.warning("No job cards found with any selector")
                return jobs

            # Process each job card
            for i, card in enumerate(job_cards[:limit]):
                try:
                    job = self._parse_linkedin_job_card(card)
                    if job and job.title:  # Only add jobs with valid data
                        jobs.append(job)
                        logger.info(
                            f"Extracted job {i+1}: {job.title} at {job.company}")
                except Exception as e:
                    logger.warning(f"Error parsing job card {i+1}: {e}")
                    continue

        except Exception as e:
            logger.error(f"Error extracting job listings: {e}")

        return jobs

    def _parse_linkedin_job_card(self, card) -> Optional[JobPosting]:
        """Parse a single LinkedIn job card element."""
        job = JobPosting()

        try:
            # Job title
            title_selectors = [
                ".job-card-list__title",
                "[data-testid='job-title']",
                ".jobs-unified-top-card__job-title",
                "h3 a",
                ".job-card-container__link"
            ]

            for selector in title_selectors:
                try:
                    title_element = card.find_element(
                        By.CSS_SELECTOR, selector)
                    job.title = title_element.text.strip()

                    # Get job URL if available
                    if title_element.tag_name == 'a':
                        job.job_url = title_element.get_attribute('href')
                    break
                except NoSuchElementException:
                    continue

            # Company name
            company_selectors = [
                ".job-card-container__company-name",
                "[data-testid='job-company']",
                ".jobs-unified-top-card__company-name",
                ".job-card-list__company-name"
            ]

            for selector in company_selectors:
                try:
                    company_element = card.find_element(
                        By.CSS_SELECTOR, selector)
                    job.company = company_element.text.strip()
                    break
                except NoSuchElementException:
                    continue

            # Location
            location_selectors = [
                ".job-card-container__metadata-item",
                "[data-testid='job-location']",
                ".jobs-unified-top-card__bullet",
                ".job-card-list__metadata"
            ]

            for selector in location_selectors:
                try:
                    location_element = card.find_element(
                        By.CSS_SELECTOR, selector)
                    job.location = location_element.text.strip()
                    break
                except NoSuchElementException:
                    continue

            # Posted date
            try:
                posted_element = card.find_element(By.CSS_SELECTOR, "time")
                job.posted_date = posted_element.get_attribute(
                    'datetime') or posted_element.text.strip()
            except NoSuchElementException:
                pass

            return job if job.title else None

        except Exception as e:
            logger.warning(f"Error parsing job card: {e}")
            return None

    def _search_jobs(self, keywords: str, location: str = "", limit: int = 10, filters: Dict = None) -> str:
        """General job search across multiple platforms."""
        if not keywords:
            return "❌ Error: keywords parameter is required"

        results = []

        # Search LinkedIn
        try:
            linkedin_result = self._search_linkedin_jobs(
                keywords, location, limit)
            if "Error" not in linkedin_result:
                results.append("📍 LinkedIn Results:")
                results.append(linkedin_result)
        except Exception as e:
            logger.warning(f"LinkedIn search failed: {e}")

        # Could add other job sites here (Indeed, Glassdoor, etc.)

        if not results:
            return f"❌ No jobs found for keywords: '{keywords}'"

        return "\n\n".join(results)

    def _get_job_details(self, job_url: str) -> str:
        """Get detailed information for a specific job posting."""
        if not job_url:
            return "❌ Error: job_url parameter is required"

        try:
            self._setup_driver()

            # Navigate to job posting
            self.driver.get(job_url)
            time.sleep(3)

            # Wait for job details to load
            WebDriverWait(self.driver, self.wait_time).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )

            # Extract detailed job information
            job_details = self._extract_job_details()

            return self._format_job_details(job_details)

        except Exception as e:
            logger.error(f"Error getting job details: {e}")
            return f"❌ Error fetching job details: {str(e)}"

    def _extract_job_details(self) -> JobPosting:
        """Extract detailed job information from a job posting page."""
        job = JobPosting()

        try:
            # Get page source and parse with BeautifulSoup for better text extraction
            soup = BeautifulSoup(self.driver.page_source, 'html.parser')

            # Extract job title
            title_selectors = [
                'h1', '.jobs-unified-top-card__job-title', '.job-title']
            for selector in title_selectors:
                title_element = soup.select_one(selector)
                if title_element:
                    job.title = title_element.get_text(strip=True)
                    break

            # Extract company
            company_selectors = [
                '.jobs-unified-top-card__company-name', '.job-company', '.company-name']
            for selector in company_selectors:
                company_element = soup.select_one(selector)
                if company_element:
                    job.company = company_element.get_text(strip=True)
                    break

            # Extract job description
            desc_selectors = ['.jobs-description-content__text',
                              '.job-description', '.description']
            for selector in desc_selectors:
                desc_element = soup.select_one(selector)
                if desc_element:
                    job.description = desc_element.get_text(strip=True)
                    break

            # Extract skills and requirements from description
            if job.description:
                job.skills_required = self._extract_skills_from_description(
                    job.description)
                job.requirements = self._extract_requirements_from_description(
                    job.description)

        except Exception as e:
            logger.warning(f"Error extracting job details: {e}")

        return job

    def _extract_skills_from_description(self, description: str) -> List[str]:
        """Extract technical skills from job description."""
        # Use similar skill list as resume parser
        tech_skills = [
            'python', 'javascript', 'java', 'c++', 'c#', 'go', 'rust', 'php', 'ruby',
            'typescript', 'kotlin', 'swift', 'scala', 'r', 'sql', 'html', 'css',
            'react', 'angular', 'vue', 'nodejs', 'django', 'flask', 'spring',
            'mysql', 'postgresql', 'mongodb', 'redis', 'aws', 'azure', 'docker',
            'kubernetes', 'git', 'jenkins', 'terraform'
        ]

        found_skills = []
        desc_lower = description.lower()

        # Skill name mappings for proper capitalization
        skill_mappings = {
            'javascript': 'JavaScript',
            'typescript': 'TypeScript',
            'nodejs': 'Node.js',
            'c++': 'C++',
            'c#': 'C#',
            'mysql': 'MySQL',
            'postgresql': 'PostgreSQL',
            'mongodb': 'MongoDB',
            'redis': 'Redis',
            'aws': 'AWS',
            'azure': 'Azure',
            'git': 'Git',
            'jenkins': 'Jenkins',
            'terraform': 'Terraform'
        }

        for skill in tech_skills:
            pattern = r'\b' + re.escape(skill.lower()) + r'\b'
            if re.search(pattern, desc_lower):
                # Use proper mapping if available, otherwise title case
                proper_name = skill_mappings.get(skill.lower(), skill.title())
                found_skills.append(proper_name)

        return sorted(list(set(found_skills)))

    def _extract_requirements_from_description(self, description: str) -> List[str]:
        """Extract job requirements from description."""
        requirements = []

        # Look for common requirement patterns
        req_patterns = [
            r'(?:requirements?|qualifications?|must have)[:\s]*(.+?)(?:\n\n|\n(?=[A-Z])|$)',
            r'(?:required skills?|needed)[:\s]*(.+?)(?:\n\n|\n(?=[A-Z])|$)',
            r'(?:experience with|proficiency in)[:\s]*(.+?)(?:\n\n|\n(?=[A-Z])|$)'
        ]

        for pattern in req_patterns:
            matches = re.findall(pattern, description,
                                 re.IGNORECASE | re.DOTALL)
            for match in matches:
                # Split by bullet points or line breaks
                items = re.split(r'[•\-\*]\s*|[\n\r]+', match.strip())
                for item in items:
                    item = item.strip()
                    # Filter reasonable length requirements
                    if len(item) > 10 and len(item) < 200:
                        requirements.append(item)

        return requirements[:10]  # Limit to top 10 requirements

    def _format_job_results(self, jobs: List[JobPosting], title: str) -> str:
        """Format job search results for display."""
        if not jobs:
            return f"❌ No jobs found"

        result = [f"🔍 {title}"]
        result.append("=" * 50)
        result.append(f"Found {len(jobs)} job(s):")
        result.append("")

        for i, job in enumerate(jobs, 1):
            result.append(f"📋 Job #{i}:")
            result.append(f"   Title: {job.title}")
            result.append(f"   Company: {job.company}")
            result.append(f"   Location: {job.location}")
            if job.posted_date:
                result.append(f"   Posted: {job.posted_date}")
            if job.job_url:
                result.append(f"   URL: {job.job_url}")
            result.append("")

        result.append("✅ Job search completed successfully!")
        return "\n".join(result)

    def _format_job_details(self, job: JobPosting) -> str:
        """Format detailed job information for display."""
        result = ["📄 Job Details"]
        result.append("=" * 40)
        result.append("")

        if job.title:
            result.append(f"📌 Title: {job.title}")
        if job.company:
            result.append(f"🏢 Company: {job.company}")
        if job.location:
            result.append(f"📍 Location: {job.location}")

        if job.skills_required:
            result.append(
                f"\n🛠️ Required Skills ({len(job.skills_required)}):")
            for skill in job.skills_required:
                result.append(f"   • {skill}")

        if job.requirements:
            result.append(f"\n📋 Requirements ({len(job.requirements)}):")
            for req in job.requirements:
                result.append(f"   • {req}")

        if job.description:
            result.append(f"\n📝 Description:")
            # Truncate long descriptions
            desc = job.description[:500] + \
                "..." if len(job.description) > 500 else job.description
            result.append(f"   {desc}")

        result.append("\n✅ Job details extraction completed!")
        return "\n".join(result)

    def get_schema(self) -> Dict[str, Any]:
        """Get the JSON schema for job scraper parameters."""
        return {
            "type": "object",
            "properties": {
                "operation": {
                    "type": "string",
                    "enum": ["search_jobs", "get_job_details", "search_linkedin"],
                    "description": "The operation to perform"
                },
                "keywords": {
                    "type": "string",
                    "description": "Job search keywords (e.g., 'python developer', 'data scientist')"
                },
                "location": {
                    "type": "string",
                    "description": "Job location (e.g., 'San Francisco', 'Remote', 'New York')"
                },
                "limit": {
                    "type": "integer",
                    "description": "Maximum number of jobs to return (default: 10)",
                    "minimum": 1,
                    "maximum": 50,
                    "default": 10
                },
                "job_url": {
                    "type": "string",
                    "description": "URL of specific job posting for detailed extraction"
                },
                "filters": {
                    "type": "object",
                    "description": "Additional search filters",
                    "properties": {
                        "job_type": {
                            "type": "string",
                            "enum": ["fulltime", "parttime", "contract", "temporary", "internship"],
                            "description": "Type of employment"
                        },
                        "experience_level": {
                            "type": "string",
                            "enum": ["internship", "entry_level", "associate", "mid_senior", "director"],
                            "description": "Required experience level"
                        },
                        "remote": {
                            "type": "boolean",
                            "description": "Filter for remote positions"
                        },
                        "date_posted": {
                            "type": "string",
                            "enum": ["past_24_hours", "past_week", "past_month"],
                            "description": "How recently the job was posted"
                        }
                    }
                }
            },
            "required": ["operation"],
            "additionalProperties": False
        }
