"""Slack integration tool for team communication."""

import logging
from typing import Dict, Any, Optional, List
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
import os

from .base import Tool

logger = logging.getLogger(__name__)


class SlackTool(Tool):
    """Tool for Slack workspace integration."""

    name = "slack"
    description = "Send messages, manage channels, and interact with Slack workspace"

    def __init__(self):
        """Initialize Slack client."""
        super().__init__(
            name="slack",
            description="Send messages, manage channels, and interact with Slack workspace"
        )
        self.token = os.getenv('SLACK_BOT_TOKEN')
        self.client = WebClient(token=self.token) if self.token else None

    def get_schema(self) -> Dict[str, Any]:
        """Get the JSON schema for Slack tool parameters."""
        return {
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "enum": ["send_message", "list_channels", "create_channel", "get_user_info", "upload_file"],
                    "description": "The Slack operation to perform"
                },
                "channel": {
                    "type": "string",
                    "description": "Channel ID or name (e.g., #general, C1234567890)"
                },
                "message": {
                    "type": "string",
                    "description": "Message content to send"
                },
                "thread_ts": {
                    "type": "string",
                    "description": "Timestamp of parent message for threading"
                },
                "name": {
                    "type": "string",
                    "description": "Name for new channel creation"
                },
                "is_private": {
                    "type": "boolean",
                    "default": False,
                    "description": "Whether to create a private channel"
                },
                "user_id": {
                    "type": "string",
                    "description": "Slack user ID to get information for"
                },
                "channels": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "List of channels for file upload"
                },
                "file_path": {
                    "type": "string",
                    "description": "Path to file to upload"
                },
                "title": {
                    "type": "string",
                    "description": "Title for uploaded file"
                },
                "initial_comment": {
                    "type": "string",
                    "description": "Initial comment for uploaded file"
                }
            },
            "required": ["action"],
            "additionalProperties": False
        }

    def execute(self, action: str, **kwargs) -> Dict[str, Any]:
        """Execute Slack operations."""
        if not self.client:
            return {"error": "Slack bot token not configured"}

        try:
            if action == "send_message":
                return self._send_message(
                    channel=kwargs.get('channel'),
                    message=kwargs.get('message'),
                    thread_ts=kwargs.get('thread_ts')
                )
            elif action == "list_channels":
                return self._list_channels()
            elif action == "create_channel":
                return self._create_channel(
                    name=kwargs.get('name'),
                    is_private=kwargs.get('is_private', False)
                )
            elif action == "get_user_info":
                return self._get_user_info(user_id=kwargs.get('user_id'))
            elif action == "upload_file":
                return self._upload_file(
                    channels=kwargs.get('channels'),
                    file_path=kwargs.get('file_path'),
                    title=kwargs.get('title'),
                    initial_comment=kwargs.get('initial_comment')
                )
            else:
                return {"error": f"Unknown action: {action}"}

        except SlackApiError as e:
            logger.error(f"Slack API error: {e.response['error']}")
            return {"error": f"Slack API error: {e.response['error']}"}
        except Exception as e:
            logger.error(f"Error in Slack tool: {str(e)}")
            return {"error": f"Slack tool error: {str(e)}"}

    def _send_message(self, channel: str, message: str, thread_ts: Optional[str] = None) -> Dict[str, Any]:
        """Send a message to a Slack channel."""
        response = self.client.chat_postMessage(
            channel=channel,
            text=message,
            thread_ts=thread_ts
        )

        return {
            "success": True,
            "message": f"✅ Message sent to #{channel}",
            "timestamp": response['ts'],
            "channel": response['channel']
        }

    def _list_channels(self) -> Dict[str, Any]:
        """List all channels in the workspace."""
        response = self.client.conversations_list(
            types="public_channel,private_channel")

        channels = []
        for channel in response['channels']:
            channels.append({
                "id": channel['id'],
                "name": channel['name'],
                "is_private": channel['is_private'],
                "num_members": channel.get('num_members', 0)
            })

        return {
            "success": True,
            "channels": channels,
            "count": len(channels)
        }

    def _create_channel(self, name: str, is_private: bool = False) -> Dict[str, Any]:
        """Create a new channel."""
        response = self.client.conversations_create(
            name=name,
            is_private=is_private
        )

        return {
            "success": True,
            "message": f"✅ Created {'private' if is_private else 'public'} channel #{name}",
            "channel_id": response['channel']['id'],
            "channel_name": response['channel']['name']
        }

    def _get_user_info(self, user_id: str) -> Dict[str, Any]:
        """Get information about a user."""
        response = self.client.users_info(user=user_id)
        user = response['user']

        return {
            "success": True,
            "user": {
                "id": user['id'],
                "name": user['name'],
                "real_name": user.get('real_name', ''),
                "email": user.get('profile', {}).get('email', ''),
                "is_admin": user.get('is_admin', False),
                "is_bot": user.get('is_bot', False)
            }
        }

    def _upload_file(self, channels: str, file_path: str, title: str = None, initial_comment: str = None) -> Dict[str, Any]:
        """Upload a file to Slack."""
        response = self.client.files_upload(
            channels=channels,
            file=file_path,
            title=title,
            initial_comment=initial_comment
        )

        return {
            "success": True,
            "message": f"✅ File uploaded to {channels}",
            "file_id": response['file']['id'],
            "file_url": response['file']['url_private']
        }
