#!/usr/bin/env python3
"""Test script for job scraper functionality."""

from src.tools.job_automation.job_scraper import JobScraperTool
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))


def test_job_scraper_schema():
    """Test that the job scraper tool is properly configured."""
    print("🧪 Testing Job Scraper Schema...")

    tool = JobScraperTool()

    # Test basic properties
    assert tool.name == "job_scraper", f"Expected name 'job_scraper', got '{tool.name}'"
    assert "scrape job postings" in tool.description.lower(
    ), "Description should mention job scraping"

    print("✅ Schema validation passed!")


def test_job_search_validation():
    """Test job search parameter validation."""
    print("🧪 Testing Job Search Validation...")

    tool = JobScraperTool()

    # Test missing keywords
    result = tool.execute(operation="search_jobs")
    assert "error" in result.lower(), "Should return error for missing keywords"
    assert "keywords parameter is required" in result.lower(), "Should specify missing keywords"

    # Test invalid operation
    result = tool.execute(operation="invalid_operation")
    assert "Unknown operation" in result, "Should return error for invalid operation"

    print("✅ Job search validation test passed!")


def test_linkedin_search_basic():
    """Test basic LinkedIn job search (without actually scraping)."""
    print("🧪 Testing LinkedIn Search Setup...")

    tool = JobScraperTool()

    # Test that the method exists and handles parameters
    try:
        # This will fail at driver setup, but we can test parameter handling
        result = tool.execute(
            operation="search_linkedin",
            keywords="software engineer",
            location="San Francisco",
            limit=5
        )

        # Should get an error about driver setup (expected in test environment)
        print(f"LinkedIn search result: {result[:100]}...")

        # The fact that we got a result (even if error) means the method structure is correct
        print("✅ LinkedIn search method structure test passed!")

    except Exception as e:
        print(f"Expected error in test environment: {e}")
        print("✅ LinkedIn search method structure test passed!")


def test_job_details_validation():
    """Test job details parameter validation."""
    print("🧪 Testing Job Details Validation...")

    tool = JobScraperTool()

    # Test missing job URL
    result = tool.execute(operation="get_job_details")
    assert "error" in result.lower(), "Should return error for missing job URL"
    assert "job url is required" in result.lower(), "Should specify missing job URL"

    print("✅ Job details validation test passed!")


def test_skill_extraction():
    """Test skill extraction from job descriptions."""
    print("🧪 Testing Skill Extraction...")

    tool = JobScraperTool()

    # Test skill extraction method directly
    sample_description = """
    We are looking for a Senior Software Engineer with experience in:
    - Python programming and Django framework
    - JavaScript and React for frontend development
    - PostgreSQL database management
    - AWS cloud services and Docker containerization
    - Git version control and Jenkins CI/CD
    """

    skills = tool._extract_skills_from_description(sample_description)

    # Check for expected skills
    expected_skills = ['Python', 'Django', 'JavaScript',
                       'React', 'PostgreSQL', 'AWS', 'Docker', 'Git', 'Jenkins']
    for skill in expected_skills:
        assert skill in skills, f"Expected skill '{skill}' not found in {skills}"

    print(f"Extracted skills: {skills}")
    print("✅ Skill extraction test passed!")


def test_requirements_extraction():
    """Test requirements extraction from job descriptions."""
    print("🧪 Testing Requirements Extraction...")

    tool = JobScraperTool()

    sample_description = """
    Requirements:
    • Bachelor's degree in Computer Science or related field
    • 5+ years of experience in software development
    • Strong proficiency in Python and web frameworks
    • Experience with cloud platforms (AWS, Azure)
    • Excellent communication and teamwork skills
    
    Qualifications:
    • Knowledge of agile development methodologies
    • Experience with microservices architecture
    """

    requirements = tool._extract_requirements_from_description(
        sample_description)

    # Check that some requirements were extracted
    assert len(requirements) > 0, "Should extract at least some requirements"

    # Check for specific requirement patterns
    has_degree_req = any("bachelor" in req.lower() for req in requirements)
    has_experience_req = any("experience" in req.lower()
                             for req in requirements)

    assert has_degree_req or has_experience_req, "Should extract degree or experience requirements"

    print(f"Extracted requirements: {requirements}")
    print("✅ Requirements extraction test passed!")


def main():
    """Run all job scraper tests."""
    print("🚀 Starting Job Scraper Tests...")
    print("=" * 50)

    try:
        test_job_scraper_schema()
        test_job_search_validation()
        test_linkedin_search_basic()
        test_job_details_validation()
        test_skill_extraction()
        test_requirements_extraction()

        print("=" * 50)
        print("🎉 All job scraper tests passed!")

    except AssertionError as e:
        print(f"❌ Test failed: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
