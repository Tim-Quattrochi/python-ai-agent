#!/usr/bin/env python3
"""Standalone MCP server script for VS Code integration."""

import sys
import os
import logging
import asyncio
from pathlib import Path

# Add the src directory to Python path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

# Configure logging to stderr to avoid interfering with MCP protocol
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stderr
)

logger = logging.getLogger(__name__)


def main():
    """Main entry point for standalone MCP server."""
    try:
        logger.info("🚀 Starting standalone Python AI Agent MCP Server...")

        # Import and initialize the tools with absolute imports
        from tools.base import ToolRegistry
        from tools.calculator import CalculatorTool
        from tools.web_search import WebSearchTool
        from tools.file_ops import FileOperationsTool
        from mcp.server.fastmcp import FastMCP

        # Create FastMCP server
        mcp = FastMCP("Python AI Agent")

        # Initialize tool registry and tools
        tool_registry = ToolRegistry()
        tool_registry.register_tool(CalculatorTool())
        tool_registry.register_tool(WebSearchTool())
        tool_registry.register_tool(FileOperationsTool())

        @mcp.tool()
        def calculator(expression: str) -> str:
            """
            Evaluate a mathematical expression.

            Args:
                expression: Mathematical expression to evaluate

            Returns:
                The result of the calculation
            """
            try:
                result = tool_registry.execute_tool(
                    "calculator", {"expression": expression})
                return result
            except Exception as e:
                return f"Error: {str(e)}"

        @mcp.tool()
        def web_search(query: str) -> str:
            """
            Search the web for information.

            Args:
                query: Search query

            Returns:
                Search results
            """
            try:
                result = tool_registry.execute_tool(
                    "web_search", {"query": query})
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

        # Run the server
        logger.info("Tools registered, starting MCP server...")

        # Check if we're in an existing event loop
        try:
            loop = asyncio.get_running_loop()
            logger.info("Running in existing event loop")
            # If we're already in a loop, just run the server
            mcp.run_sync()
        except RuntimeError:
            # No event loop, start one
            logger.info("Starting new event loop")
            mcp.run()

    except Exception as e:
        logger.error(f"Failed to start MCP server: {e}")
        import traceback
        logger.error(traceback.format_exc())
        sys.exit(1)


if __name__ == "__main__":
    main()
