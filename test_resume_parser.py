#!/usr/bin/env python3
"""Test script for resume parser functionality."""

from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from pathlib import Path
import tempfile
from tools.job_automation.resume_parser import ResumeParserTool
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))


# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))


def create_sample_resume_pdf():
    """Create a sample PDF resume for testing."""
    temp_dir = Path(tempfile.mkdtemp())
    pdf_path = temp_dir / "sample_resume.pdf"

    # Create a simple PDF with resume content
    c = canvas.Canvas(str(pdf_path), pagesize=letter)
    width, height = letter

    # Resume content
    y_position = height - 50
    line_height = 20

    resume_content = [
        "John Doe",
        "john.doe@email.com",
        "(555) 123-4567",
        "linkedin.com/in/johndoe",
        "github.com/johndoe",
        "",
        "PROFESSIONAL SUMMARY",
        "Experienced software engineer with 5+ years in web development",
        "and cloud technologies. Passionate about building scalable applications.",
        "",
        "TECHNICAL SKILLS",
        "Programming Languages: Python, JavaScript, Java, TypeScript",
        "Frameworks: React, Django, Flask, Node.js, Express",
        "Databases: PostgreSQL, MongoDB, Redis",
        "Cloud: AWS, Docker, Kubernetes",
        "Tools: Git, Jenkins, Terraform",
        "",
        "WORK EXPERIENCE",
        "Senior Software Engineer",
        "Tech Company Inc. (2020-Present)",
        "• Led development of microservices architecture using Python and AWS",
        "• Implemented React frontend applications serving 100k+ users",
        "• Optimized database queries reducing response time by 40%",
        "",
        "Software Developer",
        "StartupXYZ (2018-2020)",
        "• Built REST APIs using Django and PostgreSQL",
        "• Developed automated testing frameworks",
        "",
        "EDUCATION",
        "Bachelor of Science in Computer Science",
        "University of Technology, 2018",
        "",
        "PROJECTS",
        "E-commerce Platform",
        "• Built full-stack application using React and Node.js",
        "• Integrated payment processing and inventory management",
        "",
        "CERTIFICATIONS",
        "AWS Certified Solutions Architect",
        "Certified Kubernetes Administrator"
    ]

    for line in resume_content:
        if y_position < 50:  # Start new page if needed
            c.showPage()
            y_position = height - 50

        c.drawString(50, y_position, line)
        y_position -= line_height

    c.save()
    return temp_dir, str(pdf_path)


def test_resume_parser_schema():
    """Test that the resume parser schema is correct."""
    print("🧪 Testing Resume Parser Schema...")

    tool = ResumeParserTool()
    schema = tool.get_schema()

    # Check required fields
    assert "operation" in schema["properties"], "Operation property missing"
    assert "file_path" in schema["properties"], "File path property missing"
    assert "parse" in schema["properties"]["operation"]["enum"], "Parse operation missing"

    print("✅ Schema validation passed!")


def test_full_resume_parsing():
    """Test complete resume parsing functionality."""
    print("🧪 Testing Full Resume Parsing...")

    tool = ResumeParserTool()
    temp_dir, pdf_path = create_sample_resume_pdf()

    try:
        # Test full parsing
        result = tool.execute(operation="parse", file_path=pdf_path)
        print(f"Parse result:\\n{result}")

        # Check that we got results
        assert "Resume Parsing Results" in result, "Missing parsing results header"
        assert "Contact Information" in result, "Missing contact information"
        assert "john.doe@email.com" in result, "Missing email address"
        assert "Technical Skills" in result, "Missing skills section"
        assert "Python" in result, "Missing Python skill"

        print("✅ Full resume parsing test passed!")

    finally:
        # Cleanup
        import shutil
        shutil.rmtree(temp_dir)


def test_skills_extraction():
    """Test skills-only extraction."""
    print("🧪 Testing Skills Extraction...")

    tool = ResumeParserTool()
    temp_dir, pdf_path = create_sample_resume_pdf()

    try:
        result = tool.execute(operation="extract_skills", file_path=pdf_path)
        print(f"Skills extraction result:\\n{result}")

        # Check for expected skills
        assert "Python" in result, "Missing Python skill"
        assert "JavaScript" in result, "Missing JavaScript skill"
        assert "React" in result, "Missing React skill"

        print("✅ Skills extraction test passed!")

    finally:
        import shutil
        shutil.rmtree(temp_dir)


def test_contact_extraction():
    """Test contact information extraction."""
    print("🧪 Testing Contact Extraction...")

    tool = ResumeParserTool()
    temp_dir, pdf_path = create_sample_resume_pdf()

    try:
        result = tool.execute(operation="extract_contact", file_path=pdf_path)
        print(f"Contact extraction result:\\n{result}")

        # Check for expected contact info
        assert "john.doe@email.com" in result, "Missing email"
        assert "(555) 123-4567" in result, "Missing phone"
        assert "linkedin.com/in/johndoe" in result, "Missing LinkedIn"

        print("✅ Contact extraction test passed!")

    finally:
        import shutil
        shutil.rmtree(temp_dir)


def test_error_handling():
    """Test error handling for invalid files."""
    print("🧪 Testing Error Handling...")

    tool = ResumeParserTool()

    # Test with non-existent file
    result = tool.execute(
        operation="parse", file_path="/non/existent/file.pdf")
    assert "Error" in result, "Should return error for non-existent file"

    print("✅ Error handling test passed!")


def main():
    """Run all tests."""
    print("🚀 Starting Resume Parser Tests...")
    print("=" * 50)

    try:
        test_resume_parser_schema()
        test_full_resume_parsing()
        test_skills_extraction()
        test_contact_extraction()
        test_error_handling()

        print("=" * 50)
        print("🎉 All resume parser tests passed!")

    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
