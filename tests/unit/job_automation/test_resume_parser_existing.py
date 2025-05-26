"""Tests for job automation tools - Resume Parser (Fixed)."""

import pytest
import tempfile
from pathlib import Path
from unittest.mock import patch, mock_open

from src.tools.job_automation.resume_parser import ResumeParserTool, ResumeData, ContactInfo


@pytest.mark.job_automation
@pytest.mark.unit
class TestResumeParser:
    """Test suite for Resume Parser functionality."""

    def test_initialization(self):
        """Test resume parser tool initialization."""
        parser = ResumeParserTool()
        assert parser.name == "resume_parser"
        assert "parse pdf resumes" in parser.description.lower()

    def test_schema_validation(self):
        """Test that the resume parser schema is valid."""
        parser = ResumeParserTool()
        schema = parser.get_schema()

        assert "properties" in schema
        assert "operation" in schema["properties"]
        assert "file_path" in schema["properties"]

        # Check operations
        operations = schema["properties"]["operation"]["enum"]
        assert "parse" in operations
        assert "extract_skills" in operations
        assert "extract_contact" in operations

    def test_contact_info_extraction(self):
        """Test contact information extraction from text."""
        parser = ResumeParserTool()

        sample_text = """
        John Doe
        Software Engineer
        Email: john.doe@example.com
        Phone: (555) 123-4567
        LinkedIn: linkedin.com/in/johndoe
        GitHub: github.com/johndoe
        San Francisco, CA
        """

        contact = parser._extract_contact_info(sample_text)

        assert contact.name == "John Doe"
        assert contact.email == "john.doe@example.com"
        assert contact.phone == "(555) 123-4567"
        assert "linkedin.com/in/johndoe" in contact.linkedin
        assert "github.com/johndoe" in contact.github

    def test_skills_extraction(self):
        """Test skills extraction from resume text."""
        parser = ResumeParserTool()

        sample_text = """
        TECHNICAL SKILLS
        Programming Languages: Python, JavaScript, Java, C++
        Web Frameworks: Django, React, Angular, Flask
        Databases: PostgreSQL, MongoDB, MySQL
        Cloud Platforms: AWS, Google Cloud, Azure
        Tools: Docker, Kubernetes, Git, Jenkins
        """

        skills = parser._extract_skills(sample_text)

        # Check that common skills are extracted
        assert "Python" in skills
        assert "JavaScript" in skills
        assert "Django" in skills
        assert "React" in skills
        assert "PostgreSQL" in skills
        assert "AWS" in skills
        assert "Docker" in skills

    def test_certifications_extraction(self):
        """Test certifications extraction."""
        parser = ResumeParserTool()

        sample_text = """
        CERTIFICATIONS
        
        • AWS Certified Developer - Associate (2023)
        • Docker Certified Associate (2022)
        • Certified Kubernetes Administrator (2021)
        """

        certifications = parser._extract_certifications(sample_text)

        assert len(certifications) >= 1
        assert any("AWS" in cert for cert in certifications)

    @patch('pathlib.Path.exists')
    @patch('pdfplumber.open')
    def test_pdf_text_extraction_pdfplumber(self, mock_pdfplumber, mock_exists):
        """Test PDF text extraction using pdfplumber."""
        parser = ResumeParserTool()

        # Mock file existence and PDF suffix
        mock_exists.return_value = True

        # Mock pdfplumber
        mock_page = type('MockPage', (), {
                         'extract_text': lambda self: "Sample resume text"})()
        mock_pdf = type('MockPDF', (), {
            'pages': [mock_page],
            '__enter__': lambda self: self,
            '__exit__': lambda self, *args: None
        })()
        mock_pdfplumber.return_value = mock_pdf

        text = parser._extract_text_from_pdf("fake_path.pdf")
        assert text == "Sample resume text\n"

    def test_file_not_found_error(self):
        """Test handling of non-existent files."""
        parser = ResumeParserTool()

        result = parser.execute(
            operation="parse", file_path="/nonexistent/file.pdf")
        assert "Error" in result
        assert "not found" in result.lower()

    def test_invalid_operation(self):
        """Test handling of invalid operations."""
        parser = ResumeParserTool()

        result = parser.execute(
            operation="invalid_operation", file_path="test.pdf")
        assert "Error" in result or "Unknown operation" in result

    def test_resume_data_formatting(self, sample_resume_data):
        """Test resume data formatting for display."""
        parser = ResumeParserTool()

        formatted = parser._format_resume_summary(sample_resume_data)

        assert "John Doe" in formatted
        assert "john.doe@email.com" in formatted
        assert "Python" in formatted
        assert "Senior Software Engineer" in formatted
        assert "Bachelor of Science" in formatted

    @pytest.fixture
    def sample_test_pdf(self):
        """Create a temporary PDF file for testing."""
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as temp_file:
            temp_file.write(b"Sample PDF content")
            yield Path(temp_file.name)

    def test_extract_skills_only_operation(self, sample_test_pdf):
        """Test extract skills only operation."""
        parser = ResumeParserTool()

        # Mock the text extraction to return skills text
        with patch.object(parser, '_extract_text_from_pdf', return_value="Python JavaScript React Django"):
            result = parser.execute(
                operation="extract_skills", file_path=str(sample_test_pdf))

        assert "Extracted Skills" in result
        assert "Python" in result

    def test_extract_contact_only_operation(self, sample_test_pdf):
        """Test extract contact only operation."""
        parser = ResumeParserTool()

        contact_text = """
        John Doe
        john.doe@example.com
        (555) 123-4567
        San Francisco, CA
        """

        with patch.object(parser, '_extract_text_from_pdf', return_value=contact_text):
            result = parser.execute(
                operation="extract_contact", file_path=str(sample_test_pdf))

        assert "Contact Information" in result
        assert "John Doe" in result
        assert "john.doe@example.com" in result
