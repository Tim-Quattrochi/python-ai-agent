"""Pytest configuration and shared fixtures for all tests."""

import pytest
import tempfile
import os
import json
from pathlib import Path
from typing import Dict, Any, List
from unittest.mock import Mock, patch

# Import necessary modules for fixtures
from src.tools.job_automation.resume_parser import ResumeData, ContactInfo, Experience, Education, Project
from src.tools.job_automation.job_scraper import JobPosting, JobSearchFilters
from src.tools.job_automation.company_research import CompanyInfo, ResearchSummary
from src.tools.job_automation.job_matcher import MatchScore
from src.config import Config
from src.agent import Agent


@pytest.fixture(scope="session")
def temp_dir():
    """Create a temporary directory for tests."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def sample_resume_data():
    """Create sample resume data for testing."""
    return ResumeData(
        contact_info=ContactInfo(
            name="John Doe",
            email="john.doe@email.com",
            phone="(555) 123-4567",
            location="San Francisco, CA",
            linkedin="linkedin.com/in/johndoe",
            github="github.com/johndoe"
        ),
        summary="Experienced software engineer with 5+ years in web development",
        skills=["Python", "JavaScript", "React",
                "Django", "PostgreSQL", "Docker", "AWS"],
        experience=[
            Experience(
                title="Senior Software Engineer",
                company="Tech Corp",
                duration="2020-2023",
                description="Led development of web applications using Python and React"
            ),
            Experience(
                title="Software Engineer",
                company="StartupCo",
                duration="2018-2020",
                description="Built REST APIs and microservices"
            )
        ],
        education=[
            Education(
                degree="Bachelor of Science in Computer Science",
                institution="University of Technology",
                graduation_year="2018",
                gpa="3.8"
            )
        ],
        projects=[
            Project(
                name="E-commerce Platform",
                description="Full-stack web application with payment integration",
                technologies=["Python", "Django", "React", "PostgreSQL"]
            )
        ],
        certifications=["AWS Certified Developer",
                        "Docker Certified Associate"]
    )


@pytest.fixture
def sample_job_posting():
    """Create sample job posting for testing."""
    return JobPosting(
        title="Senior Full Stack Developer",
        company="Amazing Tech",
        location="San Francisco, CA",
        description="We are looking for a senior full stack developer with experience in Python, React, and AWS.",
        requirements=[
            "5+ years of Python experience",
            "Experience with React and modern frontend frameworks",
            "Knowledge of cloud platforms (AWS preferred)",
            "Strong communication skills"
        ],
        skills=["Python", "React", "Django", "AWS", "PostgreSQL", "Docker"],
        experience_level="Senior",
        job_type="Full-time",
        salary="$120,000 - $150,000",
        posted_date="2025-01-15",
        job_url="https://example.com/job/123",
        company_size="100-500 employees",
        industry="Technology"
    )


@pytest.fixture
def sample_company_info():
    """Create sample company info for testing."""
    return CompanyInfo(
        name="Amazing Tech",
        website="https://amazingtech.com",
        industry="Technology",
        size="100-500 employees",
        founded="2015",
        headquarters="San Francisco, CA",
        description="Leading technology company focused on innovative solutions",
        mission="To make technology accessible to everyone",
        values=["Innovation", "Collaboration", "Integrity", "Customer Focus"],
        recent_news=["Raised $50M Series B",
                     "Launched new AI platform", "Expanded to European markets"],
        key_people=["Jane Smith (CEO)", "Bob Johnson (CTO)"],
        products_services=["Cloud Platform", "AI Solutions", "Mobile Apps"],
        culture_keywords=["innovation", "collaboration",
                          "remote-friendly", "growth"]
    )


@pytest.fixture
def sample_match_score():
    """Create sample match score for testing."""
    return MatchScore(
        total_score=75.0,
        skills_score=80.0,
        experience_score=85.0,
        keyword_score=70.0,
        location_score=90.0,
        skills_matched=["Python", "React", "Django"],
        skills_missing=["Kubernetes", "Docker"],
        experience_years=5.0,
        experience_level_match=True,
        keywords_found=["backend", "frontend", "API"],
        explanation="Good match with strong technical skills",
        recommendation="Apply - strong candidate"
    )


@pytest.fixture
def agent():
    """Create an agent instance for testing."""
    return Agent()


@pytest.fixture
def mock_config():
    """Create a mock configuration for testing."""
    config = Mock()
    config.llm_provider = "openai"
    config.model = "gpt-3.5-turbo"
    config.api_key = "test-api-key"
    config.max_tokens = 4000
    config.temperature = 0.7
    return config


@pytest.fixture
def sample_test_pdf(temp_dir):
    """Create a sample PDF file for testing."""
    pdf_path = temp_dir / "sample_resume.pdf"

    # Create a simple PDF using reportlab
    try:
        from reportlab.lib.pagesizes import letter
        from reportlab.pdfgen import canvas

        c = canvas.Canvas(str(pdf_path), pagesize=letter)
        c.drawString(100, 750, "John Doe")
        c.drawString(100, 730, "Software Engineer")
        c.drawString(100, 710, "Email: john.doe@email.com")
        c.drawString(100, 690, "Phone: (555) 123-4567")
        c.drawString(100, 650, "EXPERIENCE")
        c.drawString(
            100, 630, "Senior Software Engineer at Tech Corp (2020-2023)")
        c.drawString(
            100, 610, "• Developed web applications using Python and React")
        c.drawString(100, 570, "SKILLS")
        c.drawString(100, 550, "Python, JavaScript, React, Django, PostgreSQL")
        c.save()

    except ImportError:
        # Fallback: create a text file with PDF extension
        with open(pdf_path, 'w') as f:
            f.write("Mock PDF content for testing")

    return pdf_path


@pytest.fixture
def mock_email_config():
    """Mock email configuration for testing."""
    return {
        'smtp_host': 'smtp.gmail.com',
        'smtp_port': 587,
        'smtp_user': 'test@example.com',
        'smtp_password': 'test-password',
        'from_email': 'test@example.com'
    }


@pytest.fixture
def sample_job_search_filters():
    """Create sample job search filters."""
    return JobSearchFilters(
        keywords="Python developer",
        location="San Francisco",
        experience_level="mid",
        job_type="full-time",
        remote=True,
        salary_min=80000,
        salary_max=120000,
        posted_within="week"
    )


@pytest.fixture(autouse=True)
def mock_external_apis():
    """Mock external API calls by default."""
    with patch('requests.get') as mock_get, \
            patch('requests.post') as mock_post, \
            patch('selenium.webdriver.Chrome') as mock_driver:

        # Mock successful HTTP responses
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = "<html><body>Mock HTML content</body></html>"
        mock_response.json.return_value = {"status": "success", "data": []}

        mock_get.return_value = mock_response
        mock_post.return_value = mock_response

        # Mock selenium driver
        mock_driver_instance = Mock()
        mock_driver_instance.get.return_value = None
        mock_driver_instance.find_elements.return_value = []
        mock_driver_instance.page_source = "<html><body>Mock page</body></html>"
        mock_driver.return_value = mock_driver_instance

        yield {
            'mock_get': mock_get,
            'mock_post': mock_post,
            'mock_driver': mock_driver
        }


@pytest.fixture
def cleanup_test_files():
    """Clean up test files after tests."""
    test_files = []

    def add_file(filepath):
        test_files.append(filepath)

    yield add_file

    # Cleanup
    for filepath in test_files:
        if os.path.exists(filepath):
            os.remove(filepath)


# Test markers
pytest_plugins = []


def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line("markers", "unit: mark test as a unit test")
    config.addinivalue_line(
        "markers", "integration: mark test as an integration test")
    config.addinivalue_line(
        "markers", "job_automation: mark test as job automation related")
    config.addinivalue_line("markers", "agent: mark test as agent related")
    config.addinivalue_line(
        "markers", "communication: mark test as communication related")
    config.addinivalue_line("markers", "slow: mark test as slow running")
    config.addinivalue_line(
        "markers", "network: mark test as requiring network access")
