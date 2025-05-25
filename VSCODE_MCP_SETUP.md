# VS Code MCP Integration Setup Guide

## ✅ Configuration Complete

Your Python AI Agent MCP server is now configured to work with VS Code's Continue extension and GitHub Copilot.

### Files Created

1. **`.vscode/mcp.json`** - MCP server configuration for VS Code
2. **`.vscode/settings.json`** - VS Code settings to enable MCP support
3. **`run_mcp_server.sh`** - Wrapper script to run MCP server with proper environment

### How to Use

## 1. **Open VS Code in this workspace:**

```bash
cd /Users/timq8/python-ai-agent
code .
```

## 2. **Start the MCP Server:**

When you open VS Code, you should see a "Start Server" button in the `mcp.json` file editor. Click it to start the Python AI Agent MCP server.

Alternatively, you can:

- Open Command Palette (`Cmd+Shift+P`)
- Run: `MCP: Add Server` or `MCP: List Servers`

## 3. **Use MCP Tools in VS Code Chat:**

Once the server is running, open VS Code's chat panel:

- `Ctrl+Shift+I` (Windows/Linux) or `Cmd+Shift+I` (macOS)

Then you can use the tools by asking questions like:

- "Calculate 15% of 240" (uses calculator tool)
- "Search for latest Python news" (uses web_search tool)
- "Read the contents of README.md" (uses file operations)
- "Create a file called notes.txt with some content" (uses file operations)

## 4. **Managing Tools:**

- Use the **Tools button** in the Chat view to toggle specific tools on/off
- Add specific tools to your prompt using `#` followed by the tool name
- Type `#calculator`, `#web_search`, or `#file_operations` to use specific tools

## Available MCP Tools

- **calculator** - Perform mathematical calculations
- **web_search** - Search the web for information  
- **read_file** - Read file contents
- **write_file** - Write content to files
- **list_directory** - List directory contents

## Troubleshooting

### If the server doesn't start

1. Check VS Code version (requires 1.99+)
2. Ensure MCP support is enabled: Search for "chat.mcp.enabled" in settings
3. Check server logs: Command Palette → `MCP: List Servers` → Select server → "Show Output"
4. Verify the wrapper script works: `./run_mcp_server.sh --help`

### Common Issues

- **Permission denied**: Run `chmod +x run_mcp_server.sh`
- **Python not found**: Check that virtual environment exists: `ls venv/bin/python`
- **Import errors**: Ensure all dependencies are installed: `pip install -r requirements.txt`

### Environment Variables

Make sure your `.env` file is configured with necessary API keys:

- `ANTHROPIC_API_KEY` or `OPENAI_API_KEY` for LLM functionality
- `SERPAPI_KEY` for web search (optional)

## Testing the Integration

Run this test to verify everything works:

```bash
./run_mcp_server.sh --verbose
```

The server should start and show:

```
Starting Python AI Agent MCP Server...
Registered CalculatorTool
Registered WebSearchTool  
Registered FileOperationsTool
```

## VS Code MCP Features

- **Auto-discovery**: VS Code can detect MCP servers defined in other tools
- **Tool management**: Toggle tools on/off in chat interface  
- **Context integration**: Tools work seamlessly with GitHub Copilot
- **Error handling**: Built-in error reporting and logging
- **Workspace sharing**: Team members can use the same MCP configuration

Your Python AI Agent is now fully integrated with VS Code! 🎉
