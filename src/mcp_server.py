"""MCP Server implementation for the Python AI Agent using FastMCP."""

import asyncio
import json
import logging
from typing import Dict, Any, List, Optional
from mcp.server.fastmcp import FastMCP

from .tools.base import ToolRegistry
from .tools.calculator import CalculatorTool
from .tools.web_search import WebSearchTool
from .tools.file_ops import FileOperationsTool

logger = logging.getLogger(__name__)

# Create FastMCP server
mcp = FastMCP("Python AI Agent")

# Initialize tool registry
tool_registry = ToolRegistry()


def register_tools():
    """Register all available tools."""
    try:
        tool_registry.register_tool(CalculatorTool())
        logger.info("Registered CalculatorTool")
    except Exception as e:
        logger.error(f"Failed to register CalculatorTool: {e}")

    try:
        tool_registry.register_tool(WebSearchTool())
        logger.info("Registered WebSearchTool")
    except Exception as e:
        logger.error(f"Failed to register WebSearchTool: {e}")

    try:
        tool_registry.register_tool(FileOperationsTool())
        logger.info("Registered FileOperationsTool")
    except Exception as e:
        logger.error(f"Failed to register FileOperationsTool: {e}")


# Register tools when module is imported
register_tools()


@mcp.tool()
def calculator(expression: str) -> str:
    """
    Perform mathematical calculations.

    Args:
        expression: Mathematical expression to evaluate

    Returns:
        Result of the calculation
    """
    try:
        result = tool_registry.execute_tool(
            "calculator", {"expression": expression})
        return result
    except Exception as e:
        return f"Error: {str(e)}"


@mcp.tool()
def web_search(query: str, num_results: int = 5) -> str:
    """
    Search the web for information.

    Args:
        query: Search query
        num_results: Number of results to return (default: 5)

    Returns:
        Search results
    """
    try:
        result = tool_registry.execute_tool("web_search", {
            "query": query,
            "num_results": num_results
        })
        return result
    except Exception as e:
        return f"Error: {str(e)}"


@mcp.tool()
def read_file(file_path: str) -> str:
    """
    Read the contents of a file.

    Args:
        file_path: Path to the file to read

    Returns:
        File contents
    """
    try:
        result = tool_registry.execute_tool("file_operations", {
            "operation": "read",
            "file_path": file_path
        })
        return result
    except Exception as e:
        return f"Error: {str(e)}"


@mcp.tool()
def write_file(file_path: str, content: str) -> str:
    """
    Write content to a file.

    Args:
        file_path: Path to the file to write
        content: Content to write to the file

    Returns:
        Success message
    """
    try:
        result = tool_registry.execute_tool("file_operations", {
            "operation": "write",
            "file_path": file_path,
            "content": content
        })
        return result
    except Exception as e:
        return f"Error: {str(e)}"


@mcp.tool()
def list_directory(directory_path: str) -> str:
    """
    List the contents of a directory.

    Args:
        directory_path: Path to the directory to list

    Returns:
        Directory contents
    """
    try:
        result = tool_registry.execute_tool("file_operations", {
            "operation": "list",
            "file_path": directory_path
        })
        return result
    except Exception as e:
        return f"Error: {str(e)}"


def run_server():
    """Run the MCP server with proper event loop handling."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    logger.info("Starting Python AI Agent MCP Server...")

    try:
        # Check if we're already in an event loop (like VS Code)
        loop = asyncio.get_running_loop()
        logger.warning(
            "Already running in an event loop - using run_sync() mode")
        # Use run_sync() for environments that already have an event loop
        mcp.run_sync()
    except RuntimeError:
        # No event loop running, we can use the normal approach
        logger.info("Starting new event loop with mcp.run()")
        # Use mcp.run() which handles event loop creation internally
        mcp.run()


if __name__ == "__main__":
    run_server()
