#!/usr/bin/env python3
"""
Simple email test script to check if current SMTP configuration works.
"""

import os
import sys
from dotenv import load_dotenv

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from tools.email_sender import EmailSenderTool

def main():
    print("🧪 Simple Email Test")
    print("=" * 30)
    
    # Load environment variables
    load_dotenv()
    
    # Check SMTP settings
    smtp_user = os.getenv('SMTP_USER')
    smtp_password = os.getenv('SMTP_PASSWORD')
    
    if not smtp_user or not smtp_password:
        print("❌ SMTP credentials not found in .env file")
        return False
    
    print(f"📧 Testing email to: {smtp_user}")
    print(f"🔑 Password length: {len(smtp_password)} characters")
    
    # Test email sending
    try:
        email_tool = EmailSenderTool()
        
        result = email_tool.execute(
            operation="send",
            to=smtp_user,
            subject="🧪 AI Agent Email Test - " + str(os.popen('date +%H:%M:%S').read().strip()),
            body="This is a test email from your Python AI Agent. If you receive this, your email configuration is working! 🎉"
        )
        
        print("\n📨 Email result:")
        print(result)
        
        if "✅" in result and ("sent successfully" in result or "Email sent" in result):
            print("\n🎉 EMAIL TEST PASSED!")
            print("Check your inbox for the test email.")
            return True
        else:
            print("\n❌ EMAIL TEST FAILED!")
            return False
            
    except Exception as e:
        print(f"\n❌ Email test failed with exception: {e}")
        return False

if __name__ == "__main__":
    success = main()
    if success:
        print("\n✅ Your email configuration is working correctly!")
        print("Now you can proceed to revoke and update your Gmail app password.")
    else:
        print("\n💡 Please check your .env file and SMTP settings before proceeding.")
    
    sys.exit(0 if success else 1)
