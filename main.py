#!/usr/bin/env python3
"""
Main CLI interface for the Python AI Agent.
"""

from src.config import Config
from src.agent import Agent
import sys
import os
import argparse
from pathlib import Path

# Add src to path so we can import our modules
sys.path.insert(0, str(Path(__file__).parent / "src"))


def print_banner():
    """Print the agent banner."""
    print("=" * 60)
    print("🤖 Python AI Agent")
    print("=" * 60)
    print("Type 'exit', 'quit', or 'bye' to end the conversation")
    print("Type 'clear' to clear conversation history")
    print("Type 'tools' to see available tools")
    print("Type 'help' for this help message")
    print("=" * 60)


def main():
    """Main entry point for the agent CLI."""
    parser = argparse.ArgumentParser(description="Python AI Agent CLI")
    parser.add_argument("--provider", choices=["anthropic", "openai", "local"],
                        help="LLM provider to use")
    parser.add_argument("--model", help="Model to use")
    parser.add_argument("--verbose", action="store_true",
                        help="Enable verbose logging")

    args = parser.parse_args()

    # Check for environment file
    env_file = Path(".env")
    if not env_file.exists():
        print("⚠️  No .env file found. Please create one based on .env.example")
        print("   Set your API key (ANTHROPIC_API_KEY or OPENAI_API_KEY)")
        return 1

    try:
        # Create config
        config = Config()

        # Override config with command line arguments
        if args.provider:
            config.llm_provider = args.provider
        if args.model:
            if config.llm_provider == "anthropic":
                config.anthropic_model = args.model
            else:
                config.openai_model = args.model

        # Initialize agent
        print("🚀 Initializing agent...")
        agent = Agent(config)

        print(
            f"✅ Agent ready! Using {config.llm_provider} with model {config.current_model}")
        print(f"📋 Available tools: {', '.join(agent.get_available_tools())}")

        print_banner()

        # Main conversation loop
        while True:
            try:
                user_input = input("\n👤 You: ").strip()

                if not user_input:
                    continue

                # Handle special commands
                if user_input.lower() in ['exit', 'quit', 'bye']:
                    print("👋 Goodbye!")
                    break
                elif user_input.lower() == 'clear':
                    agent.clear_conversation()
                    print("🧹 Conversation cleared!")
                    continue
                elif user_input.lower() == 'tools':
                    print("\n🔧 " + agent.tool_registry.list_tools())
                    continue
                elif user_input.lower() == 'help':
                    print_banner()
                    continue

                # Process the message
                print("🤖 Assistant:", end=" ", flush=True)
                response = agent.process_message(user_input)
                print(response)

            except KeyboardInterrupt:
                print("\n\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"\n❌ Error: {e}")
                if args.verbose:
                    import traceback
                    traceback.print_exc()

    except Exception as e:
        print(f"❌ Failed to initialize agent: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
