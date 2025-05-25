#!/usr/bin/env python3
"""
Local Llama.cpp integration with Python AI Agent.
"""

from src.agent import Agent
from src.config import Config
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))


def main():
    """Run the agent with local Llama.cpp server."""

    # Create config for local provider
    config = Config()
    config.llm_provider = "local"  # You'll need to add this to your config

    # Initialize agent with all your existing tools
    agent = Agent(config)

    print("🤖 Python AI Agent with Local Llama.cpp")
    print(f"📋 Available tools: {', '.join(agent.get_available_tools())}")
    print("=" * 60)

    while True:
        try:
            user_input = input("\n👤 You: ").strip()

            if user_input.lower() in ['exit', 'quit', 'bye']:
                print("👋 Goodbye!")
                break

            # Use your full agent system with all tools
            response = agent.process_message(user_input)
            print(f"🤖 Assistant: {response}")

        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")


if __name__ == "__main__":
    main()
