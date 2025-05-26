#!/usr/bin/env python3
"""Test script for the cover letter generator tool."""

from src.tools.job_automation.company_research import CompanyInfo
from src.tools.job_automation.job_scraper import JobPosting
from src.tools.job_automation.resume_parser import ResumeData, ContactInfo, Experience, Education, Project
from src.tools.job_automation.cover_letter_generator import CoverLetterGeneratorTool
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))


def create_sample_resume_data():
    """Create sample resume data for testing."""
    return ResumeData(
        contact_info=ContactInfo(
            name="Sarah Johnson",
            email="sarah.johnson@email.com",
            phone="(555) 123-4567",
            location="San Francisco, CA",
            linkedin="linkedin.com/in/sarahjohnson",
            github="github.com/sarahjohnson"
        ),
        summary="Experienced full-stack developer with 5+ years building scalable web applications using Python, JavaScript, and React. Passionate about creating efficient solutions and mentoring junior developers.",
        skills=[
            "Python", "JavaScript", "React", "Node.js", "Django", "PostgreSQL",
            "AWS", "Docker", "Git", "Agile", "REST APIs", "GraphQL",
            "TypeScript", "Redux", "MongoDB", "Redis", "Kubernetes"
        ],
        experience=[
            Experience(
                title="Senior Software Developer",
                company="TechCorp Inc",
                duration="2022 - Present",
                description="Lead development of microservices architecture serving 100K+ users. Implemented CI/CD pipelines reducing deployment time by 60%. Mentored 3 junior developers."
            ),
            Experience(
                title="Full Stack Developer",
                company="StartupXYZ",
                duration="2020 - 2022",
                description="Built responsive web applications using React and Python. Optimized database queries improving performance by 40%. Collaborated with UX team on user-centered design."
            ),
            Experience(
                title="Junior Developer",
                company="DevShop",
                duration="2019 - 2020",
                description="Developed REST APIs and frontend components. Participated in agile development process. Gained experience with cloud deployment and testing frameworks."
            )
        ],
        education=[
            Education(
                degree="B.S. Computer Science",
                institution="University of California, Berkeley",
                graduation_year="2019",
                gpa="3.8/4.0"
            )
        ],
        projects=[
            Project(
                name="E-commerce Platform",
                description="Full-stack e-commerce application with React frontend and Django backend",
                technologies=["React", "Django", "PostgreSQL", "Redis"],
                url="github.com/sarahjohnson/ecommerce"
            )
        ],
        certifications=["AWS Certified Developer", "Certified Scrum Master"]
    )


def create_sample_job_posting():
    """Create sample job posting for testing."""
    return JobPosting(
        title="Senior Full Stack Developer",
        company="InnovateTech Solutions",
        location="San Francisco, CA",
        description="""We are seeking a Senior Full Stack Developer to join our growing engineering team. 
        
        Responsibilities:
        - Design and develop scalable web applications
        - Lead technical decision making for new features
        - Mentor junior developers and conduct code reviews
        - Collaborate with product and design teams
        - Implement best practices for testing and deployment
        
        Requirements:
        - 5+ years of experience in full-stack development
        - Strong expertise in JavaScript, Python, and React
        - Experience with cloud platforms (AWS preferred)
        - Knowledge of microservices architecture
        - Strong communication and leadership skills
        - Experience with agile development methodologies
        
        Nice to have:
        - Experience with GraphQL and modern state management
        - DevOps experience with Docker and Kubernetes
        - Previous mentoring or team lead experience""",
        posted_date="2024-01-15",
        job_url="https://innovatetech.com/careers/senior-fullstack",
        skills_required=["JavaScript", "Python",
                         "React", "AWS", "Microservices"],
        experience_level="Senior",
        job_type="Full-time",
        salary_range="$120,000 - $160,000"
    )


def create_sample_company_info():
    """Create sample company info for testing."""
    return CompanyInfo(
        name="InnovateTech Solutions",
        website="https://innovatetech.com",
        industry="Technology",
        size="50-200 employees",
        description="Leading provider of innovative software solutions for enterprise clients. We focus on scalable, maintainable code and collaborative development.",
        mission="To democratize technology and make complex software solutions accessible to businesses of all sizes.",
        values=["Innovation", "Collaboration",
                "Quality", "Growth", "Transparency"],
        culture_keywords=["remote-friendly", "learning",
                          "mentorship", "agile", "work-life balance"],
        recent_news=["Raised Series B funding",
                     "Launched new AI platform", "Expanded to European market"],
        key_people=["Jane Smith"]
    )


def test_cover_letter_generation():
    """Test basic cover letter generation."""
    print("=" * 60)
    print("Testing Cover Letter Generation")
    print("=" * 60)

    generator = CoverLetterGeneratorTool()
    resume_data = create_sample_resume_data()
    job_posting = create_sample_job_posting()
    company_info = create_sample_company_info()

    result = generator.execute(
        operation="generate_cover_letter",
        resume_data=resume_data,
        job_posting=job_posting,
        company_info=company_info,
        template_style="auto",
        length="standard"
    )

    print(f"Success: {result['success']}")
    if result['success']:
        print(f"Template used: {result['result']['template_used']['name']}")
        print(
            f"Personalization score: {result['result']['personalization_score']:.2f}")
        print(f"Word count: {result['result']['content']['word_count']}")
        print("\nGenerated Cover Letter:")
        print("-" * 40)
        print(result['cover_letter'])
        print("-" * 40)
        print("\nSummary:")
        print(result['summary'])
    else:
        print(f"Error: {result['error']}")

    return result['success']


def test_template_selection():
    """Test automatic template selection."""
    print("\n" + "=" * 60)
    print("Testing Template Selection")
    print("=" * 60)

    generator = CoverLetterGeneratorTool()
    resume_data = create_sample_resume_data()
    company_info = create_sample_company_info()

    # Test different job types
    job_types = [
        ("Technical Lead", "technical"),
        ("Creative Director", "creative"),
        ("VP of Engineering", "executive"),
        ("Software Developer", "professional")
    ]

    for job_title, expected_style in job_types:
        job_posting = create_sample_job_posting()
        job_posting.title = job_title

        result = generator.execute(
            operation="generate_cover_letter",
            resume_data=resume_data,
            job_posting=job_posting,
            company_info=company_info,
            template_style="auto"
        )

        if result['success']:
            actual_style = result['result']['template_used']['style']
            print(
                f"{job_title}: {actual_style} template (expected: {expected_style})")
        else:
            print(f"{job_title}: Error - {result['error']}")

    return True


def test_different_templates():
    """Test different template styles."""
    print("\n" + "=" * 60)
    print("Testing Different Template Styles")
    print("=" * 60)

    generator = CoverLetterGeneratorTool()
    resume_data = create_sample_resume_data()
    job_posting = create_sample_job_posting()
    company_info = create_sample_company_info()

    templates = ["professional", "technical", "creative", "executive"]

    for template_style in templates:
        print(f"\nTesting {template_style} template:")
        result = generator.execute(
            operation="generate_cover_letter",
            resume_data=resume_data,
            job_posting=job_posting,
            company_info=company_info,
            template_style=template_style
        )

        if result['success']:
            content = result['result']['content']
            print(f"  Word count: {content['word_count']}")
            print(f"  Key points: {len(content['key_points_covered'])}")
            print(
                f"  Personalization score: {result['result']['personalization_score']:.2f}")
        else:
            print(f"  Error: {result['error']}")

    return True


def test_without_company_info():
    """Test cover letter generation without company research."""
    print("\n" + "=" * 60)
    print("Testing Without Company Info")
    print("=" * 60)

    generator = CoverLetterGeneratorTool()
    resume_data = create_sample_resume_data()
    job_posting = create_sample_job_posting()

    result = generator.execute(
        operation="generate_cover_letter",
        resume_data=resume_data,
        job_posting=job_posting,
        template_style="professional"
    )

    print(f"Success: {result['success']}")
    if result['success']:
        print(
            f"Personalization score: {result['result']['personalization_score']:.2f}")
        print("Generated cover letter without company info successfully")
    else:
        print(f"Error: {result['error']}")

    return result['success']


def test_analyze_requirements():
    """Test requirement analysis operation."""
    print("\n" + "=" * 60)
    print("Testing Requirement Analysis")
    print("=" * 60)

    generator = CoverLetterGeneratorTool()
    resume_data = create_sample_resume_data()
    job_posting = create_sample_job_posting()

    result = generator.execute(
        operation="analyze_requirements",
        resume_data=resume_data,
        job_posting=job_posting
    )

    print(f"Success: {result['success']}")
    if result['success']:
        analysis = result['analysis']
        print(f"Recommended template: {analysis['recommended_template']}")
        print(f"Key focus areas: {analysis['focus_areas']}")
        print(f"Skills to highlight: {analysis['key_skills_to_highlight']}")
        print(
            f"Tone recommendations: {analysis.get('tone_recommendations', 'N/A')}")
        print(
            f"Length recommendation: {analysis.get('length_recommendation', 'N/A')}")
    else:
        print(f"Error: {result['error']}")

    return result['success']


def test_edge_cases():
    """Test edge cases and error handling."""
    print("\n" + "=" * 60)
    print("Testing Edge Cases")
    print("=" * 60)

    generator = CoverLetterGeneratorTool()

    # Test with missing required parameters
    print("Testing missing parameters:")
    result = generator.execute(operation="generate_cover_letter")
    print(
        f"  Missing params: {'Success' if not result['success'] else 'Failed'}")

    # Test with minimal data
    print("Testing minimal data:")
    minimal_resume = ResumeData(
        contact_info=ContactInfo(name="John Doe", email="john@email.com"),
        skills=["Python"],
        experience=[],
        education=[]
    )
    minimal_job = JobPosting(
        title="Developer",
        company="Company",
        description="Basic job"
    )

    result = generator.execute(
        operation="generate_cover_letter",
        resume_data=minimal_resume,
        job_posting=minimal_job
    )
    print(f"  Minimal data: {'Success' if result['success'] else 'Failed'}")

    # Test invalid operation
    print("Testing invalid operation:")
    result = generator.execute(operation="invalid_operation")
    print(
        f"  Invalid operation: {'Success' if not result['success'] else 'Failed'}")

    return True


def main():
    """Run all tests."""
    print("Cover Letter Generator Tool Tests")
    print("=" * 60)

    tests = [
        ("Basic Generation", test_cover_letter_generation),
        ("Template Selection", test_template_selection),
        ("Different Templates", test_different_templates),
        ("Without Company Info", test_without_company_info),
        ("Requirement Analysis", test_analyze_requirements),
        ("Edge Cases", test_edge_cases)
    ]

    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
            print(f"\n✓ {test_name}: {'PASSED' if result else 'FAILED'}")
        except Exception as e:
            results.append((test_name, False))
            print(f"\n✗ {test_name}: FAILED - {str(e)}")

    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
        status = "PASS" if result else "FAIL"
        print(f"{status:4} | {test_name}")

    print(f"\nTotal: {passed}/{total} tests passed")

    if passed == total:
        print("🎉 All tests passed!")
        return True
    else:
        print(f"❌ {total - passed} tests failed")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
