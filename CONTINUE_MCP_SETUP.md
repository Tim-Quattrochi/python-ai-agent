# Continue Extension MCP Setup

This guide expl### 4. Verify Integration

1. Open VS Code
2. Open the Continue chat panel in VS Code
3. Start a conversation
4. The tools should now be available as MCP tools
5. Look for the MCP tools icon in the Continue interface
6. Try using the tools directly through Continue's natural language interface:
   - "Calculate 15 times 24"
   - "Search the web for latest Python features"  
   - "Read the contents of README.md file"
   - "List the files in the src directory"t up the Python AI Agent as an MCP (Model Context Protocol) server for the Continue VS Code extension.

## What You Get

When integrated with Continue, you'll have access to these tools directly in your VS Code chat:

- **Calculator**: Perform mathematical calculations
- **Web Search**: Search the web for current information
- **File Operations**: Read, write, and list files
- **Directory Listing**: Browse directory contents

## Setup Steps

### 1. Prerequisites

- VS Code with Continue extension installed
- Python AI Agent properly set up with virtual environment
- MCP dependencies installed (already done)

### 2. Continue Configuration

The Continue extension uses the same MCP configuration format as Claude for Desktop. The configuration has been automatically added to your `~/.continue/config.json` file:

```json
{
  "mcpServers": {
    "python-ai-agent": {
      "command": "/Users/timq8/python-ai-agent/venv/bin/python",
      "args": ["/Users/timq8/python-ai-agent/mcp_standalone.py"],
      "env": {
        "PYTHONPATH": "/Users/timq8/python-ai-agent"
      }
    }
  }
}
```

This configuration tells Continue:

1. There's an MCP server named "python-ai-agent"
2. To launch it using the virtual environment Python interpreter
3. Running the standalone MCP server script
4. With the proper Python path for imports

### 3. Restart Continue Extension

After updating the configuration:

1. Open VS Code
2. Reload the window (`Cmd+Shift+P` → "Developer: Reload Window")
3. Or restart VS Code completely

### 4. Verify Integration

1. Open the Continue chat panel in VS Code
2. Start a conversation
3. Try using the tools:
   - `@python-ai-agent calculator 15 * 24`
   - `@python-ai-agent web_search latest Python features`
   - `@python-ai-agent read_file /path/to/some/file.txt`

## Troubleshooting

### Server Not Starting

If the MCP server doesn't start:

1. Check that the virtual environment exists:

   ```bash
   ls /Users/timq8/python-ai-agent/venv/bin/python
   ```

2. Test the server manually:

   ```bash
   cd /Users/timq8/python-ai-agent
   source venv/bin/activate
   python mcp_server.py --verbose
   ```

3. Check Continue extension logs:
   - Open VS Code Developer Tools (`Cmd+Shift+P` → "Developer: Toggle Developer Tools")
   - Look for MCP-related errors in the console

### Tools Not Working

If tools don't respond correctly:

1. Verify all dependencies are installed:

   ```bash
   cd /Users/timq8/python-ai-agent
   source venv/bin/activate
   pip list | grep -E "(mcp|requests|duckduckgo)"
   ```

2. Run the test suite:

   ```bash
   cd /Users/timq8/python-ai-agent
   source venv/bin/activate
   python test_mcp.py
   ```

### Event Loop Issues

The server now properly handles event loop conflicts that can occur in VS Code environments. If you still encounter issues:

1. Check the logs for "Already running in an event loop" messages
2. The server automatically switches to `run_sync()` mode for VS Code compatibility

## Available Tools

### Calculator

```
@python-ai-agent calculator <expression>
```

Examples:

- `@python-ai-agent calculator 2 + 2`
- `@python-ai-agent calculator sqrt(16) * 5`
- `@python-ai-agent calculator sin(pi/2)`

### Web Search

```
@python-ai-agent web_search <query>
```

Examples:

- `@python-ai-agent web_search Python 3.12 new features`
- `@python-ai-agent web_search machine learning trends 2024`

### File Operations

```
@python-ai-agent read_file <file_path>
@python-ai-agent write_file <file_path> <content>
@python-ai-agent list_directory <directory_path>
```

Examples:

- `@python-ai-agent read_file ./config.json`
- `@python-ai-agent write_file ./output.txt "Hello World"`
- `@python-ai-agent list_directory ./src`

## Configuration Details

The MCP server configuration includes:

- **Command**: Uses the virtual environment Python
- **Args**: Points to the standalone MCP server script
- **Environment**: Sets PYTHONPATH for proper imports
- **Event Loop**: Handles both sync and async execution contexts

## Next Steps

1. Try the tools in Continue chat
2. Customize the tool responses for your specific needs
3. Add more tools by extending `src/mcp_server.py`
4. Create tool combinations for complex workflows

## Support

If you encounter issues:

1. Check the terminal output when running the server manually
2. Look at Continue extension logs in VS Code Developer Tools
3. Verify the configuration matches your actual file paths
4. Test individual tools using the test suite

The MCP integration provides a powerful way to extend Continue with your AI agent's capabilities!
