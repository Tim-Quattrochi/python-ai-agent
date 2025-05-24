"""Base classes for the tool system."""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
import logging

logger = logging.getLogger(__name__)


class Tool(ABC):
    """Abstract base class for all tools."""

    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description

    @abstractmethod
    def execute(self, **kwargs) -> str:
        """Execute the tool with the given arguments."""
        pass

    @abstractmethod
    def get_schema(self) -> Dict[str, Any]:
        """Get the JSON schema for this tool's parameters."""
        pass

    def get_function_definition(self) -> Dict[str, Any]:
        """Get the function definition for LLM tool calling."""
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": self.get_schema()
            }
        }


class ToolRegistry:
    """Registry for managing available tools."""

    def __init__(self):
        self._tools: Dict[str, Tool] = {}

    def register_tool(self, tool: Tool):
        """Register a tool in the registry."""
        self._tools[tool.name] = tool
        logger.info(f"Registered tool: {tool.name}")

    def get_tool(self, name: str) -> Optional[Tool]:
        """Get a tool by name."""
        return self._tools.get(name)

    def get_tool_names(self) -> List[str]:
        """Get a list of all registered tool names."""
        return list(self._tools.keys())

    def get_tools_schema(self) -> List[Dict[str, Any]]:
        """Get the schema for all registered tools."""
        return [tool.get_function_definition() for tool in self._tools.values()]

    def execute_tool(self, name: str, arguments: Dict[str, Any]) -> str:
        """Execute a tool with the given arguments."""
        tool = self.get_tool(name)
        if not tool:
            raise ValueError(f"Tool '{name}' not found")

        try:
            result = tool.execute(**arguments)
            return str(result)
        except Exception as e:
            raise Exception(f"Error executing tool '{name}': {str(e)}")

    def list_tools(self) -> str:
        """Get a formatted list of available tools."""
        if not self._tools:
            return "No tools available."

        tool_list = []
        for tool in self._tools.values():
            tool_list.append(f"- {tool.name}: {tool.description}")

        return "Available tools:\n" + "\n".join(tool_list)
