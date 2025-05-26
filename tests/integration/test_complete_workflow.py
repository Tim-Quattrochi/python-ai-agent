#!/usr/bin/env python3
"""Complete end-to-end test of the job automation system."""

from src.tools.job_automation import (
    JobApplicationOrchestrator, ApplicationConfig,
    ResumeParserTool, JobScraperTool, JobMatcherTool,
    ResumeCustomizerTool, CompanyResearchTool, CoverLetterGeneratorTool
)
import sys
import os
import tempfile
from pathlib import Path

# Add the src directory to the path
sys.path.append('.')


def create_comprehensive_test_resume():
    """Create a comprehensive test resume PDF."""
    from reportlab.lib.pagesizes import letter
    from reportlab.pdfgen import canvas

    resume_content = [
        "Sarah Johnson",
        "Email: sarah.johnson@email.com",
        "Phone: (555) 987-6543",
        "Location: Seattle, WA",
        "LinkedIn: linkedin.com/in/sarahjohnson",
        "GitHub: github.com/sarahjohnson",
        "",
        "PROFESSIONAL SUMMARY",
        "Senior Full-Stack Developer with 7+ years of experience building scalable web",
        "applications using Python, JavaScript, React, and cloud technologies. Proven track",
        "record of leading development teams and delivering high-impact solutions for",
        "enterprises and startups. Expert in microservices architecture, DevOps, and agile",
        "methodologies. Passionate about code quality, performance optimization, and",
        "mentoring junior developers.",
        "",
        "TECHNICAL SKILLS",
        "Languages: Python, JavaScript, TypeScript, Java, Go, SQL",
        "Frontend: React, Vue.js, Angular, HTML5, CSS3, SASS, Tailwind CSS",
        "Backend: Django, Flask, FastAPI, Node.js, Express, Spring Boot",
        "Databases: PostgreSQL, MongoDB, Redis, MySQL, Elasticsearch",
        "Cloud: AWS (EC2, S3, RDS, Lambda, ECS), Google Cloud, Azure",
        "DevOps: Docker, Kubernetes, Jenkins, GitLab CI, Terraform, Ansible",
        "Tools: Git, Jira, Confluence, Figma, Postman, VS Code",
        "",
        "WORK EXPERIENCE",
        "",
        "Senior Software Engineer - CloudTech Solutions (2021-Present)",
        "• Lead a team of 5 developers building microservices architecture for",
        "  e-commerce platform serving 1M+ users",
        "• Implemented CI/CD pipelines reducing deployment time from 2 hours to 15 minutes",
        "• Designed and built real-time analytics dashboard using React and WebSocket",
        "• Optimized database queries and API performance, reducing response time by 60%",
        "• Mentored 3 junior developers and conducted technical interviews",
        "• Technologies: Python, Django, React, PostgreSQL, AWS, Docker, Kubernetes",
        "",
        "Full-Stack Developer - InnovateLabs (2019-2021)",
        "• Developed SaaS platform for project management using MERN stack",
        "• Built REST APIs serving 50K+ requests/day with 99.9% uptime",
        "• Implemented OAuth2 authentication and role-based access control",
        "• Created automated testing framework covering 95% code coverage",
        "• Collaborated with UX team to improve user engagement by 40%",
        "• Technologies: JavaScript, React, Node.js, MongoDB, AWS Lambda",
        "",
        "Software Developer - StartupXYZ (2018-2019)",
        "• Built responsive web applications using React and Python Flask",
        "• Developed data visualization components using D3.js and Chart.js",
        "• Integrated third-party APIs including Stripe, Twilio, and SendGrid",
        "• Participated in agile development process with 2-week sprints",
        "• Technologies: Python, Flask, React, PostgreSQL, Redis",
        "",
        "Junior Developer - TechCorp (2017-2018)",
        "• Developed features for CRM system using Django and jQuery",
        "• Fixed bugs and performed code reviews",
        "• Gained experience with version control and deployment processes",
        "• Technologies: Python, Django, JavaScript, MySQL",
        "",
        "EDUCATION",
        "Master of Science in Computer Science",
        "University of Washington, Seattle (2017)",
        "GPA: 3.8/4.0",
        "Relevant Coursework: Algorithms, Databases, Software Engineering, Machine Learning",
        "",
        "Bachelor of Science in Computer Science",
        "University of California, San Diego (2015)",
        "GPA: 3.6/4.0, Magna Cum Laude",
        "",
        "PROJECTS",
        "",
        "Real-Time Chat Application (2023)",
        "• Built scalable chat app using WebSocket, Redis, and React",
        "• Supports 10K+ concurrent users with message persistence",
        "• Technologies: React, Node.js, Socket.io, Redis, MongoDB",
        "",
        "E-commerce Microservices Platform (2022)",
        "• Designed and implemented microservices architecture",
        "• Used Docker containers and Kubernetes orchestration",
        "• Technologies: Python, Django, PostgreSQL, Docker, Kubernetes, AWS",
        "",
        "Machine Learning Stock Predictor (2021)",
        "• Built ML model for stock price prediction using historical data",
        "• Achieved 85% accuracy using ensemble methods",
        "• Technologies: Python, scikit-learn, pandas, numpy, Flask",
        "",
        "CERTIFICATIONS",
        "• AWS Certified Solutions Architect – Associate (2023)",
        "• AWS Certified Developer – Associate (2022)",
        "• Certified Kubernetes Application Developer (2022)",
        "• Certified ScrumMaster (CSM) (2021)",
        "",
        "ACHIEVEMENTS",
        "• Led team that won company hackathon for best technical innovation (2023)",
        "• Reduced infrastructure costs by 40% through cloud optimization (2022)",
        "• Mentored 8 junior developers, 6 received promotions within 18 months",
        "• Speaker at Seattle Tech Meetup on 'Microservices Best Practices' (2023)"
    ]

    # Create temporary PDF file
    temp_file = tempfile.NamedTemporaryFile(suffix='.pdf', delete=False)
    temp_file.close()

    # Create PDF
    c = canvas.Canvas(temp_file.name, pagesize=letter)
    width, height = letter

    y_position = height - 40
    line_height = 12

    for line in resume_content:
        if y_position < 40:  # Start new page if needed
            c.showPage()
            y_position = height - 40

        c.drawString(40, y_position, line)
        y_position -= line_height

    c.save()
    return temp_file.name


def test_individual_tools():
    """Test each tool individually with the comprehensive resume."""
    print("🔧 Testing Individual Tools")
    print("=" * 60)

    resume_file = create_comprehensive_test_resume()

    try:
        # Test Resume Parser
        print("1. Testing Resume Parser...")
        parser = ResumeParserTool()
        result = parser.execute(operation="parse", file_path=resume_file)
        assert "Sarah Johnson" in result, "Resume parsing failed"
        assert "Technical Skills" in result or "skills" in result.lower(), "Skills extraction failed"
        print("   ✅ Resume parser working")

        # Test Job Scraper (mock test)
        print("2. Testing Job Scraper...")
        scraper = JobScraperTool()
        schema = scraper.get_schema()
        assert "operation" in schema["properties"], "Job scraper schema invalid"
        print("   ✅ Job scraper initialized")

        # Test Job Matcher
        print("3. Testing Job Matcher...")
        matcher = JobMatcherTool()
        schema = matcher.get_schema()
        assert "match_job" in schema["properties"]["operation"]["enum"], "Job matcher schema invalid"
        print("   ✅ Job matcher initialized")

        # Test Resume Customizer
        print("4. Testing Resume Customizer...")
        customizer = ResumeCustomizerTool()
        schema = customizer.get_schema()
        assert "customize_resume" in schema["properties"]["operation"]["enum"], "Customizer schema invalid"
        print("   ✅ Resume customizer initialized")

        # Test Company Research
        print("5. Testing Company Research...")
        researcher = CompanyResearchTool()
        schema = researcher.get_schema()
        assert "research_company" in schema["properties"]["operation"]["enum"], "Research schema invalid"
        print("   ✅ Company research initialized")

        # Test Cover Letter Generator
        print("6. Testing Cover Letter Generator...")
        generator = CoverLetterGeneratorTool()
        schema = generator.get_schema()
        assert "generate_cover_letter" in schema["properties"]["operation"]["enum"], "Generator schema invalid"
        print("   ✅ Cover letter generator initialized")

        print("   🎉 All individual tools working!")
        return True

    finally:
        if os.path.exists(resume_file):
            os.unlink(resume_file)


def test_complete_workflow():
    """Test the complete orchestrated workflow."""
    print("\n🚀 Testing Complete Workflow")
    print("=" * 60)

    resume_file = create_comprehensive_test_resume()

    try:
        orchestrator = JobApplicationOrchestrator()

        # Configuration for comprehensive test
        config = {
            "resume_file_path": resume_file,
            "applicant_email": "sarah.johnson@email.com",
            "applicant_name": "Sarah Johnson",
            "keywords": "Senior Python Developer",
            "location": "Seattle, WA",
            "max_applications": 2,
            "min_match_score": 0.7,
            "auto_send_emails": False,  # Don't actually send emails in test
            "output_directory": "./test_workflow_output",
            "template_style": "technical",
            "delay_between_applications": 1,  # Fast for testing
            "email_host": "smtp.gmail.com",
            "email_username": "test@email.com",
            "email_password": "test_password"
        }

        print("1. Testing Configuration Validation...")
        validation_result = orchestrator.execute(
            operation="test_configuration",
            config=config
        )

        if validation_result["success"]:
            print("   ✅ Configuration valid")
            for test_name, passed, message in validation_result["tests"]:
                status = "✅" if passed else "❌"
                print(f"   {status} {test_name}: {message}")
        else:
            print("   ❌ Configuration validation failed")
            return False

        print("\n2. Testing Resume Parsing in Orchestrator...")
        config_obj = orchestrator._parse_config(config)
        resume_result = orchestrator._parse_resume(config_obj)

        if resume_result["success"]:
            resume_data = resume_result["resume_data"]
            print(f"   ✅ Resume parsed: {resume_data.contact_info.name}")
            print(f"   📊 Skills found: {len(resume_data.skills)}")
            print(f"   💼 Experience entries: {len(resume_data.experience)}")
            print(f"   🎓 Education entries: {len(resume_data.education)}")
        else:
            print(f"   ❌ Resume parsing failed: {resume_result['error']}")
            return False

        print("\n3. Testing Preview Mode...")
        preview_result = orchestrator.execute(
            operation="preview_applications",
            config=config,
            dry_run=True
        )

        if preview_result["success"]:
            summary = preview_result["summary"]
            print(f"   ✅ Preview completed")
            print(f"   🔍 Jobs found: {summary['total_jobs_found']}")
            print(
                f"   🎯 Jobs above threshold: {summary['jobs_above_threshold']}")
            print(
                f"   📄 Applications processed: {summary['applications_attempted']}")
            print(f"   ⏱️ Time taken: {summary['total_time_taken']:.1f}s")

            if summary['results']:
                print(
                    f"   📝 Sample results: {len(summary['results'])} applications")
                for i, result in enumerate(summary['results'][:2], 1):
                    print(
                        f"      {i}. {result.job_posting.title} at {result.job_posting.company}")
                    print(f"         Match Score: {result.match_score:.1f}%")
        else:
            print(
                f"   ❌ Preview failed: {preview_result.get('error', 'Unknown error')}")
            return False

        print("\n   🎉 Complete workflow test successful!")
        return True

    finally:
        if os.path.exists(resume_file):
            os.unlink(resume_file)

        # Cleanup output directory
        import shutil
        output_dir = "./test_workflow_output"
        if os.path.exists(output_dir):
            shutil.rmtree(output_dir)


def test_error_scenarios():
    """Test error handling scenarios."""
    print("\n🛡️ Testing Error Scenarios")
    print("=" * 60)

    orchestrator = JobApplicationOrchestrator()

    # Test with invalid resume file
    print("1. Testing with invalid resume file...")
    config = {
        "resume_file_path": "/nonexistent/file.pdf",
        "applicant_email": "test@email.com",
        "applicant_name": "Test User",
        "keywords": "Developer",
        "location": "Remote",
        "email_host": "smtp.gmail.com",
        "email_username": "test@email.com",
        "email_password": "test_password"
    }

    result = orchestrator.execute(
        operation="test_configuration", config=config)

    found_error = False
    for test_name, passed, message in result["tests"]:
        if not passed and "file" in test_name.lower():
            print(f"   ✅ Correctly detected file error: {message}")
            found_error = True
            break

    if not found_error:
        print("   ❌ Failed to detect invalid file")
        return False

    # Test with missing email configuration
    print("2. Testing with missing email config...")
    config_no_email = {
        "resume_file_path": "test.pdf",
        "applicant_email": "test@email.com",
        "applicant_name": "Test User",
        "keywords": "Developer",
        "location": "Remote"
        # Missing email_host, email_username, email_password
    }

    result = orchestrator.execute(
        operation="test_configuration", config=config_no_email)

    found_email_error = False
    for test_name, passed, message in result["tests"]:
        if not passed and "email" in test_name.lower():
            print(f"   ✅ Correctly detected email config error: {message}")
            found_email_error = True
            break

    if not found_email_error:
        print("   ❌ Failed to detect missing email config")
        return False

    print("   🎉 Error handling tests passed!")
    return True


def main():
    """Run all comprehensive tests."""
    print("🔬 Job Automation System - Comprehensive Test Suite")
    print("=" * 80)

    test_results = []

    try:
        # Individual tools test
        result1 = test_individual_tools()
        test_results.append(("Individual Tools", result1))

        # Complete workflow test
        result2 = test_complete_workflow()
        test_results.append(("Complete Workflow", result2))

        # Error scenarios test
        result3 = test_error_scenarios()
        test_results.append(("Error Handling", result3))

        # Print summary
        print("\n📊 Test Summary")
        print("=" * 80)

        passed = 0
        for test_name, result in test_results:
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"{status} | {test_name}")
            if result:
                passed += 1

        total = len(test_results)
        print(f"\nResult: {passed}/{total} test suites passed")

        if passed == total:
            print("\n🎉 ALL TESTS PASSED! The job automation system is ready for use.")
            print("\n📋 Next Steps:")
            print("   1. Configure your real email settings")
            print("   2. Prepare your actual resume PDF")
            print("   3. Test with preview mode first")
            print("   4. Start automating your job applications!")
        else:
            print(
                f"\n❌ {total - passed} test suite(s) failed. Please fix issues before using.")
            sys.exit(1)

    except Exception as e:
        print(f"\n💥 Test suite failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
