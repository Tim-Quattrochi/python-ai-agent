#!/usr/bin/env python3
"""
Standalone MCP Server for Python AI Agent.
This script can be used directly by MCP clients.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

if __name__ == "__main__":
    from src.mcp_cli import main
    main()
