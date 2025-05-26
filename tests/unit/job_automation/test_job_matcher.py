#!/usr/bin/env python3
"""Test script for job matcher functionality."""

from src.tools.job_automation.job_matcher import JobMatcherTool
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))


def test_job_matcher_schema():
    """Test that the job matcher tool is properly configured."""
    print("🧪 Testing Job Matcher Schema...")

    tool = JobMatcherTool()

    # Test basic properties
    assert tool.name == "job_matcher", f"Expected name 'job_matcher', got '{tool.name}'"
    assert "match resumes" in tool.description.lower(
    ), "Description should mention resume matching"

    # Test schema
    schema = tool.get_schema()
    assert "operation" in schema["properties"], "Schema should have operation parameter"
    assert "match_job" in schema["properties"]["operation"]["enum"], "Should support match_job operation"

    print("✅ Schema validation passed!")


def test_match_validation():
    """Test job matching parameter validation."""
    print("🧪 Testing Match Validation...")

    tool = JobMatcherTool()

    # Test missing data
    result = tool.execute(operation="match_job")
    assert "Error" in result, "Should return error for missing data"
    assert "resume_data and job_data are required" in result, "Should specify missing parameters"

    # Test invalid operation
    result = tool.execute(operation="invalid_operation")
    assert "Unknown operation" in result, "Should return error for invalid operation"

    print("✅ Match validation test passed!")


def test_skills_matching():
    """Test skills matching algorithm."""
    print("🧪 Testing Skills Matching...")

    tool = JobMatcherTool()

    # Create sample resume data
    from src.tools.job_automation.resume_parser import ResumeData, ContactInfo
    resume = ResumeData()
    resume.skills = ['Python', 'JavaScript',
                     'React', 'Django', 'PostgreSQL', 'AWS']
    resume.contact_info = ContactInfo()
    resume.contact_info.name = "Test User"

    # Create sample job data
    from src.tools.job_automation.job_scraper import JobPosting
    job = JobPosting()
    job.title = "Senior Python Developer"
    job.company = "Tech Corp"
    job.skills_required = ['Python', 'Django',
                           'PostgreSQL', 'Docker', 'Kubernetes']
    job.description = "We need a senior developer with 5+ years of experience in Python development."

    # Test skills calculation
    score, matched, missing = tool._calculate_skills_score(resume, job)

    print(f"Skills score: {score:.1f}%")
    print(f"Matched skills: {matched}")
    print(f"Missing skills: {missing}")

    # Verify results
    assert score > 0, "Should have some skills match"
    assert 'Python' in matched, "Python should be matched"
    assert 'Django' in matched, "Django should be matched"
    assert 'Docker' in missing or 'Kubernetes' in missing, "Should identify missing skills"

    print("✅ Skills matching test passed!")


def test_experience_calculation():
    """Test experience calculation."""
    print("🧪 Testing Experience Calculation...")

    tool = JobMatcherTool()

    # Test experience duration parsing
    test_cases = [
        ("2020-2023", 3.0),
        ("5 years", 5.0),
        ("2 years 6 months", 2.5),  # This might not work perfectly, but let's see
        ("2019-present", 5.0)  # Approximate, depends on current year
    ]

    for duration, expected in test_cases:
        years = tool._parse_experience_duration(duration)
        print(
            f"Duration '{duration}' -> {years:.1f} years (expected ~{expected})")
        # Allow some tolerance for "present" calculations
        if "present" not in duration:
            assert abs(
                years - expected) < 1.0, f"Experience parsing failed for '{duration}'"

    # Test required experience extraction
    job_desc = "We are looking for a candidate with 3+ years of experience in software development."
    required = tool._extract_required_experience(job_desc)
    print(f"Required experience from description: {required} years")
    assert required == 3.0, f"Should extract 3 years, got {required}"

    print("✅ Experience calculation test passed!")


def test_complete_matching():
    """Test complete job matching workflow."""
    print("🧪 Testing Complete Matching...")

    tool = JobMatcherTool()

    # Create comprehensive test data
    resume_data = {
        "skills": ["Python", "JavaScript", "React", "Django", "PostgreSQL", "Git"],
        "experience": [
            {
                "title": "Software Engineer",
                "company": "Tech Co",
                "duration": "2020-2023",
                "description": "Developed web applications using Python and React"
            },
            {
                "title": "Junior Developer",
                "company": "Startup Inc",
                "duration": "2018-2020",
                "description": "Built REST APIs with Django"
            }
        ],
        "summary": "Experienced full-stack developer with expertise in Python and web technologies",
        "contact_info": {"name": "John Doe", "location": "San Francisco"}
    }

    job_data = {
        "title": "Senior Full Stack Developer",
        "company": "Amazing Tech",
        "location": "San Francisco, CA",
        "skills_required": ["Python", "Django", "React", "PostgreSQL", "Docker"],
        "description": "We need a senior developer with 4+ years of experience. Must know Python, Django, React. Experience with Docker is a plus. Must work well in agile environment.",
        "experience_level": "Mid-Senior"
    }

    # Test single job matching
    result = tool.execute(
        operation="match_job",
        resume_data=resume_data,
        job_data=job_data
    )

    print("Match result:")
    print(result[:500] + "..." if len(result) > 500 else result)

    # Verify result contains expected elements
    assert "Job Match Analysis" in result, "Should contain analysis header"
    assert "Overall Match Score" in result, "Should show overall score"
    assert "Skills Matched" in result, "Should show matched skills"
    assert "Python" in result, "Should mention Python skill"

    print("✅ Complete matching test passed!")


def test_batch_matching():
    """Test batch job matching."""
    print("🧪 Testing Batch Matching...")

    tool = JobMatcherTool()

    resume_data = {
        "skills": ["Python", "Django", "React"],
        "experience": [{"duration": "3 years", "description": "Python development"}],
        "summary": "Python developer"
    }

    jobs_list = [
        {
            "title": "Python Developer",
            "company": "Company A",
            "skills_required": ["Python", "Django"],
            "description": "2+ years Python experience required"
        },
        {
            "title": "Java Developer",
            "company": "Company B",
            "skills_required": ["Java", "Spring"],
            "description": "Java expertise required"
        },
        {
            "title": "Full Stack Developer",
            "company": "Company C",
            "skills_required": ["Python", "React", "Django"],
            "description": "Full stack development"
        }
    ]

    result = tool.execute(
        operation="batch_match",
        resume_data=resume_data,
        jobs_list=jobs_list,
        threshold=50
    )

    print("Batch result:")
    print(result[:400] + "..." if len(result) > 400 else result)

    # Should find at least the Python and Full Stack jobs
    assert "Batch Job Matching Results" in result, "Should contain batch results header"
    assert "Python Developer" in result or "Full Stack Developer" in result, "Should match relevant jobs"

    print("✅ Batch matching test passed!")


def main():
    """Run all job matcher tests."""
    print("🚀 Starting Job Matcher Tests...")
    print("=" * 50)

    try:
        test_job_matcher_schema()
        test_match_validation()
        test_skills_matching()
        test_experience_calculation()
        test_complete_matching()
        test_batch_matching()

        print("=" * 50)
        print("🎉 All job matcher tests passed!")

    except AssertionError as e:
        print(f"❌ Test failed: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
