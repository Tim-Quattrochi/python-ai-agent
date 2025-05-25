#!/usr/bin/env python3
"""Comprehensive test script for the enhanced AI Agent with all tools."""

from src.config import get_config
from src.agent import Agent
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))


def test_agent_initialization():
    """Test agent initialization and tool registration."""
    print("🚀 Testing Agent Initialization...")

    try:
        agent = Agent()
        print("✅ Agent initialized successfully")

        # Check available tools
        tools = agent.get_available_tools()
        print(f"📋 Available tools ({len(tools)}): {', '.join(tools)}")

        expected_tools = [
            'calculator', 'web_search', 'file_operations',
            'task_scheduler', 'email_sender', 'todo_manager',
            'database', 'image_processing', 'github', 'weather',
            'content_generator', 'ml_tool', 'slack', 'system_monitor'
        ]

        missing_tools = [tool for tool in expected_tools if tool not in tools]
        if missing_tools:
            print(f"⚠️ Missing tools: {missing_tools}")
        else:
            print("✅ All expected tools are registered")

        return agent

    except Exception as e:
        print(f"❌ Agent initialization failed: {e}")
        return None


def test_basic_interactions(agent):
    """Test basic agent interactions."""
    print("\n🧪 Testing Basic Interactions...")

    test_queries = [
        "What tools do you have available?",
        "Calculate 25 * 47",
        "What's the weather like? (Note: requires API key)",
        "Help me with email operations",
        "Show me todo manager operations"
    ]

    for query in test_queries:
        print(f"\n📝 Query: {query}")
        try:
            response = agent.process_message(query)
            print(
                f"🤖 Response: {response[:200]}{'...' if len(response) > 200 else ''}")
        except Exception as e:
            print(f"❌ Error: {e}")


def test_tool_specific_operations(agent):
    """Test specific tool operations."""
    print("\n🔧 Testing Tool-Specific Operations...")

    # Test calculator
    print("\n➕ Testing Calculator:")
    try:
        response = agent.process_message("Calculate the square root of 144")
        print(f"Calculator response: {response[:150]}...")
    except Exception as e:
        print(f"Calculator error: {e}")

    # Test file operations
    print("\n📁 Testing File Operations:")
    try:
        response = agent.process_message("List files in the current directory")
        print(f"File ops response: {response[:150]}...")
    except Exception as e:
        print(f"File ops error: {e}")

    # Test todo manager
    print("\n✅ Testing Todo Manager:")
    try:
        response = agent.process_message(
            "Add a todo item: Test the new AI agent features")
        print(f"Todo response: {response[:150]}...")
    except Exception as e:
        print(f"Todo error: {e}")


def test_system_monitor(agent):
    """Test system monitoring capabilities."""
    print("\n💻 Testing System Monitor:")
    try:
        response = agent.process_message("Check system CPU usage")
        print(f"System monitor response: {response[:200]}...")
    except Exception as e:
        print(f"System monitor error: {e}")


def test_ml_capabilities(agent):
    """Test ML tool capabilities."""
    print("\n🤖 Testing ML Tool:")
    try:
        response = agent.process_message(
            "What machine learning operations can you perform?")
        print(f"ML tool response: {response[:200]}...")
    except Exception as e:
        print(f"ML tool error: {e}")


def main():
    """Run comprehensive agent tests."""
    print("🧬 Starting Comprehensive AI Agent Tests")
    print("=" * 50)

    # Initialize agent
    agent = test_agent_initialization()
    if not agent:
        print("❌ Cannot continue tests without agent initialization")
        return

    # Run tests
    test_basic_interactions(agent)
    test_tool_specific_operations(agent)
    test_system_monitor(agent)
    test_ml_capabilities(agent)

    print("\n" + "=" * 50)
    print("🎉 Tests completed! Check the output above for any issues.")

    # Print final summary
    tools = agent.get_available_tools()
    print(f"\n📊 Final Summary:")
    print(f"   • Total tools registered: {len(tools)}")
    print(f"   • Agent status: Ready for use")
    print(f"   • LLM Provider: {agent.config.llm_provider}")

    if agent.config.llm_provider == 'local':
        print(f"   • Local LLM URL: {agent.config.local_llm_url}")


if __name__ == "__main__":
    main()
