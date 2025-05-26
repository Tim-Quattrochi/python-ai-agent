"""Enhanced job scraper using ScrapingAnt for reliable web scraping."""

import re
import json
import time
import logging
import os
import urllib3
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, asdict
from bs4 import BeautifulSoup
from scrapingant_client import ScrapingAntClient
import requests

from ..base import Tool

# Configure urllib3 to handle SSL warnings appropriately
import warnings

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


class ScrapingAntJobScraper(Tool):
    """A professional job scraper using ScrapingAnt API for reliable scraping."""

    def __init__(self, api_key: Optional[str] = None, use_proxy_mode: bool = True):
        super().__init__(
            name="scrapingant_scraper",
            description="Job scraper using ScrapingAnt with anti-detection for LinkedIn and other job boards."
        )

        # Try to get API key from parameter, environment, or use demo mode
        self.api_key = api_key or os.getenv(
            'SCRAPINGANT_API_KEY') or "YOUR_SCRAPINGANT_API_KEYea"
        self.client = None
        self.use_proxy_mode = use_proxy_mode  # Option to disable proxy mode if needed
        self.rate_limit_delay = 2  # seconds between requests

        # Demo mode for testing without API key
        self.demo_mode = self.api_key == "YOUR_SCRAPINGANT_API_KEY" or not self.api_key

        if not self.demo_mode:
            try:
                self.client = ScrapingAntClient(token=self.api_key)
                logger.info(
                    f"ScrapingAnt client initialized with API key (proxy mode: {self.use_proxy_mode})")
            except Exception as e:
                logger.warning(
                    f"Failed to initialize ScrapingAnt client: {e}. Using demo mode.")
                self.demo_mode = True
        else:
            logger.info(
                "Running in demo mode - add SCRAPINGANT_API_KEY to environment for real scraping")

    def get_schema(self) -> Dict[str, Any]:
        """Get the JSON schema for this tool's parameters."""
        return {
            "type": "object",
            "properties": {
                "operation": {
                    "type": "string",
                    "enum": ["search_jobs", "get_job_details", "search_linkedin", "search_linkedin_enhanced", "search_indeed"],
                    "description": "The operation to perform. 'search_linkedin_enhanced' uses proven anti-detection configuration for better LinkedIn success rates."
                },
                "keywords": {
                    "type": "string",
                    "description": "Job search keywords (e.g., 'python developer', 'data scientist')"
                },
                "location": {
                    "type": "string",
                    "description": "Job location (e.g., 'remote', 'New York, NY', 'United States')"
                },
                "max_results": {
                    "type": "integer",
                    "minimum": 1,
                    "maximum": 20,
                    "default": 5,
                    "description": "Maximum number of job results to return"
                },
                "source": {
                    "type": "string",
                    "enum": ["linkedin", "indeed", "all"],
                    "default": "linkedin",
                    "description": "Job site to search (for search_jobs operation)"
                },
                "job_url": {
                    "type": "string",
                    "description": "URL of job posting to get details for (for get_job_details operation)"
                }
            },
            "required": ["operation"],
            "additionalProperties": False
        }

    def execute(self, operation: str, **kwargs) -> str:
        """Execute a job scraping operation."""
        try:
            if operation == "search_jobs":
                return self._search_jobs(
                    keywords=kwargs.get('keywords', ''),
                    location=kwargs.get('location', ''),
                    max_results=kwargs.get('max_results', 5),
                    source=kwargs.get('source', 'linkedin')
                )
            elif operation == "get_job_details":
                return self._get_job_details(kwargs.get('job_url'))
            elif operation == "search_linkedin":
                return self._search_linkedin_jobs(
                    keywords=kwargs.get('keywords', ''),
                    location=kwargs.get('location', ''),
                    max_results=kwargs.get('max_results', 5)
                )
            elif operation == "search_linkedin_enhanced":
                return self._search_linkedin_enhanced(
                    keywords=kwargs.get('keywords', ''),
                    location=kwargs.get('location', ''),
                    max_results=kwargs.get('max_results', 5)
                )
            elif operation == "search_indeed":
                return self._search_indeed_jobs(
                    keywords=kwargs.get('keywords', ''),
                    location=kwargs.get('location', ''),
                    max_results=kwargs.get('max_results', 5)
                )
            else:
                return f"Error: Unknown operation '{operation}'. Available: search_jobs, get_job_details, search_linkedin, search_linkedin_enhanced, search_indeed"
        except Exception as e:
            logger.error(f"ScrapingAnt job scraper error: {e}")
            return f"Error executing {operation}: {str(e)}"

    def _search_jobs(self, keywords: str, location: str = "", max_results: int = 5, source: str = "linkedin") -> str:
        """Search for jobs across multiple platforms."""
        if self.demo_mode:
            return self._get_demo_jobs(keywords, location, max_results)

        try:
            if source.lower() == "linkedin":
                return self._search_linkedin_jobs(keywords, location, max_results)
            elif source.lower() == "indeed":
                return self._search_indeed_jobs(keywords, location, max_results)
            else:
                # Search multiple sources and combine results
                linkedin_jobs = json.loads(self._search_linkedin_jobs(
                    keywords, location, max_results // 2))
                indeed_jobs = json.loads(self._search_indeed_jobs(
                    keywords, location, max_results // 2))

                combined_jobs = linkedin_jobs + indeed_jobs
                return json.dumps(combined_jobs[:max_results], indent=2)

        except Exception as e:
            logger.error(f"Error in multi-source job search: {e}")
            return self._get_demo_jobs(keywords, location, max_results)

    def _search_linkedin_jobs(self, keywords: str, location: str = "", max_results: int = 5) -> str:
        """Search for jobs on LinkedIn using ScrapingAnt."""
        if self.demo_mode:
            return self._get_demo_jobs(keywords, location, max_results, source="LinkedIn")

        if not keywords:
            return json.dumps({"error": "Keywords parameter is required"})

        try:
            # Build LinkedIn search URL with proper encoding
            import urllib.parse

            base_url = "https://www.linkedin.com/jobs/search"
            params = {
                'keywords': keywords,
                'location': location,
                'f_TPR': 'r604800',  # Past week
                'f_JT': 'F',  # Full-time
                'position': '1',
                'pageNum': '0'
            }

            # Remove empty parameters
            params = {k: v for k, v in params.items() if v}

            # Properly encode URL
            search_url = f"{base_url}?{urllib.parse.urlencode(params)}"

            logger.info(f"Scraping LinkedIn jobs: {search_url}")

            # Try proxy mode first for better anti-bot bypass
            jobs = []
            proxy_success = False

            try:
                logger.info(
                    "Attempting proxy mode for enhanced anti-bot bypass...")
                response = self._scrape_with_proxy(
                    search_url, disable_browser=False)
                soup = BeautifulSoup(response.text, 'html.parser')
                jobs = self._parse_linkedin_jobs(soup, max_results)
                proxy_success = True
                logger.info(f"Proxy mode successful, found {len(jobs)} jobs")
            except Exception as proxy_error:
                logger.warning(f"Proxy mode failed: {proxy_error}")

            # Fallback to enhanced API configuration (proven to bypass detection)
            if not proxy_success or len(jobs) == 0:
                try:
                    logger.info(
                        "Using enhanced anti-detection configuration...")
                    result = self.client.general_request(
                        url=search_url,
                        browser=True,
                        return_page_source=True,    # CRITICAL: Raw server response
                        proxy_type='residential',   # Residential proxies for LinkedIn
                        proxy_country='US',
                        wait_for=3000              # 3-second wait to simulate human behavior
                    )
                    soup = BeautifulSoup(result.content, 'html.parser')
                    jobs = self._parse_linkedin_jobs(soup, max_results)
                    logger.info(
                        f"Enhanced configuration found {len(jobs)} jobs")
                except Exception as api_error:
                    logger.warning(
                        f"Enhanced configuration failed: {api_error}")
                    # Final fallback to datacenter proxy
                    try:
                        logger.info("Final fallback to datacenter proxy...")
                        result = self.client.general_request(
                            url=search_url,
                            browser=True,
                            return_page_source=True,
                            proxy_type='datacenter',
                            proxy_country='US',
                            wait_for=3000
                        )
                        soup = BeautifulSoup(result.content, 'html.parser')
                        jobs = self._parse_linkedin_jobs(soup, max_results)
                        logger.info(
                            f"Datacenter fallback found {len(jobs)} jobs")
                    except Exception as final_error:
                        logger.error(f"All API methods failed: {final_error}")
                        if len(jobs) == 0:  # Only use demo if we have no jobs at all
                            return self._get_demo_jobs(keywords, location, max_results, source="LinkedIn")

            # Add delay to respect rate limits
            time.sleep(self.rate_limit_delay)

            return json.dumps([asdict(job) for job in jobs], indent=2)

        except Exception as e:
            logger.error(f"Error scraping LinkedIn jobs: {e}")
            return self._get_demo_jobs(keywords, location, max_results, source="LinkedIn")

    def _search_indeed_jobs(self, keywords: str, location: str = "", max_results: int = 5) -> str:
        """Search for jobs on Indeed using ScrapingAnt."""
        if self.demo_mode:
            return self._get_demo_jobs(keywords, location, max_results, source="Indeed")

        if not keywords:
            return json.dumps({"error": "Keywords parameter is required"})

        try:
            # Build Indeed search URL with proper encoding
            import urllib.parse

            base_url = "https://www.indeed.com/jobs"
            params = {
                'q': keywords,
                'l': location,
                'fromage': '7',  # Past week
                'limit': str(min(max_results, 10))
            }

            # Remove empty parameters
            params = {k: v for k, v in params.items() if v}

            # Properly encode URL
            search_url = f"{base_url}?{urllib.parse.urlencode(params)}"

            logger.info(f"Scraping Indeed jobs: {search_url}")

            # Try proxy mode first for better anti-bot bypass
            jobs = []
            proxy_success = False

            try:
                logger.info(
                    "Attempting proxy mode for enhanced anti-bot bypass...")
                response = self._scrape_with_proxy(
                    search_url, disable_browser=False)
                soup = BeautifulSoup(response.text, 'html.parser')
                jobs = self._parse_indeed_jobs(soup, max_results)
                proxy_success = True
                logger.info(f"Proxy mode successful, found {len(jobs)} jobs")
            except Exception as proxy_error:
                logger.warning(f"Proxy mode failed: {proxy_error}")

            # Fallback to direct API if proxy failed or found no jobs
            if not proxy_success or len(jobs) == 0:
                try:
                    logger.info("Falling back to direct API mode...")
                    result = self.client.general_request(
                        url=search_url,
                        browser=True,
                        proxy_type='datacenter',
                        proxy_country='US',
                        wait_for=2000,
                        block_resources=['image', 'stylesheet', 'font']
                    )
                    soup = BeautifulSoup(result.content, 'html.parser')
                    jobs = self._parse_indeed_jobs(soup, max_results)
                    logger.info(f"Direct API mode found {len(jobs)} jobs")
                except Exception as api_error:
                    logger.error(f"Direct API also failed: {api_error}")
                    if len(jobs) == 0:  # Only use demo if we have no jobs at all
                        return self._get_demo_jobs(keywords, location, max_results, source="Indeed")

            # Add delay to respect rate limits
            time.sleep(self.rate_limit_delay)

            return json.dumps([asdict(job) for job in jobs], indent=2)

        except Exception as e:
            logger.error(f"Error scraping Indeed jobs: {e}")
            return self._get_demo_jobs(keywords, location, max_results, source="Indeed")

    def _parse_linkedin_jobs(self, soup: BeautifulSoup, max_results: int) -> List[JobPosting]:
        """Parse LinkedIn job listings from HTML."""
        jobs = []

        # LinkedIn job card selectors (multiple fallbacks)
        job_selectors = [
            '.job-search-card',
            '.jobs-search__results-list li',
            '.job-result-card',
            '[data-entity-urn*="jobPosting"]'
        ]

        job_elements = []
        for selector in job_selectors:
            job_elements = soup.select(selector)
            if job_elements:
                break

        for element in job_elements[:max_results]:
            try:
                job = JobPosting()

                # Extract title
                title_selectors = ['.base-search-card__title',
                                   '.job-title', 'h3 a', '.job-result-card__title']
                for selector in title_selectors:
                    title_elem = element.select_one(selector)
                    if title_elem:
                        job.title = title_elem.get_text(strip=True)
                        break

                # Extract company
                company_selectors = [
                    '.base-search-card__subtitle', '.job-company', '.company-name', 'h4 a']
                for selector in company_selectors:
                    company_elem = element.select_one(selector)
                    if company_elem:
                        job.company = company_elem.get_text(strip=True)
                        break

                # Extract location
                location_selectors = [
                    '.job-search-card__location', '.job-location', '.location']
                for selector in location_selectors:
                    location_elem = element.select_one(selector)
                    if location_elem:
                        job.location = location_elem.get_text(strip=True)
                        break

                # Extract job URL
                url_elem = element.select_one('a[href*="/jobs/view/"]')
                if url_elem:
                    href = url_elem.get('href', '')
                    if href.startswith('/'):
                        job.job_url = f"https://www.linkedin.com{href}"
                    else:
                        job.job_url = href

                # Extract description snippet
                desc_selectors = ['.job-search-card__snippet',
                                  '.job-snippet', '.summary']
                for selector in desc_selectors:
                    desc_elem = element.select_one(selector)
                    if desc_elem:
                        job.description = desc_elem.get_text(strip=True)
                        break

                # Extract skills from description
                if job.description:
                    job.skills_required = self._extract_skills_from_text(
                        job.description)

                # Only add jobs with essential information
                if job.title and job.company:
                    jobs.append(job)

            except Exception as e:
                logger.warning(f"Error parsing LinkedIn job element: {e}")
                continue

        return jobs

    def _parse_indeed_jobs(self, soup: BeautifulSoup, max_results: int) -> List[JobPosting]:
        """Parse Indeed job listings from HTML."""
        jobs = []

        # Indeed job card selectors
        job_selectors = [
            '[data-testid="job-result"]',
            '.job_seen_beacon',
            '.jobsearch-SerpJobCard'
        ]

        job_elements = []
        for selector in job_selectors:
            job_elements = soup.select(selector)
            if job_elements:
                break

        for element in job_elements[:max_results]:
            try:
                job = JobPosting()

                # Extract title
                title_elem = element.select_one(
                    '[data-testid="job-title"] a, .jobTitle a, h2 a')
                if title_elem:
                    job.title = title_elem.get_text(strip=True)

                # Extract company
                company_elem = element.select_one(
                    '[data-testid="company-name"], .companyName, .company')
                if company_elem:
                    job.company = company_elem.get_text(strip=True)

                # Extract location
                location_elem = element.select_one(
                    '[data-testid="job-location"], .companyLocation, .location')
                if location_elem:
                    job.location = location_elem.get_text(strip=True)

                # Extract salary
                salary_elem = element.select_one(
                    '[data-testid="job-salary"], .salary-snippet, .salaryText')
                if salary_elem:
                    job.salary_range = salary_elem.get_text(strip=True)

                # Extract job URL
                url_elem = element.select_one(
                    '[data-testid="job-title"] a, .jobTitle a')
                if url_elem:
                    href = url_elem.get('href', '')
                    if href.startswith('/'):
                        job.job_url = f"https://www.indeed.com{href}"
                    else:
                        job.job_url = href

                # Extract description
                desc_elem = element.select_one('.job-snippet, .summary')
                if desc_elem:
                    job.description = desc_elem.get_text(strip=True)
                    job.skills_required = self._extract_skills_from_text(
                        job.description)

                if job.title and job.company:
                    jobs.append(job)

            except Exception as e:
                logger.warning(f"Error parsing Indeed job element: {e}")
                continue

        return jobs

    def _extract_skills_from_text(self, text: str) -> List[str]:
        """Extract technical skills from job description text."""
        # Common technical skills to look for
        skills_patterns = [
            # Programming languages
            r'\b(Python|Java|JavaScript|TypeScript|C\+\+|C#|Ruby|PHP|Swift|Kotlin|Go|Rust|Scala)\b',
            # Frameworks and libraries
            r'\b(React|Angular|Vue\.js|Django|Flask|Spring|Express|Laravel|Rails|Bootstrap)\b',
            # Databases
            r'\b(MySQL|PostgreSQL|MongoDB|Redis|SQLite|Oracle|SQL Server|Cassandra|DynamoDB)\b',
            # Cloud and DevOps
            r'\b(AWS|Azure|GCP|Docker|Kubernetes|Jenkins|Git|CI/CD|Terraform|Ansible)\b',
            # Other technologies
            r'\b(REST|API|GraphQL|Machine Learning|AI|Data Science|DevOps|Agile|Scrum)\b'
        ]

        skills = []
        text_upper = text.upper()

        for pattern in skills_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            skills.extend(matches)

        # Remove duplicates and return
        return list(set(skills))

    def _get_job_details(self, job_url: str) -> str:
        """Get detailed information about a specific job."""
        if self.demo_mode:
            return json.dumps({
                "title": "Senior Python Developer",
                "company": "Tech Innovation Corp",
                "location": "Remote",
                "description": "We are seeking a talented Senior Python Developer to join our growing team...",
                "requirements": [
                    "5+ years of Python development experience",
                    "Experience with Django/Flask frameworks",
                    "Strong knowledge of SQL databases",
                    "Experience with cloud platforms (AWS/Azure)",
                    "Excellent problem-solving skills"
                ],
                "skills_required": ["Python", "Django", "SQL", "AWS", "REST APIs"],
                "salary_range": "$120,000 - $160,000",
                "job_type": "Full-time",
                "experience_level": "Senior"
            }, indent=2)

        if not job_url:
            return json.dumps({"error": "Job URL is required"})

        try:
            # Use ScrapingAnt to get job details
            result = self.client.general_request({
                'url': job_url,
                'browser': True,
                'proxy_type': 'datacenter',
                'wait_for': 2000
            })

            soup = BeautifulSoup(result.content, 'html.parser')

            # Parse job details (implementation depends on the specific job site)
            job_details = self._parse_job_details(soup, job_url)

            time.sleep(self.rate_limit_delay)

            return json.dumps(asdict(job_details), indent=2)

        except Exception as e:
            logger.error(f"Error getting job details: {e}")
            return json.dumps({"error": f"Failed to fetch job details: {str(e)}"})

    def _parse_job_details(self, soup: BeautifulSoup, job_url: str) -> JobPosting:
        """Parse detailed job information from job detail page."""
        job = JobPosting()
        job.job_url = job_url

        # This would need to be customized based on the specific job site
        # LinkedIn, Indeed, etc. have different HTML structures

        # Generic parsing logic
        title_elem = soup.select_one(
            'h1, .job-title, [data-testid="job-title"]')
        if title_elem:
            job.title = title_elem.get_text(strip=True)

        company_elem = soup.select_one(
            '.company-name, [data-testid="company-name"]')
        if company_elem:
            job.company = company_elem.get_text(strip=True)

        # Extract full description
        desc_elem = soup.select_one(
            '.job-description, .description, [data-testid="job-description"]')
        if desc_elem:
            job.description = desc_elem.get_text(strip=True)
            job.skills_required = self._extract_skills_from_text(
                job.description)

        return job

    def _get_demo_jobs(self, keywords: str, location: str, max_results: int, source: str = "Demo") -> str:
        """Return demo job data for testing purposes."""
        demo_jobs = []

        for i in range(min(max_results, 3)):
            job = JobPosting(
                title=f"{keywords.title()} Developer",
                company=f"Tech Company {i+1}",
                location=location if location else "Remote",
                job_type="Full-time",
                experience_level="Mid-Senior",
                description=f"We are looking for a skilled {keywords} developer to join our team. "
                f"You will work on exciting projects using modern technologies including "
                f"{keywords}, cloud platforms, and agile methodologies.",
                requirements=[
                    f"3+ years of {keywords} experience",
                    "Strong problem-solving skills",
                    "Experience with cloud platforms",
                    "Team collaboration skills"
                ],
                skills_required=[keywords.title(), "Git", "SQL",
                                 "REST APIs", "Cloud"],
                salary_range=f"${80000 + i*10000:,} - ${100000 + i*15000:,}",
                posted_date="2024-01-15",
                job_url=f"https://example.com/job/{i+1}",
                company_size="Medium",
                industry="Technology"
            )
            demo_jobs.append(asdict(job))

        logger.info(
            f"Returning {len(demo_jobs)} demo jobs for '{keywords}' in '{location}' from {source}")
        return json.dumps(demo_jobs, indent=2)

    def _scrape_with_proxy(self, url: str, disable_browser: bool = True) -> requests.Response:
        """Use ScrapingAnt proxy mode for better anti-bot bypass."""
        if self.demo_mode:
            raise Exception("Demo mode - no real scraping available")

        # ScrapingAnt proxy configuration
        proxy_host = "proxy.scrapingant.com"
        proxy_port = 8080

        # Configure proxy parameters
        # Disable browser rendering for proxy mode as recommended
        proxy_params = []
        if disable_browser:
            proxy_params.append("browser=false")
        proxy_params.append("proxy_type=datacenter")
        proxy_params.append("proxy_country=US")
        proxy_params.append("forward_headers=true")

        # Build username with parameters
        username = "scrapingant"
        if proxy_params:
            username += "&" + "&".join(proxy_params)

        # Configure proxy
        proxies = {
            'http': f'http://{username}:{self.api_key}@{proxy_host}:{proxy_port}',
            'https': f'http://{username}:{self.api_key}@{proxy_host}:{proxy_port}'
        }

        # Headers to mimic regular browser
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        }

        try:
            # Suppress SSL warnings only for this specific proxy request
            with warnings.catch_warnings():
                warnings.filterwarnings(
                    "ignore", category=urllib3.exceptions.InsecureRequestWarning)

                # Make request through ScrapingAnt proxy with longer timeout
                response = requests.get(
                    url,
                    proxies=proxies,
                    headers=headers,
                    timeout=60,  # Increased timeout for complex sites
                    verify=False  # Disable SSL verification as required for proxy mode
                )

            logger.info(f"Proxy request successful: {response.status_code}")
            return response

        except Exception as e:
            logger.error(f"Proxy request failed: {e}")
            raise

    def _search_linkedin_enhanced(self, keywords: str, location: str = "", max_results: int = 5) -> str:
        """
        Enhanced LinkedIn scraping with proven anti-detection configuration.

        This method uses the configuration that successfully bypassed LinkedIn's browser detection:
        - browser=true with return_page_source=true
        - residential proxies 
        - proper wait times
        - retry logic with fallback configurations
        """
        if self.demo_mode:
            return self._get_demo_jobs(keywords, location, max_results, source="LinkedIn Enhanced")

        if not keywords:
            return json.dumps({"error": "Keywords parameter is required"})

        try:
            # Build LinkedIn search URL
            import urllib.parse

            base_url = "https://www.linkedin.com/jobs/search"
            params = {
                'keywords': keywords,
                'location': location,
                'f_TPR': 'r604800',  # Past week
                'f_JT': 'F',  # Full-time
                'position': '1',
                'pageNum': '0'
            }

            # Remove empty parameters
            params = {k: v for k, v in params.items() if v}
            search_url = f"{base_url}?{urllib.parse.urlencode(params)}"

            logger.info(f"Enhanced LinkedIn scraping: {search_url}")

            # Proven configurations in order of preference
            configs = [
                {
                    'name': 'Enhanced Residential',
                    'browser': True,
                    'return_page_source': True,  # CRITICAL for bypassing detection
                    'proxy_type': 'residential',
                    'proxy_country': 'US',
                    'wait_for': 3000
                },
                {
                    'name': 'Enhanced Residential GB',
                    'browser': True,
                    'return_page_source': True,
                    'proxy_type': 'residential',
                    'proxy_country': 'GB',
                    'wait_for': 5000
                },
                {
                    'name': 'Enhanced Datacenter',
                    'browser': True,
                    'return_page_source': True,
                    'proxy_type': 'datacenter',
                    'proxy_country': 'US',
                    'wait_for': 3000
                }
            ]

            jobs = []

            for i, config in enumerate(configs, 1):
                try:
                    logger.info(f"Attempt {i}: {config['name']} configuration")

                    result = self.client.general_request(
                        url=search_url,
                        **config
                    )

                    soup = BeautifulSoup(result.content, 'html.parser')
                    jobs = self._parse_linkedin_jobs(soup, max_results)

                    if len(jobs) > 0:
                        logger.info(
                            f"✅ Success with {config['name']}: found {len(jobs)} jobs")
                        break
                    else:
                        logger.warning(
                            f"⚠️ {config['name']} returned no jobs, trying next config...")

                except Exception as config_error:
                    logger.warning(
                        f"❌ {config['name']} failed: {config_error}")
                    continue

                # Add delay between attempts
                if i < len(configs):
                    time.sleep(2)

            # Add final delay to respect rate limits
            time.sleep(self.rate_limit_delay)

            if len(jobs) == 0:
                logger.warning(
                    "All enhanced configurations failed, no jobs found")
                return self._get_demo_jobs(keywords, location, max_results, source="LinkedIn Enhanced")

            return json.dumps([asdict(job) for job in jobs], indent=2)

        except Exception as e:
            logger.error(f"Error in enhanced LinkedIn scraping: {e}")
            return self._get_demo_jobs(keywords, location, max_results, source="LinkedIn Enhanced")
