# Python AI Agent

A powerful, extensible AI agent built in Python that can use various tools to help you with calculations, web searches, file operations, and more. The agent supports both OpenAI and Anthropic (Claude) language models.

## Features

- 🤖 **Multi-Provider LLM Support**: Works with both OpenAI GPT and Anthropic Claude
- 🔧 **Extensible Tool System**: Easy to add new tools and capabilities
- 🧮 **Built-in Tools**:
  - Calculator for mathematical operations
  - Web search for finding information online
  - File operations for reading and writing files
- 💬 **Interactive CLI**: User-friendly command-line interface
- 🔒 **Security**: File operations with path validation and size limits
- 📚 **Conversation Memory**: Maintains context across the conversation

## Quick Start

### 1. Installation

```bash
# Clone or download the project
cd python-ai-agent

# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate  # On macOS/Linux
# or
venv\Scripts\activate     # On Windows

# Install dependencies
pip install -r requirements.txt
```

### 2. Configuration

Copy the example environment file and add your API keys:

```bash
cp .env.example .env
```

Edit `.env` file and add your API key:

```bash
# Choose your preferred provider
LLM_PROVIDER=anthropic  # or "openai"

# Add your API key
ANTHROPIC_API_KEY=your_anthropic_api_key_here
# OR
OPENAI_API_KEY=your_openai_api_key_here

# Optional: Customize models
ANTHROPIC_MODEL=claude-3-sonnet-20240229
OPENAI_MODEL=gpt-4-turbo-preview
```

### 3. Running the Agent

```bash
# Start the interactive agent
python main.py

# Or with specific options
python main.py --provider anthropic --verbose
```

## Getting API Keys

### Anthropic Claude API Key

1. Go to [Anthropic Console](https://console.anthropic.com/)
2. Sign up or log in
3. Navigate to API Keys section
4. Create a new API key
5. Copy the key to your `.env` file

### OpenAI API Key

1. Go to [OpenAI Platform](https://platform.openai.com/)
2. Sign up or log in
3. Navigate to API Keys section
4. Create a new API key
5. Copy the key to your `.env` file

## Usage Examples

### Basic Conversation

```
👤 You: Hello! What can you help me with?
🤖 Assistant: Hi! I'm an AI assistant with access to several useful tools...
```

### Calculator

```
👤 You: What's 15% of 240?
🤖 Assistant: I'll calculate 15% of 240 for you.
[Uses calculator tool]
The result is 36.
```

### Web Search

```
👤 You: What's the latest news about AI?
🤖 Assistant: I'll search for the latest AI news for you.
[Uses web search tool]
Here are some recent AI developments...
```

### File Operations

```
👤 You: Create a file called notes.txt with "Hello World"
🤖 Assistant: I'll create that file for you.
[Uses file operations tool]
Successfully created notes.txt with your content.
```

## Available Commands

In the interactive mode, you can use these special commands:

- `exit`, `quit`, `bye` - Exit the agent
- `clear` - Clear conversation history
- `tools` - List available tools
- `help` - Show help message

## Command Line Options

```bash
python main.py [options]

Options:
  --provider {anthropic,openai}  LLM provider to use
  --model MODEL                  Model to use
  --verbose                      Enable verbose logging
  --help                         Show help message
```

## Project Structure

```
python-ai-agent/
├── docs/
│   └── implementation-plan.md     # Development plan and progress
├── src/
│   ├── __init__.py
│   ├── agent.py                   # Main Agent class
│   ├── llm_client.py             # LLM client wrapper
│   ├── config.py                 # Configuration management
│   └── tools/
│       ├── __init__.py
│       ├── base.py               # Base tool classes
│       ├── calculator.py         # Calculator tool
│       ├── web_search.py         # Web search tool
│       └── file_ops.py           # File operations tool
├── tests/
│   ├── __init__.py
│   ├── test_agent.py
│   ├── test_tools.py
│   └── test_integration.py
├── main.py                       # CLI interface
├── requirements.txt              # Python dependencies
├── .env.example                  # Environment variables template
├── .gitignore                    # Git ignore file
└── README.md                     # This file
```

## Adding New Tools

To add a new tool, follow these steps:

1. Create a new file in `src/tools/` (e.g., `weather.py`)
2. Inherit from the `Tool` base class
3. Implement the required methods
4. Register the tool in `src/agent.py`

Example:

```python
from .base import Tool

class WeatherTool(Tool):
    def __init__(self):
        super().__init__(
            name="weather",
            description="Get current weather information for a location"
        )
    
    def execute(self, location: str) -> str:
        # Implement weather API call
        return f"Weather for {location}: ..."
    
    def get_schema(self) -> dict:
        return {
            "type": "object",
            "properties": {
                "location": {
                    "type": "string",
                    "description": "City or location name"
                }
            },
            "required": ["location"]
        }
```

## Security Features

- **File Path Validation**: File operations are restricted to safe paths
- **File Size Limits**: Maximum 1MB file size for safety
- **Extension Filtering**: Only allowed file types can be processed
- **Safe Expression Evaluation**: Calculator uses AST parsing for safety

## Troubleshooting

### Common Issues

1. **API Key Error**: Make sure your `.env` file has the correct API key
2. **Import Errors**: Ensure you're in the virtual environment and dependencies are installed
3. **Permission Errors**: For file operations, check file/directory permissions

### Debug Mode

Run with `--verbose` flag to see detailed error messages:

```bash
python main.py --verbose
```

## Development

### Running Tests

```bash
# Run all tests
pytest tests/

# Run specific test file
pytest tests/test_tools.py

# Run with coverage
pytest --cov=src tests/
```

### Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Submit a pull request

## License

This project is open source. Feel free to use and modify as needed.

## Support

For issues or questions:

1. Check the troubleshooting section
2. Review the implementation plan in `docs/`
3. Create an issue with detailed information
