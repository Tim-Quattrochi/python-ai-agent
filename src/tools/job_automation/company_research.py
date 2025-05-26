"""Company research tool for gathering information to personalize job applications."""

import re
import logging
import requests
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, asdict
from datetime import datetime
from bs4 import BeautifulSoup

from .job_scraper import JobPosting
from ..base import Tool

logger = logging.getLogger(__name__)


@dataclass
class CompanyInfo:
    """Company information data structure."""
    name: str = ""
    website: str = ""
    industry: str = ""
    size: str = ""
    founded: str = ""
    headquarters: str = ""
    description: str = ""
    mission: str = ""
    values: List[str] = None
    recent_news: List[str] = None
    key_people: List[str] = None
    products_services: List[str] = None
    culture_keywords: List[str] = None

    def __post_init__(self):
        if self.values is None:
            self.values = []
        if self.recent_news is None:
            self.recent_news = []
        if self.key_people is None:
            self.key_people = []
        if self.products_services is None:
            self.products_services = []
        if self.culture_keywords is None:
            self.culture_keywords = []


@dataclass
class ResearchSummary:
    """Research summary for application personalization."""
    company_info: CompanyInfo
    talking_points: List[str] = None
    personalization_tips: List[str] = None
    cover_letter_hooks: List[str] = None
    interview_questions: List[str] = None
    company_fit_score: float = 0.0
    research_timestamp: str = ""

    def __post_init__(self):
        if self.talking_points is None:
            self.talking_points = []
        if self.personalization_tips is None:
            self.personalization_tips = []
        if self.cover_letter_hooks is None:
            self.cover_letter_hooks = []
        if self.interview_questions is None:
            self.interview_questions = []
        if not self.research_timestamp:
            self.research_timestamp = datetime.now().isoformat()


class CompanyResearchTool(Tool):
    """A tool for researching companies to personalize job applications."""

    def __init__(self):
        super().__init__(
            name="company_research",
            description="Research companies to gather information for personalizing job applications and cover letters."
        )

        # Common culture keywords to look for
        self.culture_keywords = [
            'innovation', 'collaboration', 'diversity', 'inclusion', 'sustainability',
            'growth', 'learning', 'development', 'teamwork', 'excellence',
            'integrity', 'customer-focused', 'agile', 'remote-friendly', 'flexible',
            'work-life balance', 'entrepreneurial', 'fast-paced', 'data-driven'
        ]

    def get_schema(self) -> Dict[str, Any]:
        """Get the JSON schema for company research parameters."""
        return {
            "type": "object",
            "properties": {
                "operation": {
                    "type": "string",
                    "enum": ["research_company", "analyze_job_posting", "generate_talking_points"],
                    "description": "The research operation to perform"
                },
                "company_name": {
                    "type": "string",
                    "description": "Name of the company to research"
                },
                "company_website": {
                    "type": "string",
                    "description": "Company website URL (optional)"
                },
                "job_posting": {
                    "type": "object",
                    "description": "Job posting data to extract company information from"
                },
                "research_depth": {
                    "type": "string",
                    "enum": ["basic", "detailed", "comprehensive"],
                    "description": "Depth of research to perform",
                    "default": "detailed"
                },
                "focus_areas": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Specific areas to focus research on",
                    "default": ["culture", "values", "recent_news", "leadership"]
                }
            },
            "required": ["operation"]
        }

    def execute(self, **kwargs) -> Dict[str, Any]:
        """Execute company research operation."""
        try:
            operation = kwargs.get('operation', 'research_company')

            if operation == "research_company":
                company_name = kwargs.get('company_name')
                company_website = kwargs.get('company_website')

                if not company_name:
                    return {
                        "success": False,
                        "error": "Company name is required for research"
                    }

                return self._research_company(
                    company_name,
                    company_website,
                    kwargs.get('research_depth', 'detailed'),
                    kwargs.get('focus_areas', [
                               'culture', 'values', 'recent_news', 'leadership'])
                )

            elif operation == "analyze_job_posting":
                job_posting = kwargs.get('job_posting')

                if not job_posting:
                    return {
                        "success": False,
                        "error": "Job posting data is required"
                    }

                return self._analyze_job_posting(
                    job_posting,
                    kwargs.get('research_depth', 'detailed')
                )

            elif operation == "generate_talking_points":
                company_info = kwargs.get('company_info')
                job_posting = kwargs.get('job_posting')

                if not company_info:
                    return {
                        "success": False,
                        "error": "Company information is required for talking points"
                    }

                return self._generate_talking_points(company_info, job_posting)

            else:
                return {
                    "success": False,
                    "error": f"Unknown operation: {operation}"
                }

        except Exception as e:
            logger.error(f"Company research error: {str(e)}")
            return {
                "success": False,
                "error": f"Company research failed: {str(e)}"
            }

    def _research_company(self, company_name: str, company_website: Optional[str],
                          depth: str, focus_areas: List[str]) -> Dict[str, Any]:
        """Research a company and gather information."""
        company_info = CompanyInfo(name=company_name)

        # Try to find company website if not provided
        if not company_website:
            company_website = self._find_company_website(company_name)

        if company_website:
            company_info.website = company_website

            # Scrape company website
            website_info = self._scrape_company_website(
                company_website, focus_areas)
            company_info = self._merge_company_info(company_info, website_info)

        # Search for recent news
        if 'recent_news' in focus_areas:
            company_info.recent_news = self._search_company_news(company_name)

        # Generate research summary
        research_summary = self._generate_research_summary(company_info, depth)

        return {
            "success": True,
            "company_info": asdict(company_info),
            "research_summary": asdict(research_summary),
            "summary": self._format_research_output(research_summary)
        }

    def _analyze_job_posting(self, job_posting_data: dict, depth: str) -> Dict[str, Any]:
        """Analyze job posting to extract company information."""
        if isinstance(job_posting_data, dict):
            job_posting = JobPosting(**job_posting_data)
        else:
            job_posting = job_posting_data

        # Extract company info from job posting
        company_info = CompanyInfo(
            name=job_posting.company,
            industry=job_posting.industry,
            size=job_posting.company_size
        )

        # Research the company further
        research_result = self._research_company(
            job_posting.company,
            None,  # Let it find the website
            depth,
            ['culture', 'values', 'recent_news']
        )

        if research_result.get('success'):
            return research_result
        else:
            # Return basic info from job posting
            return {
                "success": True,
                "company_info": asdict(company_info),
                "summary": f"Basic company information extracted from job posting for {job_posting.company}"
            }

    def _generate_talking_points(self, company_info_data: dict, job_posting_data: Optional[dict] = None) -> Dict[str, Any]:
        """Generate talking points for interviews and cover letters."""
        if isinstance(company_info_data, dict):
            company_info = CompanyInfo(**company_info_data)
        else:
            company_info = company_info_data

        talking_points = []
        personalization_tips = []
        cover_letter_hooks = []

        # Generate talking points based on company values
        if company_info.values:
            for value in company_info.values[:3]:
                talking_points.append(
                    f"Alignment with {value}: How your experience demonstrates this value")
                cover_letter_hooks.append(
                    f"I'm particularly drawn to {company_info.name}'s commitment to {value}")

        # Generate points from recent news
        if company_info.recent_news:
            for news in company_info.recent_news[:2]:
                talking_points.append(f"Recent development: {news[:100]}...")
                cover_letter_hooks.append(
                    f"I was excited to read about {company_info.name}'s recent {news[:50]}...")

        # Generate personalization tips
        if company_info.culture_keywords:
            for keyword in company_info.culture_keywords[:3]:
                personalization_tips.append(
                    f"Emphasize experience with {keyword} in your application")

        if company_info.products_services:
            personalization_tips.append(
                f"Mention familiarity with {company_info.products_services[0]} if relevant")

        result = {
            "talking_points": talking_points,
            "personalization_tips": personalization_tips,
            "cover_letter_hooks": cover_letter_hooks,
            "company_info": asdict(company_info)
        }

        return {
            "success": True,
            "result": result,
            "summary": self._format_talking_points_output(result)
        }

    def _find_company_website(self, company_name: str) -> Optional[str]:
        """Try to find company website through search."""
        try:
            # Simple heuristic - try common patterns
            common_domains = [
                f"https://www.{company_name.lower().replace(' ', '')}.com",
                f"https://{company_name.lower().replace(' ', '')}.com",
                f"https://www.{company_name.lower().replace(' ', '-')}.com",
                f"https://{company_name.lower().replace(' ', '-')}.com"
            ]

            for domain in common_domains:
                try:
                    response = requests.head(
                        domain, timeout=5, allow_redirects=True)
                    if response.status_code == 200:
                        return domain
                except:
                    continue

            return None
        except Exception as e:
            logger.error(f"Error finding company website: {e}")
            return None

    def _scrape_company_website(self, website_url: str, focus_areas: List[str]) -> CompanyInfo:
        """Scrape company website for information."""
        company_info = CompanyInfo()

        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            response = requests.get(website_url, headers=headers, timeout=10)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, 'html.parser')

            # Extract description from meta tags or about section
            description_meta = soup.find('meta', attrs={'name': 'description'})
            if description_meta:
                company_info.description = description_meta.get('content', '')

            # Look for about/values/culture pages
            if 'culture' in focus_areas or 'values' in focus_areas:
                company_info.culture_keywords = self._extract_culture_keywords(
                    soup)
                company_info.values = self._extract_company_values(soup)

            # Extract mission statement
            company_info.mission = self._extract_mission_statement(soup)

            # Extract products/services
            company_info.products_services = self._extract_products_services(
                soup)

        except Exception as e:
            logger.error(f"Error scraping company website: {e}")

        return company_info

    def _extract_culture_keywords(self, soup: BeautifulSoup) -> List[str]:
        """Extract culture-related keywords from website content."""
        found_keywords = []
        text_content = soup.get_text().lower()

        for keyword in self.culture_keywords:
            if keyword in text_content:
                found_keywords.append(keyword)

        return found_keywords[:10]  # Limit to top 10

    def _extract_company_values(self, soup: BeautifulSoup) -> List[str]:
        """Extract company values from website."""
        values = []

        # Look for common value section patterns
        value_patterns = [
            'our values', 'core values', 'company values', 'our principles',
            'what we believe', 'our mission', 'our culture'
        ]

        for pattern in value_patterns:
            sections = soup.find_all(text=re.compile(pattern, re.IGNORECASE))
            for section in sections:
                parent = section.parent
                if parent:
                    # Look for list items or headings near this section
                    nearby_items = parent.find_all(['li', 'h3', 'h4', 'h5'])
                    for item in nearby_items:
                        text = item.get_text().strip()
                        if text and len(text) < 100:  # Reasonable value length
                            values.append(text)

        return list(set(values))[:5]  # Remove duplicates and limit

    def _extract_mission_statement(self, soup: BeautifulSoup) -> str:
        """Extract mission statement from website."""
        mission_patterns = [
            'our mission', 'mission statement', 'our purpose', 'why we exist'
        ]

        for pattern in mission_patterns:
            mission_sections = soup.find_all(
                text=re.compile(pattern, re.IGNORECASE))
            for section in mission_sections:
                parent = section.parent
                if parent:
                    # Look for nearby paragraph or text
                    next_p = parent.find_next('p')
                    if next_p:
                        mission_text = next_p.get_text().strip()
                        if len(mission_text) > 50:  # Reasonable mission length
                            return mission_text[:500]  # Limit length

        return ""

    def _extract_products_services(self, soup: BeautifulSoup) -> List[str]:
        """Extract products and services from website."""
        products = []

        # Look for navigation menus, product sections
        nav_items = soup.find_all(['nav', 'header'])
        for nav in nav_items:
            links = nav.find_all('a')
            for link in links:
                text = link.get_text().strip()
                if text and 'product' in text.lower() or 'service' in text.lower():
                    products.append(text)

        # Look for product/service headings
        headings = soup.find_all(['h1', 'h2', 'h3'])
        for heading in headings:
            text = heading.get_text().strip()
            if any(keyword in text.lower() for keyword in ['product', 'service', 'solution']):
                products.append(text)

        return list(set(products))[:10]  # Remove duplicates and limit

    def _search_company_news(self, company_name: str) -> List[str]:
        """Search for recent company news."""
        # This is a simplified implementation
        # In a real implementation, you'd use a news API or search engine
        news_items = [
            f"{company_name} announces new product launch",
            f"{company_name} expands to new markets",
            f"{company_name} receives industry recognition"
        ]

        return news_items[:3]  # Limit to 3 recent items

    def _merge_company_info(self, base_info: CompanyInfo, additional_info: CompanyInfo) -> CompanyInfo:
        """Merge two CompanyInfo objects."""
        # Update fields if additional info has content
        if additional_info.description and not base_info.description:
            base_info.description = additional_info.description

        if additional_info.mission and not base_info.mission:
            base_info.mission = additional_info.mission

        base_info.values.extend(additional_info.values)
        base_info.culture_keywords.extend(additional_info.culture_keywords)
        base_info.products_services.extend(additional_info.products_services)

        # Remove duplicates
        base_info.values = list(set(base_info.values))
        base_info.culture_keywords = list(set(base_info.culture_keywords))
        base_info.products_services = list(set(base_info.products_services))

        return base_info

    def _generate_research_summary(self, company_info: CompanyInfo, depth: str) -> ResearchSummary:
        """Generate a research summary with personalization insights."""
        summary = ResearchSummary(company_info=company_info)

        # Generate talking points
        if company_info.values:
            summary.talking_points.extend([
                f"Company values alignment: {value}" for value in company_info.values[:3]
            ])

        if company_info.recent_news:
            summary.talking_points.extend([
                f"Recent development: {news[:50]}..." for news in company_info.recent_news[:2]
            ])

        # Generate personalization tips
        if company_info.culture_keywords:
            summary.personalization_tips.extend([
                f"Emphasize {keyword} in your application" for keyword in company_info.culture_keywords[:5]
            ])

        # Generate cover letter hooks
        if company_info.mission:
            summary.cover_letter_hooks.append(
                f"I'm inspired by {company_info.name}'s mission")

        if company_info.values:
            summary.cover_letter_hooks.extend([
                f"I share {company_info.name}'s commitment to {value}" for value in company_info.values[:2]
            ])

        # Calculate company fit score (simplified)
        fit_score = 0.0
        if company_info.description:
            fit_score += 20
        if company_info.values:
            fit_score += len(company_info.values) * 10
        if company_info.culture_keywords:
            fit_score += len(company_info.culture_keywords) * 5
        if company_info.recent_news:
            fit_score += len(company_info.recent_news) * 10

        summary.company_fit_score = min(100.0, fit_score)

        return summary

    def _format_research_output(self, research_summary: ResearchSummary) -> str:
        """Format research output for display."""
        company = research_summary.company_info

        output = f"""
🏢 Company Research Report: {company.name}
==================================================

📋 Basic Information:
   • Website: {company.website or 'Not found'}
   • Industry: {company.industry or 'Unknown'}
   • Size: {company.size or 'Unknown'}

📝 Description:
   {company.description[:200] + '...' if company.description else 'Not available'}

🎯 Mission:
   {company.mission[:200] + '...' if company.mission else 'Not available'}

💎 Core Values ({len(company.values)}):
   {', '.join(company.values[:5]) if company.values else 'Not identified'}

🏛️ Culture Keywords ({len(company.culture_keywords)}):
   {', '.join(company.culture_keywords[:8]) if company.culture_keywords else 'Not identified'}

📰 Recent News ({len(company.recent_news)}):
   {chr(10).join(f'   • {news[:80]}...' for news in company.recent_news[:3]) if company.recent_news else '   None found'}

💡 Talking Points ({len(research_summary.talking_points)}):
   {chr(10).join(f'   • {point}' for point in research_summary.talking_points[:5]) if research_summary.talking_points else '   None generated'}

🎪 Cover Letter Hooks ({len(research_summary.cover_letter_hooks)}):
   {chr(10).join(f'   • {hook}' for hook in research_summary.cover_letter_hooks[:3]) if research_summary.cover_letter_hooks else '   None generated'}

📊 Company Fit Score: {research_summary.company_fit_score:.1f}%
        """.strip()

        return output

    def _format_talking_points_output(self, result: dict) -> str:
        """Format talking points output for display."""
        return f"""
💡 Personalization Guide
==================================================

🎯 Talking Points ({len(result['talking_points'])}):
   {chr(10).join(f'   • {point}' for point in result['talking_points'][:5])}

💎 Personalization Tips ({len(result['personalization_tips'])}):
   {chr(10).join(f'   • {tip}' for tip in result['personalization_tips'][:5])}

✉️ Cover Letter Hooks ({len(result['cover_letter_hooks'])}):
   {chr(10).join(f'   • {hook}' for hook in result['cover_letter_hooks'][:3])}
        """.strip()
