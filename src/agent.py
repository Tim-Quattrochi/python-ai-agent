"""Main Agent class that orchestrates the conversation and tool execution."""

from typing import List, Dict, Any, Optional
import logging
from dataclasses import dataclass

from .config import Config, get_config
from .llm_client import LLMClient, create_llm_client, Message
from .tools.base import Tool, ToolRegistry
from .tools.calculator import CalculatorTool
from .tools.web_search import WebSearchTool
from .tools.file_ops import FileOperationsTool
from .tools.task_scheduler import TaskSchedulerTool
from .tools.email_sender import EmailSenderTool
from .tools.todo_manager import TodoManagerTool
from .tools.database import DatabaseTool
from .tools.image_processing import ImageProcessingTool
from .tools.github import GitHubTool
from .tools.weather import WeatherTool
from .tools.content_generator import ContentGeneratorTool
from .tools.ml_tool import MLTool
from .tools.slack_integration import SlackTool
from .tools.system_monitor import SystemMonitorTool

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class ConversationState:
    """Represents the current state of the conversation."""
    messages: List[Message]
    tool_calls_count: int = 0

    def add_message(self, message: Message):
        """Add a message to the conversation history."""
        self.messages.append(message)

    def get_recent_messages(self, max_count: int) -> List[Message]:
        """Get the most recent messages up to max_count."""
        return self.messages[-max_count:] if max_count > 0 else self.messages


class Agent:
    """Main AI Agent class that handles conversations and tool execution."""

    def __init__(self, config: Optional[Config] = None):
        """Initialize the agent with configuration and components."""
        self.config = config or get_config()
        self.llm_client = create_llm_client(self.config)
        self.tool_registry = ToolRegistry()
        self.conversation_state = ConversationState(messages=[])

        # Register available tools
        self._register_tools()

        # Add system message
        system_message = Message(
            role="system",
            content=self._get_system_prompt()
        )
        self.conversation_state.add_message(system_message)

        logger.info(
            f"Agent initialized with {self.config.llm_provider} provider")

    def _get_system_prompt(self) -> str:
        """Get the system prompt for the agent."""
        available_tools = self.tool_registry.get_tool_names()
        tools_description = ", ".join(
            available_tools) if available_tools else "No tools available"

        return f"""You are a helpful AI assistant with access to various tools.

Available tools: {tools_description}

Guidelines:
1. Use tools when they can help answer the user's question or complete their request
2. Always explain what you're doing when using tools
3. If a tool call fails, try to handle the error gracefully and explain what went wrong
4. Be conversational and helpful in your responses
5. If you need to use multiple tools, use them one at a time and explain each step

Remember to think step by step and use the appropriate tools to provide accurate and helpful responses."""

    def _register_tools(self):
        """Register all available tools."""
        # Register core tools
        self.register_tool(CalculatorTool())
        self.register_tool(WebSearchTool())
        self.register_tool(FileOperationsTool())

        # Register task automation tools
        self.register_tool(TaskSchedulerTool())
        self.register_tool(EmailSenderTool())
        self.register_tool(TodoManagerTool())

        # Register data and development tools
        self.register_tool(DatabaseTool())
        self.register_tool(ImageProcessingTool())
        self.register_tool(GitHubTool())
        self.register_tool(WeatherTool())

        # Register advanced tools
        self.register_tool(ContentGeneratorTool())
        self.register_tool(MLTool())
        self.register_tool(SlackTool())
        self.register_tool(SystemMonitorTool())

        logger.info("All tools registered successfully")

    def register_tool(self, tool: Tool):
        """Register a new tool with the agent."""
        self.tool_registry.register_tool(tool)
        logger.info(f"Registered tool: {tool.name}")

    def process_message(self, user_input: str) -> str:
        """Process a user message and return the agent's response."""
        try:
            # Check for tool-specific interactions
            if user_input.lower() in ['email_sender', 'email', 'task_scheduler', 'tasks', 'todo_manager', 'todo']:
                # Provide a helpful guide for tool usage
                tool_guides = {
                    'email_sender': "Email Sender Tool Operations:\n"
                                    "- 'draft': Save an email draft\n"
                                    "- 'send': Send an email\n"
                                    "- 'list_drafts': Show saved drafts\n"
                                    "Example: 'draft an email to team'",
                    'task_scheduler': "Task Scheduler Operations:\n"
                                      "- 'schedule': Create a new task\n"
                                      "- 'list': Show tasks\n"
                                      "- 'complete': Mark task as done\n"
                                      "- 'overdue': Show overdue tasks\n"
                                      "Example: 'schedule a meeting next week'",
                    'todo_manager': "Todo Manager Operations:\n"
                                    "- 'add': Create a new todo\n"
                                    "- 'list': Show todos\n"
                                    "- 'complete': Mark todo as done\n"
                                    "- 'stats': Get todo statistics\n"
                                    "Example: 'add todo to review reports'"
                }

                # Get the tool name
                tool_name = user_input.lower().replace('_', ' ').replace(' ', '_')

                return tool_guides.get(tool_name, "Tool not found. Please specify a valid operation.")

            # Add user message to conversation
            user_message = Message(role="user", content=user_input)
            self.conversation_state.add_message(user_message)

            # Get recent messages for context
            recent_messages = self.conversation_state.get_recent_messages(
                self.config.max_conversation_history
            )

            # Reset tool calls count for this turn
            self.conversation_state.tool_calls_count = 0

            # Generate response with potential tool calls
            response = self._generate_response_with_tools(recent_messages)

            return response

        except Exception as e:
            logger.error(f"Error processing message: {str(e)}")
            return f"I apologize, but I encountered an error: {str(e)}"

    def _generate_response_with_tools(self, messages: List[Message]) -> str:
        """Generate a response, handling tool calls if necessary."""
        max_iterations = self.config.max_tool_calls_per_turn
        iteration = 0
        current_messages = messages.copy()

        while iteration < max_iterations:
            iteration += 1

            # Get available tools in the required format
            tools = self.tool_registry.get_tools_schema()

            # Generate response from LLM
            response = self.llm_client.generate_response(
                current_messages, tools)

            # Add assistant message to conversation
            self.conversation_state.add_message(response)

            # Check if there are tool calls to execute
            if not response.tool_calls:
                # No tool calls, return the response content
                return response.content

            # Execute tool calls
            for tool_call in response.tool_calls:
                tool_result = self._execute_tool_call(tool_call)

                # Add tool result to conversation
                tool_message = Message(
                    role="tool",
                    content=tool_result,
                    tool_call_id=tool_call["id"]
                )
                self.conversation_state.add_message(tool_message)
                current_messages.append(tool_message)

            # Continue the loop to let the LLM respond to the tool results

        # If we've hit the max iterations, return the last response content
        logger.warning(
            f"Reached maximum tool call iterations ({max_iterations})")
        return response.content if 'response' in locals() else "Maximum iterations reached without a final response."

    def _execute_tool_call(self, tool_call: Dict[str, Any]) -> str:
        """Execute a single tool call and return the result."""
        try:
            function = tool_call["function"]
            tool_name = function["name"]

            # Parse arguments
            import json
            try:
                arguments = json.loads(function["arguments"])
            except json.JSONDecodeError:
                return f"Error: Invalid JSON arguments for tool {tool_name}"

            # Execute the tool
            result = self.tool_registry.execute_tool(tool_name, arguments)

            logger.info(
                f"Executed tool {tool_name} with result: {result[:100]}...")
            return result

        except Exception as e:
            error_msg = f"Error executing tool: {str(e)}"
            logger.error(error_msg)
            return error_msg

    def get_conversation_history(self) -> List[Dict[str, Any]]:
        """Get the conversation history as a list of dictionaries."""
        return [msg.to_dict() for msg in self.conversation_state.messages]

    def clear_conversation(self):
        """Clear the conversation history except for the system message."""
        system_msg = self.conversation_state.messages[0]  # Keep system message
        self.conversation_state = ConversationState(messages=[system_msg])
        logger.info("Conversation history cleared")

    def get_available_tools(self) -> List[str]:
        """Get a list of available tool names."""
        return self.tool_registry.get_tool_names()
