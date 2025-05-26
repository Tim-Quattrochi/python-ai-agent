#!/usr/bin/env python3
"""Test script to verify MCP server functionality."""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.mcp_server import tool_registry

def test_mcp_tools():
    """Test all MCP tools to ensure they work correctly."""
    print("🧪 Testing MCP Server Tools")
    print("=" * 50)
    
    # Test Calculator
    print("\n📊 Testing Calculator Tool:")
    try:
        result = tool_registry.execute_tool("calculator", {"expression": "2 + 2 * 3"})
        print(f"   ✅ Calculator: 2 + 2 * 3 = {result}")
    except Exception as e:
        print(f"   ❌ Calculator error: {e}")
    
    # Test Web Search (if API key is available)
    print("\n🔍 Testing Web Search Tool:")
    try:
        result = tool_registry.execute_tool("web_search", {
            "query": "python programming", 
            "num_results": 2
        })
        print(f"   ✅ Web Search completed: {result[:100]}...")
    except Exception as e:
        print(f"   ⚠️  Web Search error (may need API key): {e}")
    
    # Test File Operations
    print("\n📁 Testing File Operations Tool:")
    
    # Test write
    try:
        test_file = "/tmp/mcp_test.txt"
        write_result = tool_registry.execute_tool("file_operations", {
            "operation": "write",
            "file_path": test_file,
            "content": "Hello from MCP Server!"
        })
        print(f"   ✅ File Write: {write_result}")
        
        # Test read
        read_result = tool_registry.execute_tool("file_operations", {
            "operation": "read",
            "file_path": test_file
        })
        print(f"   ✅ File Read: {read_result}")
        
        # Clean up
        import os
        os.remove(test_file)
        print(f"   ✅ File cleanup completed")
        
    except Exception as e:
        print(f"   ❌ File Operations error: {e}")
    
    print("\n🎉 MCP Server test completed!")
    print("\n📋 Available tools:")
    for tool_name in tool_registry.get_tool_names():
        tool = tool_registry.get_tool(tool_name)
        print(f"   - {tool_name}: {tool.description}")

if __name__ == "__main__":
    test_mcp_tools()
