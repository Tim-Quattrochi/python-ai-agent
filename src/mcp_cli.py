#!/usr/bin/env python3
"""CLI for running the agent as an MCP server."""

import argparse
import asyncio
import sys
import logging
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))


def main():
    """Main entry point for MCP server."""
    parser = argparse.ArgumentParser(
        description="Python AI Agent MCP Server",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python mcp_cli.py                 # Run MCP server with INFO logging
  python mcp_cli.py --verbose       # Run MCP server with DEBUG logging
  python mcp_cli.py --quiet         # Run MCP server with WARNING logging only

The MCP server exposes the following tools:
  - calculator: Perform mathematical calculations
  - web_search: Search the web for information
  - file_operations: Read, write, and manage files

Connect to this server using any MCP-compatible client.
        """
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose (DEBUG) logging"
    )
    parser.add_argument(
        "--quiet", "-q",
        action="store_true",
        help="Enable quiet mode (WARNING level logging only)"
    )

    args = parser.parse_args()

    # Set up logging level based on arguments
    if args.verbose:
        log_level = logging.DEBUG
    elif args.quiet:
        log_level = logging.WARNING
    else:
        log_level = logging.INFO

    # Configure logging
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            # Log to stderr to avoid interfering with MCP protocol
            logging.StreamHandler(sys.stderr)
        ]
    )

    logger = logging.getLogger(__name__)
    logger.info("🚀 Starting Python AI Agent MCP Server...")

    try:
        # Import the MCP server run function here to avoid circular imports
        from .mcp_server import run_server
        # Call run_server() directly - it handles event loop management
        run_server()
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Server error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
