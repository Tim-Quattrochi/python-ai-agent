"""Integration test for the AI Agent."""

from src.tools.base import ToolRegistry
from src.tools import CalculatorTool, WebSearchTool, FileOperationsTool
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


def test_tool_integration():
    """Test that all tools can be registered and work together."""
    print("🧪 Testing tool integration...")

    # Create registry
    registry = ToolRegistry()

    # Register tools
    calculator = CalculatorTool()
    web_search = WebSearchTool()
    file_ops = FileOperationsTool()

    registry.register_tool(calculator)
    registry.register_tool(web_search)
    registry.register_tool(file_ops)

    # Test registry functions
    assert len(registry.get_tool_names()) == 3
    assert "calculator" in registry.get_tool_names()
    assert "web_search" in registry.get_tool_names()
    assert "file_operations" in registry.get_tool_names()

    # Test tool schemas
    schemas = registry.get_tools_schema()
    assert len(schemas) == 3

    # Test calculator execution
    result = registry.execute_tool("calculator", {"expression": "2 + 2"})
    assert "4" in result

    # Test file operations
    test_content = "Hello from test!"
    test_file = "/tmp/test_agent.txt"

    # Write file
    write_result = registry.execute_tool("file_operations", {
        "operation": "write",
        "file_path": test_file,
        "content": test_content
    })
    assert "successfully" in write_result.lower()

    # Read file
    read_result = registry.execute_tool("file_operations", {
        "operation": "read",
        "file_path": test_file
    })
    assert test_content in read_result

    # Clean up
    import os
    if os.path.exists(test_file):
        os.remove(test_file)

    print("✅ All tool integration tests passed!")


def test_schemas_format():
    """Test that tool schemas are properly formatted for LLM function calling."""
    print("🧪 Testing schema formats...")

    tools = [CalculatorTool(), WebSearchTool(), FileOperationsTool()]

    for tool in tools:
        schema = tool.get_function_definition()

        # Check required fields
        assert "type" in schema
        assert schema["type"] == "function"
        assert "function" in schema

        func = schema["function"]
        assert "name" in func
        assert "description" in func
        assert "parameters" in func

        # Check parameters structure
        params = func["parameters"]
        assert "type" in params
        assert "properties" in params

        print(f"✅ {tool.name} schema is valid")

    print("✅ All schema format tests passed!")


if __name__ == "__main__":
    try:
        test_tool_integration()
        test_schemas_format()
        print("\n🎉 All integration tests passed! The agent is ready to use.")
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
