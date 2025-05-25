#!/usr/bin/env python3
"""Test script for the enhanced AI Agent with all tools."""

from src.config import get_config
from src.agent import Agent
import os
import sys
import logging
from dotenv import load_dotenv

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))


# Set up logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def test_tool_registration():
    """Test that all tools are properly registered."""
    print("🔧 Testing tool registration...")

    try:
        # Load environment variables
        load_dotenv()

        # Initialize agent
        agent = Agent()

        # Get registered tools
        tool_names = agent.tool_registry.get_tool_names()

        print(f"✅ Agent initialized successfully!")
        print(f"📋 Total tools registered: {len(tool_names)}")
        print("🛠️  Available tools:")

        for i, tool_name in enumerate(tool_names, 1):
            print(f"   {i:2d}. {tool_name}")

        # Expected tools
        expected_tools = [
            'calculator', 'web_search', 'file_ops', 'task_scheduler',
            'email_sender', 'todo_manager', 'database', 'image_processing',
            'github', 'weather', 'content_generator', 'ml_tool',
            'slack', 'system_monitor'
        ]

        missing_tools = [
            tool for tool in expected_tools if tool not in tool_names]
        if missing_tools:
            print(f"⚠️  Missing tools: {missing_tools}")
        else:
            print("✅ All expected tools are registered!")

        return agent

    except Exception as e:
        print(f"❌ Error during tool registration test: {e}")
        logger.exception("Tool registration failed")
        return None


def test_basic_conversation(agent):
    """Test basic conversation functionality."""
    print("\n💬 Testing basic conversation...")

    try:
        test_messages = [
            "Hello! Can you tell me what tools you have available?",
            "What's 125 * 37?",
            "Can you help me understand what the weather tool can do?"
        ]

        for i, message in enumerate(test_messages, 1):
            print(f"\n📝 Test message {i}: {message}")
            try:
                response = agent.process_message(message)
                print(
                    f"🤖 Response: {response[:200]}{'...' if len(response) > 200 else ''}")
            except Exception as e:
                print(f"❌ Error processing message {i}: {e}")

    except Exception as e:
        print(f"❌ Error during conversation test: {e}")
        logger.exception("Conversation test failed")


def test_tool_capabilities(agent):
    """Test specific tool capabilities."""
    print("\n🧪 Testing specific tool capabilities...")

    # Test calculator
    try:
        print("\n🔢 Testing Calculator...")
        response = agent.process_message("Calculate 15 * 8 + 32")
        print(
            f"Calculator result: {response[:150]}{'...' if len(response) > 150 else ''}")
    except Exception as e:
        print(f"❌ Calculator test failed: {e}")

    # Test weather tool help
    try:
        print("\n🌤️  Testing Weather Tool Help...")
        response = agent.process_message("Show me help for the weather tool")
        print(
            f"Weather help: {response[:200]}{'...' if len(response) > 200 else ''}")
    except Exception as e:
        print(f"❌ Weather tool test failed: {e}")

    # Test file operations
    try:
        print("\n📁 Testing File Operations...")
        response = agent.process_message(
            "List the files in the current directory")
        print(
            f"File listing: {response[:200]}{'...' if len(response) > 200 else ''}")
    except Exception as e:
        print(f"❌ File operations test failed: {e}")


def main():
    """Main test function."""
    print("🚀 Starting Enhanced AI Agent Test Suite")
    print("=" * 50)

    # Test tool registration
    agent = test_tool_registration()

    if agent is None:
        print("❌ Cannot continue tests - agent initialization failed")
        return False

    # Test basic conversation
    test_basic_conversation(agent)

    # Test tool capabilities
    test_tool_capabilities(agent)

    print("\n" + "=" * 50)
    print("✅ Enhanced AI Agent test suite completed!")
    print("📊 Check the output above for any issues or errors.")
    print("\n💡 Next steps:")
    print("   1. Add OPENWEATHER_API_KEY to .env for weather functionality")
    print("   2. Configure Slack token for Slack integration")
    print("   3. Try interacting with the agent using main.py")

    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
