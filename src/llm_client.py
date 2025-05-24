"""LLM client wrapper supporting both OpenAI and Anthropic."""

import json
from typing import List, Dict, Any, Optional, Union
from abc import ABC, abstractmethod

import openai
import anthropic

from .config import Config


class Message:
    """Represents a conversation message."""

    def __init__(self, role: str, content: str, tool_calls: Optional[List[Dict]] = None, tool_call_id: Optional[str] = None):
        self.role = role
        self.content = content
        self.tool_calls = tool_calls or []
        self.tool_call_id = tool_call_id

    def to_dict(self) -> Dict[str, Any]:
        """Convert message to dictionary format."""
        msg = {"role": self.role, "content": self.content}
        if self.tool_calls:
            msg["tool_calls"] = self.tool_calls
        if self.tool_call_id:
            msg["tool_call_id"] = self.tool_call_id
        return msg


class LLMClient(ABC):
    """Abstract base class for LLM clients."""

    @abstractmethod
    def generate_response(self, messages: List[Message], tools: Optional[List[Dict]] = None) -> Message:
        """Generate a response from the LLM."""
        pass


class AnthropicClient(LLMClient):
    """Anthropic Claude client."""

    def __init__(self, config: Config):
        self.config = config
        self.client = anthropic.Anthropic(api_key=config.anthropic_api_key)

    def generate_response(self, messages: List[Message], tools: Optional[List[Dict]] = None) -> Message:
        """Generate a response using Anthropic Claude."""
        # Convert messages to Anthropic format
        anthropic_messages = []
        system_message = None

        for msg in messages:
            if msg.role == "system":
                system_message = msg.content
            elif msg.role in ["user", "assistant"]:
                anthropic_messages.append({
                    "role": msg.role,
                    "content": msg.content
                })

        try:
            kwargs = {
                "model": self.config.current_model,
                "max_tokens": 4096,
                "messages": anthropic_messages
            }

            if system_message:
                kwargs["system"] = system_message

            if tools:
                kwargs["tools"] = self._convert_tools_to_anthropic_format(
                    tools)

            response = self.client.messages.create(**kwargs)

            # Handle tool calls if present
            tool_calls = []
            if hasattr(response, 'content') and isinstance(response.content, list):
                for content_block in response.content:
                    if hasattr(content_block, 'type') and content_block.type == 'tool_use':
                        tool_calls.append({
                            "id": content_block.id,
                            "type": "function",
                            "function": {
                                "name": content_block.name,
                                "arguments": json.dumps(content_block.input)
                            }
                        })

            content = ""
            if hasattr(response, 'content'):
                if isinstance(response.content, list):
                    text_blocks = [block for block in response.content if hasattr(
                        block, 'type') and block.type == 'text']
                    if text_blocks:
                        content = text_blocks[0].text
                else:
                    content = str(response.content)

            return Message(
                role="assistant",
                content=content,
                tool_calls=tool_calls if tool_calls else None
            )

        except Exception as e:
            raise Exception(f"Anthropic API error: {str(e)}")

    def _convert_tools_to_anthropic_format(self, tools: List[Dict]) -> List[Dict]:
        """Convert OpenAI-style tools to Anthropic format."""
        anthropic_tools = []
        for tool in tools:
            if tool.get("type") == "function":
                func = tool["function"]
                anthropic_tools.append({
                    "name": func["name"],
                    "description": func["description"],
                    "input_schema": func["parameters"]
                })
        return anthropic_tools


class OpenAIClient(LLMClient):
    """OpenAI GPT client."""

    def __init__(self, config: Config):
        self.config = config
        self.client = openai.OpenAI(api_key=config.openai_api_key)

    def generate_response(self, messages: List[Message], tools: Optional[List[Dict]] = None) -> Message:
        """Generate a response using OpenAI GPT."""
        # Convert messages to OpenAI format
        openai_messages = [msg.to_dict() for msg in messages]

        try:
            kwargs = {
                "model": self.config.current_model,
                "messages": openai_messages,
                "max_tokens": 4096
            }

            if tools:
                kwargs["tools"] = tools
                kwargs["tool_choice"] = "auto"

            response = self.client.chat.completions.create(**kwargs)

            message = response.choices[0].message

            tool_calls = []
            if hasattr(message, 'tool_calls') and message.tool_calls:
                tool_calls = [
                    {
                        "id": tc.id,
                        "type": tc.type,
                        "function": {
                            "name": tc.function.name,
                            "arguments": tc.function.arguments
                        }
                    }
                    for tc in message.tool_calls
                ]

            return Message(
                role="assistant",
                content=message.content or "",
                tool_calls=tool_calls if tool_calls else None
            )

        except Exception as e:
            raise Exception(f"OpenAI API error: {str(e)}")


def create_llm_client(config: Config) -> LLMClient:
    """Factory function to create the appropriate LLM client."""
    if config.llm_provider == "anthropic":
        return AnthropicClient(config)
    elif config.llm_provider == "openai":
        return OpenAIClient(config)
    else:
        raise ValueError(f"Unsupported LLM provider: {config.llm_provider}")
