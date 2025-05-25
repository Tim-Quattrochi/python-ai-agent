#!/usr/bin/env python3
"""Test script to verify email configuration."""

import os
import sys
import smtplib
from email.mime.text import MIMEText
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_email_config():
    """Test SMTP configuration without sending an email."""
    print("🧪 Testing Email Configuration")
    print("=" * 40)
    
    # Check environment variables
    smtp_user = os.getenv('SMTP_USER')
    smtp_password = os.getenv('SMTP_PASSWORD')
    smtp_host = os.getenv('SMTP_HOST', 'smtp.gmail.com')
    smtp_port = int(os.getenv('SMTP_PORT', '587'))
    from_email = os.getenv('FROM_EMAIL', smtp_user)
    
    print(f"📧 SMTP Host: {smtp_host}")
    print(f"🔌 SMTP Port: {smtp_port}")
    print(f"👤 SMTP User: {smtp_user}")
    print(f"🔑 Password Length: {len(smtp_password) if smtp_password else 0} characters")
    print(f"📤 From Email: {from_email}")
    print()
    
    # Check if credentials are set
    if not smtp_user:
        print("❌ SMTP_USER not set in .env file")
        return False
        
    if not smtp_password:
        print("❌ SMTP_PASSWORD not set in .env file")
        return False
    
    if len(smtp_password) != 16:
        print("⚠️  Warning: Gmail app passwords are typically 16 characters")
        print(f"   Your password is {len(smtp_password)} characters")
        print("   Make sure you're using an app password, not your regular password")
    
    # Test SMTP connection
    print("🔗 Testing SMTP connection...")
    try:
        with smtplib.SMTP(smtp_host, smtp_port) as server:
            print("✅ Connected to SMTP server")
            
            server.starttls()
            print("✅ TLS encryption started")
            
            server.login(smtp_user, smtp_password)
            print("✅ Authentication successful")
            
            print("\n🎉 Email configuration is working correctly!")
            print("You can now send emails through your AI agent.")
            return True
            
    except smtplib.SMTPAuthenticationError as e:
        print(f"❌ Authentication failed: {e}")
        print("\n💡 Tips to fix:")
        print("1. Make sure 2-factor authentication is enabled on your Gmail account")
        print("2. Generate an app password: https://myaccount.google.com/apppasswords")
        print("3. Use the app password (16 characters) in your .env file")
        return False
        
    except smtplib.SMTPException as e:
        print(f"❌ SMTP Error: {e}")
        return False
        
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def send_test_email():
    """Send a test email to verify end-to-end functionality."""
    smtp_user = os.getenv('SMTP_USER')
    
    if not smtp_user:
        print("❌ Cannot send test email: SMTP_USER not configured")
        return
    
    print("\n📧 Sending test email...")
    
    # Import and test the actual email tool
    sys.path.append(os.path.dirname(__file__))
    from src.tools.email_sender import EmailSenderTool
    
    email_tool = EmailSenderTool()
    
    result = email_tool._send_email(
        to=smtp_user,  # Send to yourself
        subject="Test Email from AI Agent",
        body=f"This is a test email sent at {os.popen('date').read().strip()}\n\nIf you received this, your email configuration is working! 🎉"
    )
    
    print(result)

if __name__ == "__main__":
    print("🤖 Python AI Agent - Email Configuration Test")
    print("=" * 50)
    
    if test_email_config():
        print("\n" + "=" * 50)
        
        while True:
            response = input("\n🤔 Would you like to send a test email to yourself? (y/n): ").lower().strip()
            if response in ['y', 'yes']:
                send_test_email()
                break
            elif response in ['n', 'no']:
                print("✅ Configuration test complete!")
                break
            else:
                print("Please enter 'y' or 'n'")
    else:
        print("\n❌ Please fix the configuration issues above and try again.")
