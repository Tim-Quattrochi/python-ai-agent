"""Test script for the Job Application Orchestrator."""

from src.tools.job_automation.application_orchestrator import (
    JobApplicationOrchestrator, ApplicationConfig
)
import sys
import os
import tempfile
from datetime import datetime


sys.path.append('.')


def create_sample_resume_file():
    """Create a sample resume PDF file for testing."""
    from reportlab.lib.pagesizes import letter
    from reportlab.pdfgen import canvas

    resume_content = [
        "John Smith",
        "Email: john.smith@email.com",
        "Phone: (555) 123-4567",
        "Location: San Francisco, CA",
        "",
        "PROFESSIONAL SUMMARY",
        "Experienced software engineer with 5 years of full-stack development experience.",
        "Specializes in Python, JavaScript, and cloud technologies. Strong background in",
        "building scalable web applications and leading development teams.",
        "",
        "SKILLS",
        "Python, JavaScript, React, Django, AWS, Docker, PostgreSQL, Git, Agile",
        "",
        "EXPERIENCE",
        "",
        "Senior Software Engineer - TechCorp Inc (2022-Present)",
        "• Led development of microservices architecture serving 100K+ daily users",
        "• Implemented CI/CD pipelines reducing deployment time by 60%",
        "• Mentored junior developers and conducted code reviews",
        "• Technologies: Python, Django, AWS, Docker, PostgreSQL",
        "",
        "Software Engineer - StartupXYZ (2019-2022)",
        "• Built responsive web applications using React and Node.js",
        "• Designed and implemented RESTful APIs",
        "• Collaborated with product team to define technical requirements",
        "• Technologies: JavaScript, React, Node.js, MongoDB",
        "",
        "Junior Developer - DevCorp (2019-2019)",
        "• Developed features for e-commerce platform",
        "• Fixed bugs and improved application performance",
        "• Technologies: Python, Flask, MySQL",
        "",
        "EDUCATION",
        "B.S. Computer Science - University of California, Berkeley (2019)",
        "GPA: 3.7/4.0",
        "",
        "PROJECTS",
        "• Personal Finance Tracker - Full-stack web app with React frontend and Django backend",
        "• Task Management API - RESTful API built with FastAPI and PostgreSQL",
        "• Machine Learning Stock Predictor - Python application using scikit-learn",
        "",
        "CERTIFICATIONS",
        "• AWS Certified Developer Associate (2023)",
        "• Certified Scrum Master (2022)"
    ]

    # Create temporary PDF file
    temp_file = tempfile.NamedTemporaryFile(suffix='.pdf', delete=False)
    temp_file.close()

    # Create PDF
    c = canvas.Canvas(temp_file.name, pagesize=letter)
    width, height = letter

    y_position = height - 50
    line_height = 15

    for line in resume_content:
        if y_position < 50:  # Start new page if needed
            c.showPage()
            y_position = height - 50

        c.drawString(50, y_position, line)
        y_position -= line_height

    c.save()
    return temp_file.name


def test_configuration_validation():
    """Test configuration validation."""
    print("1. Testing configuration validation...")

    orchestrator = JobApplicationOrchestrator()

    # Create test resume file
    resume_file = create_sample_resume_file()

    try:
        # Test valid configuration
        config = {
            "resume_file_path": resume_file,
            "applicant_email": "john.smith@email.com",
            "applicant_name": "John Smith",
            "keywords": "Python developer",
            "location": "San Francisco",
            "max_applications": 3,
            "min_match_score": 0.6,
            "auto_send_emails": False,
            "output_directory": "./test_applications",
            "email_host": "smtp.gmail.com",
            "email_username": "test@email.com",
            "email_password": "test_password"
        }

        result = orchestrator.execute(
            operation="test_configuration",
            config=config
        )

        print(f"   Configuration test success: {result['success']}")
        print(f"   Tests results:")
        for test_name, passed, message in result['tests']:
            status = "PASS" if passed else "FAIL"
            print(f"      {status}: {test_name} - {message}")

        return result['success']

    finally:
        # Clean up
        if os.path.exists(resume_file):
            os.unlink(resume_file)


def test_preview_mode():
    """Test preview mode (dry run)."""
    print("\n2. Testing preview mode...")

    orchestrator = JobApplicationOrchestrator()

    # Create test resume file
    resume_file = create_sample_resume_file()

    try:
        config = {
            "resume_file_path": resume_file,
            "applicant_email": "john.smith@email.com",
            "applicant_name": "John Smith",
            "keywords": "Python software engineer",
            "location": "San Francisco",
            "max_applications": 2,
            "min_match_score": 0.5,
            "auto_send_emails": False,
            "output_directory": "./test_applications",
            "template_style": "technical",
            "delay_between_applications": 1,
            "email_host": "smtp.gmail.com",
            "email_username": "test@email.com",
            "email_password": "test_password"
        }

        result = orchestrator.execute(
            operation="preview_applications",
            config=config,
            dry_run=True
        )

        print(f"   Preview success: {result['success']}")
        if result['success']:
            summary = result['summary']
            print(f"   Jobs found: {summary['total_jobs_found']}")
            print(
                f"   Jobs above threshold: {summary['jobs_above_threshold']}")
            print(
                f"   Applications processed: {summary['applications_attempted']}")
            print(f"   Time taken: {summary['total_time_taken']:.1f} seconds")

            if summary['results']:
                print(f"   Sample applications:")
                for i, app_result in enumerate(summary['results'][:2]):
                    job = app_result['job_posting']
                    print(
                        f"      {i+1}. {job['title']} at {job['company']} (Score: {app_result['match_score']:.2f})")
        else:
            print(f"   Error: {result['error']}")
            if 'summary' in result and result['summary']['errors']:
                print(f"   Detailed errors: {result['summary']['errors']}")

        return result['success']

    finally:
        # Clean up
        if os.path.exists(resume_file):
            os.unlink(resume_file)

        # Clean up test output directory
        if os.path.exists("./test_applications"):
            import shutil
            shutil.rmtree("./test_applications")


def test_error_handling():
    """Test error handling with invalid configuration."""
    print("\n3. Testing error handling...")

    orchestrator = JobApplicationOrchestrator()

    # Test with missing resume file
    config = {
        "resume_file_path": "nonexistent_file.txt",
        "applicant_email": "test@email.com",
        "applicant_name": "Test User",
        "keywords": "developer",
        "location": "Remote",
        "max_applications": 1
    }

    result = orchestrator.execute(
        operation="run_application_process",
        config=config,
        dry_run=True
    )

    # Should fail
    print(f"   Error handling test success: {not result['success']}")
    if not result['success']:
        print(f"   Expected error caught: {result['error']}")
        return True
    else:
        print("   Unexpected success - should have failed with missing file")
        return False


def test_minimal_workflow():
    """Test minimal workflow without external dependencies."""
    print("\n4. Testing minimal workflow...")

    orchestrator = JobApplicationOrchestrator()

    # Create test resume file
    resume_file = create_sample_resume_file()

    try:
        config = {
            "resume_file_path": resume_file,
            "applicant_email": "john.smith@email.com",
            "applicant_name": "John Smith",
            "keywords": "Python",
            "location": "Remote",
            "max_applications": 1,
            "min_match_score": 0.3,  # Lower threshold for testing
            "auto_send_emails": False,
            "output_directory": "./test_minimal",
            "delay_between_applications": 1,
            "email_host": "smtp.gmail.com",
            "email_username": "test@email.com",
            "email_password": "test_password"
        }

        # Test just the resume parsing part
        resume_result = orchestrator._parse_resume(
            orchestrator._parse_config(config))

        print(f"   Resume parsing: {resume_result['success']}")
        if resume_result['success']:
            resume_data = resume_result['resume_data']
            print(f"   Parsed name: {resume_data.contact_info.name}")
            print(f"   Skills count: {len(resume_data.skills)}")
            print(f"   Experience count: {len(resume_data.experience)}")
            return True
        else:
            print(f"   Resume parsing error: {resume_result['error']}")
            return False

    finally:
        # Clean up
        if os.path.exists(resume_file):
            os.unlink(resume_file)


def test_orchestrator_instantiation():
    """Test basic orchestrator instantiation."""
    print("\n5. Testing orchestrator instantiation...")

    try:
        orchestrator = JobApplicationOrchestrator()
        print(f"   Tool name: {orchestrator.name}")
        print(f"   Tool description: {orchestrator.description}")

        # Test schema
        schema = orchestrator.get_schema()
        print(f"   Schema properties: {list(schema['properties'].keys())}")

        return True

    except Exception as e:
        print(f"   Instantiation error: {str(e)}")
        return False


def main():
    """Run all orchestrator tests."""
    print("=== Job Application Orchestrator Tests ===\n")

    try:
        results = []

        # Run tests
        results.append(("Orchestrator Instantiation",
                       test_orchestrator_instantiation()))
        results.append(("Configuration Validation",
                       test_configuration_validation()))
        results.append(("Minimal Workflow", test_minimal_workflow()))
        results.append(("Error Handling", test_error_handling()))

        # Note: Preview mode test is commented out as it requires external services
        # results.append(("Preview Mode", test_preview_mode()))

        print("\n=== Test Results ===")
        passed = 0
        for test_name, result in results:
            status = "PASS" if result else "FAIL"
            print(f"{status:4} | {test_name}")
            if result:
                passed += 1

        print(f"\nSummary: {passed}/{len(results)} tests passed")

        if passed == len(results):
            print("🎉 All orchestrator tests passed!")
            print("\n📋 Next Steps:")
            print("   1. Configure email settings for live applications")
            print("   2. Test with real job sites (LinkedIn, Indeed, etc.)")
            print("   3. Set up production resume and preferences")
            print("   4. Run preview mode before live automation")
        else:
            print(f"❌ {len(results) - passed} tests failed")

        return passed == len(results)

    except Exception as e:
        print(f"\nTest suite failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    main()
