#!/usr/bin/env python3
"""
Email Configuration Test Script
This script tests the email functionality to ensure SMTP settings are working correctly.
"""

from tools.email_sender import EmailSenderTool
import os
import sys
from dotenv import load_dotenv

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))


def test_email_configuration():
    """Test email configuration and send a test email."""

    # Load environment variables
    load_dotenv()

    # Check if required environment variables are set
    required_vars = ['SMTP_HOST', 'SMTP_PORT',
                     'SMTP_USER', 'SMTP_PASSWORD', 'FROM_EMAIL']
    missing_vars = []

    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)

    if missing_vars:
        print(f"❌ Missing environment variables: {', '.join(missing_vars)}")
        print("Please check your .env file")
        return False

    print("✅ All environment variables found")

    # Initialize email sender
    try:
        email_tool = EmailSenderTool()
        print("✅ Email sender initialized successfully")
    except Exception as e:
        print(f"❌ Failed to initialize email sender: {e}")
        return False

    # Test email configuration (this will attempt to connect to SMTP server)
    print("\n🔧 Testing SMTP connection...")

    # Send a test email
    try:
        result = email_tool.execute({
            "to": os.getenv('SMTP_USER'),  # Send to yourself
            "subject": "🧪 AI Agent Email Test",
            "body": """
Hello! 👋

This is a test email from your Python AI Agent to verify that email functionality is working correctly.

✅ SMTP Configuration: Working
✅ Authentication: Successful
✅ Email Delivery: Success

Your AI Agent is ready to send emails!

Best regards,
Your Python AI Agent 🤖
            """.strip()
        })

        if result.get("status") == "success":
            print("✅ Test email sent successfully!")
            print(f"📧 Email sent to: {os.getenv('SMTP_USER')}")
            print("\nPlease check your inbox to confirm delivery.")
            return True
        else:
            print(
                f"❌ Email sending failed: {result.get('message', 'Unknown error')}")
            return False

    except Exception as e:
        print(f"❌ Email test failed: {e}")
        return False


def main():
    print("🧪 AI Agent Email Configuration Test")
    print("=" * 40)

    success = test_email_configuration()

    print("\n" + "=" * 40)
    if success:
        print("🎉 Email configuration test PASSED!")
        print("Your AI Agent email functionality is working correctly.")
    else:
        print("💥 Email configuration test FAILED!")
        print("Please check your .env file and SMTP settings.")

    return success


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
