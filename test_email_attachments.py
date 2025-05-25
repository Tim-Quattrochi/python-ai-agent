#!/usr/bin/env python3
"""Test script for email attachment functionality."""

import os
import sys
import tempfile
from pathlib import Path

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from tools.email_sender import EmailSenderTool


def create_test_files():
    """Create temporary test files for attachment testing."""
    temp_dir = Path(tempfile.mkdtemp())
    
    # Create a test PDF file (simple text content)
    pdf_file = temp_dir / "test_resume.pdf"
    with open(pdf_file, 'w') as f:
        f.write("This is a test PDF file for attachment testing.")
    
    # Create a test text file
    txt_file = temp_dir / "test_cover_letter.txt"
    with open(txt_file, 'w') as f:
        f.write("This is a test cover letter for attachment testing.")
    
    return temp_dir, [str(pdf_file), str(txt_file)]


def test_email_tool_schema():
    """Test that the email tool schema includes attachment support."""
    print("🧪 Testing Email Tool Schema...")
    
    tool = EmailSenderTool()
    schema = tool.get_schema()
    
    # Check that attachments is in the schema
    assert "attachments" in schema["properties"], "Attachments property missing from schema"
    assert schema["properties"]["attachments"]["type"] == "array", "Attachments should be array type"
    
    print("✅ Schema validation passed!")


def test_draft_with_attachments():
    """Test saving and listing drafts with attachments."""
    print("🧪 Testing Draft with Attachments...")
    
    tool = EmailSenderTool()
    temp_dir, test_files = create_test_files()
    
    try:
        # Test saving draft with attachments
        result = tool.execute(
            operation="draft",
            to="test@example.com",
            subject="Test Job Application",
            body="Please find my resume and cover letter attached.",
            attachments=test_files
        )
        
        print(f"Draft creation result: {result}")
        assert "Draft saved!" in result, "Draft saving failed"
        
        # Test listing drafts
        result = tool.execute(operation="list_drafts")
        print(f"Draft listing result: {result}")
        assert "test@example.com" in result, "Draft not found in listing"
        
        print("✅ Draft with attachments test passed!")
        
    finally:
        # Cleanup
        import shutil
        shutil.rmtree(temp_dir)


def test_attachment_validation():
    """Test attachment file validation."""
    print("🧪 Testing Attachment Validation...")
    
    tool = EmailSenderTool()
    
    # Test with non-existent file
    from email.mime.multipart import MIMEMultipart
    msg = MIMEMultipart()
    
    result = tool._add_attachment(msg, "/non/existent/file.pdf")
    assert result is False, "Should fail for non-existent file"
    
    # Test with valid file
    temp_dir, test_files = create_test_files()
    try:
        result = tool._add_attachment(msg, test_files[0])
        assert result is True, "Should succeed for valid file"
        
        print("✅ Attachment validation test passed!")
        
    finally:
        import shutil
        shutil.rmtree(temp_dir)


def main():
    """Run all tests."""
    print("🚀 Starting Email Attachment Tests...")
    print("=" * 50)
    
    try:
        test_email_tool_schema()
        test_draft_with_attachments()
        test_attachment_validation()
        
        print("=" * 50)
        print("🎉 All tests passed! Email attachment functionality is working.")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
