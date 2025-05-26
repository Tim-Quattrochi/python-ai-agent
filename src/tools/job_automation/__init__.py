"""Job automation tools package."""

from .resume_parser import ResumeParserTool, ResumeData, ContactInfo, Experience, Education, Project
from .job_scraper import JobScraperTool, JobPosting, JobSearchFilters
from .job_matcher import JobMatcherTool, JobMatchResult, MatchScore
from .resume_customizer import ResumeCustomizerTool
from .company_research import CompanyResearchTool, CompanyInfo, ResearchSummary
from .cover_letter_generator import CoverLetterGeneratorTool, CoverLetterTemplate, CoverLetterContent
from .application_orchestrator import JobApplicationOrchestrator, ApplicationConfig, ApplicationResult

# Optional ScrapingAnt scraper
try:
    from .scrapingant_scraper import ScrapingAntJobScraper
    SCRAPINGANT_AVAILABLE = True
except ImportError:
    ScrapingAntJobScraper = None
    SCRAPINGANT_AVAILABLE = False

__all__ = [
    # Tools
    'ResumeParserTool',
    'JobScraperTool',
    'JobMatcherTool',
    'ResumeCustomizerTool',
    'CompanyResearchTool',
    'CoverLetterGeneratorTool',
    'JobApplicationOrchestrator',

    # Data structures
    'ResumeData',
    'ContactInfo',
    'Experience',
    'Education',
    'Project',
    'JobPosting',
    'JobSearchFilters',
    'JobMatchResult',
    'MatchScore',
    'CompanyInfo',
    'ResearchSummary',
    'CoverLetterTemplate',
    'CoverLetterContent',
    'ApplicationConfig',
    'ApplicationResult',

    # Optional tools
    'ScrapingAntJobScraper',
    'SCRAPINGANT_AVAILABLE',
]
