"""Test script for resume customizer tool."""

from src.tools.job_automation.job_scraper import JobPosting
from src.tools.job_automation.resume_parser import ResumeData, ContactInfo, Experience
from src.tools.job_automation.resume_customizer import ResumeCustomizerTool
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))


def test_resume_customizer():
    """Test the resume customizer tool."""
    print("🚀 Starting Resume Customizer Tests...")
    print("=" * 50)

    # Initialize tool
    customizer = ResumeCustomizerTool()

    # Test 1: Schema validation
    print("🧪 Testing Resume Customizer Schema...")
    schema = customizer.get_schema()
    assert "properties" in schema
    assert "operation" in schema["properties"]
    assert "resume_data" in schema["properties"]
    assert "job_data" in schema["properties"]
    print("✅ Schema validation passed!")

    # Create test data
    test_resume = ResumeData(
        contact_info=ContactInfo(
            name="John Doe",
            email="john@example.com",
            phone="555-123-4567",
            location="San Francisco, CA"
        ),
        summary="Software developer with 3 years of experience",
        skills=["Python", "JavaScript", "React", "Django", "SQL", "Git"],
        experience=[
            Experience(
                title="Software Developer",
                company="Tech Corp",
                duration="2021-2024",
                description="Developed web applications using Python and Django. Worked on React frontend components."
            )
        ]
    )

    test_job = JobPosting(
        title="Senior Python Developer",
        company="Amazing Tech",
        location="Remote",
        description="We are looking for a senior Python developer with experience in Django, Docker, and AWS. The ideal candidate should have strong problem-solving skills and experience with agile methodologies.",
        skills_required=["Python", "Django", "Docker", "AWS", "PostgreSQL"]
    )

    # Test 2: Suggest improvements
    print("🧪 Testing Improvement Suggestions...")
    suggestions_result = customizer.execute(
        operation="suggest_improvements",
        resume_data=test_resume,
        job_data=test_job
    )

    assert suggestions_result["success"] == True
    assert "suggestions" in suggestions_result
    suggestions = suggestions_result["suggestions"]

    print(f"Priority skills: {suggestions['priority_skills']}")
    print(f"Missing skills to add: {suggestions['missing_skills_to_add']}")
    print(f"Keywords to include: {suggestions['keywords_to_include']}")
    print("✅ Improvement suggestions test passed!")

    # Test 3: Preview changes
    print("🧪 Testing Preview Changes...")
    preview_result = customizer.execute(
        operation="preview_changes",
        resume_data=test_resume,
        job_data=test_job,
        customization_level="moderate"
    )

    assert preview_result["success"] == True
    assert "preview" in preview_result
    preview = preview_result["preview"]

    print(f"Skills reordering preview: {preview['skills_reordering']}")
    print(f"Summary changes preview: {preview['summary_changes']}")
    print("✅ Preview changes test passed!")

    # Test 4: Full customization (simplified without job matcher)
    print("🧪 Testing Full Resume Customization...")

    # Test just the suggestion generation first
    suggestions = customizer._generate_suggestions(
        test_resume, test_job, "moderate")
    print(
        f"Generated suggestions successfully: {len(suggestions.priority_skills)} priority skills")

    # Test applying customizations
    customized_resume = customizer._apply_customizations(
        test_resume, suggestions, True)
    print(
        f"Applied customizations successfully: {len(customized_resume.skills)} skills")

    print("✅ Basic customization test passed!")

    # Test 5: Test individual methods
    print("🧪 Testing Individual Methods...")

    # Test skill extraction
    job_skills = customizer._extract_job_skills(test_job)
    print(f"Extracted job skills: {job_skills}")

    # Test priority skills
    priority_skills = customizer._get_priority_skills(
        test_resume.skills, job_skills)
    print(f"Priority skills: {priority_skills}")

    print("✅ Individual methods test passed!")

    print("=" * 50)
    print("🎉 All resume customizer tests passed!")


if __name__ == "__main__":
    test_resume_customizer()
