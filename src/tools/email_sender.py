"""Email sender tool for composing and sending emails."""

import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from typing import Dict, Any, Optional, List
import logging
from .base import Tool

logger = logging.getLogger(__name__)


class EmailSenderTool(Tool):
    """A tool for composing and sending emails via SMTP."""

    def __init__(self):
        super().__init__(
            name="email_sender",
            description="Compose and send emails. Operations: send, draft, list_drafts. Requires SMTP configuration in environment variables."
        )
        # Load SMTP configuration from environment
        self.smtp_host = os.getenv('SMTP_HOST', 'smtp.gmail.com')
        self.smtp_port = int(os.getenv('SMTP_PORT', '587'))
        self.smtp_user = os.getenv('SMTP_USER')
        self.smtp_password = os.getenv('SMTP_PASSWORD')
        self.from_email = os.getenv('FROM_EMAIL', self.smtp_user)

        # Store drafts in memory (in production, use a database)
        self.drafts = []

    def execute(self, operation: str, **kwargs) -> str:
        """Execute an email operation."""
        try:
            if operation == "send":
                return self._send_email(
                    kwargs.get('to'),
                    kwargs.get('subject'),
                    kwargs.get('body'),
                    kwargs.get('cc'),
                    kwargs.get('draft_id')
                )
            elif operation == "draft":
                return self._save_draft(
                    kwargs.get('to'),
                    kwargs.get('subject'),
                    kwargs.get('body'),
                    kwargs.get('cc')
                )
            elif operation == "list_drafts":
                return self._list_drafts()
            else:
                return f"Error: Unknown operation '{operation}'. Available: send, draft, list_drafts"
        except Exception as e:
            logger.error(f"Email sender error: {e}")
            return f"Error executing {operation}: {str(e)}"

    def _send_email(self, to: str, subject: str, body: str, cc: Optional[str] = None, draft_id: Optional[int] = None) -> str:
        """Send an email via SMTP with enhanced logging and feedback."""
        # Check if we're sending from a draft
        if draft_id is not None:
            if 0 <= draft_id < len(self.drafts):
                draft = self.drafts[draft_id]
                to = to or draft['to']
                subject = subject or draft['subject']
                body = body or draft['body']
                cc = cc or draft.get('cc')
                # Remove draft after using
                self.drafts.pop(draft_id)
                logger.info(f"Using draft {draft_id} for email to {to}")
            else:
                error_msg = f"❌ Error: Draft with ID {draft_id} not found"
                logger.error(error_msg)
                return error_msg

        # Validate required fields
        if not to:
            error_msg = "❌ Error: Recipient email address ('to') is required"
            logger.error(error_msg)
            return error_msg
        if not subject:
            error_msg = "❌ Error: Email subject is required"
            logger.error(error_msg)
            return error_msg
        if not body:
            body = "(No message body)"  # Allow empty body with warning
            logger.warning("Email sent with empty body")

        # Check SMTP configuration
        if not self.smtp_user or not self.smtp_password:
            error_msg = "❌ Error: SMTP credentials not configured.\n" \
                "Please set SMTP_USER and SMTP_PASSWORD in your .env file.\n" \
                "For Gmail: Enable 2-factor authentication and generate an app password."
            logger.error("SMTP credentials missing")
            return error_msg

        logger.info(f"Attempting to send email from {self.from_email} to {to}")
        logger.info(f"SMTP Server: {self.smtp_host}:{self.smtp_port}")

        try:
            # Create message
            msg = MIMEMultipart()
            msg['From'] = self.from_email
            msg['To'] = to
            msg['Subject'] = subject
            msg['Date'] = datetime.now().strftime("%a, %d %b %Y %H:%M:%S %z")

            if cc:
                msg['Cc'] = cc
                logger.info(f"CC recipients: {cc}")

            # Add body
            msg.attach(MIMEText(body, 'plain'))

            # Connect to SMTP server and send
            logger.info("Connecting to SMTP server...")
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                logger.info("Starting TLS...")
                server.starttls()

                logger.info("Authenticating...")
                server.login(self.smtp_user, self.smtp_password)

                # Prepare recipients
                recipients = [to]
                if cc:
                    recipients.extend([addr.strip() for addr in cc.split(',')])

                logger.info(f"Sending to recipients: {recipients}")
                server.send_message(
                    msg, from_addr=self.from_email, to_addrs=recipients)

            success_msg = f"✅ Email sent successfully!\n" \
                f"📧 From: {self.from_email}\n" \
                f"📬 To: {to}\n" \
                f"📋 Subject: {subject}\n" \
                f"⏰ Sent at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"

            if cc:
                success_msg += f"\n📎 CC: {cc}"

            logger.info(f"Email sent successfully to {to}")
            return success_msg

        except smtplib.SMTPAuthenticationError as e:
            error_msg = f"❌ SMTP Authentication failed!\n" \
                f"Check your email credentials in .env file.\n" \
                f"For Gmail: Make sure you're using an app password (16 characters), not your regular password.\n" \
                f"Error details: {str(e)}"
            logger.error(f"SMTP Authentication failed: {e}")
            return error_msg

        except smtplib.SMTPRecipientsRefused as e:
            error_msg = f"❌ Recipient address refused: {to}\n" \
                f"Please check the email address is valid.\n" \
                f"Error details: {str(e)}"
            logger.error(f"Recipients refused: {e}")
            return error_msg

        except smtplib.SMTPServerDisconnected as e:
            error_msg = f"❌ SMTP server disconnected unexpectedly.\n" \
                f"This might be a network issue or server problem.\n" \
                f"Error details: {str(e)}"
            logger.error(f"SMTP server disconnected: {e}")
            return error_msg

        except smtplib.SMTPException as e:
            error_msg = f"❌ SMTP Error occurred:\n{str(e)}"
            logger.error(f"SMTP Error: {e}")
            return error_msg

        except Exception as e:
            error_msg = f"❌ Unexpected error while sending email:\n{str(e)}"
            logger.error(f"Unexpected error: {e}")
            return error_msg

    def _save_draft(self, to: str, subject: str, body: str, cc: Optional[str] = None) -> str:
        """Save an email as draft."""
        draft = {
            'id': len(self.drafts),
            'to': to or '',
            'subject': subject or '',
            'body': body or '',
            'cc': cc or '',
            'created_at': datetime.now().isoformat()
        }

        self.drafts.append(draft)

        return f"📝 Draft saved!\n" \
            f"Draft ID: {draft['id']}\n" \
            f"To: {draft['to'] or '(not set)'}\n" \
            f"Subject: {draft['subject'] or '(not set)'}\n" \
            f"Use 'send' operation with draft_id={draft['id']} to send this draft."

    def _list_drafts(self) -> str:
        """List all saved drafts."""
        if not self.drafts:
            return "📭 No drafts saved"

        result = "📝 Saved drafts:\n\n"
        for draft in self.drafts:
            created = datetime.fromisoformat(draft['created_at'])
            result += f"[{draft['id']}] Created: {created.strftime('%Y-%m-%d %H:%M')}\n"
            result += f"    To: {draft['to'] or '(not set)'}\n"
            result += f"    Subject: {draft['subject'] or '(not set)'}\n"
            if draft['body']:
                preview = draft['body'][:50] + \
                    '...' if len(draft['body']) > 50 else draft['body']
                result += f"    Preview: {preview}\n"
            result += "\n"

        return result

    def get_schema(self) -> Dict[str, Any]:
        """Get the JSON schema for this tool's parameters."""
        return {
            "type": "object",
            "properties": {
                "operation": {
                    "type": "string",
                    "enum": ["send", "draft", "list_drafts"],
                    "description": "Operation: send (send email), draft (save as draft), list_drafts (show saved drafts)"
                },
                "to": {
                    "type": "string",
                    "description": "Recipient email address (required for send)"
                },
                "subject": {
                    "type": "string",
                    "description": "Email subject"
                },
                "body": {
                    "type": "string",
                    "description": "Email body content"
                },
                "cc": {
                    "type": "string",
                    "description": "CC recipients (comma-separated)"
                },
                "draft_id": {
                    "type": "integer",
                    "description": "Draft ID to send (for sending a saved draft)"
                }
            },
            "required": ["operation"]
        }
