# 🚀 Python AI Agent - Tool Development Guide

## Current Tools Overview

Your AI agent already has these impressive tools:

### Core Tools ✅

- **calculator** - Mathematical calculations
- **web_search** - Web search using SERP API
- **file_operations** - File reading/writing operations

### Task Automation Tools ✅

- **task_scheduler** - Schedule and manage tasks
- **email_sender** - Send emails via SMTP
- **todo_manager** - Manage todo lists

### Data & Development Tools ✅

- **database** - Database operations
- **image_processing** - Image manipulation with PIL
- **github** - GitHub repository management
- **ml_tool** - Machine learning operations
- **system_monitor** - System monitoring
- **content_generator** - Content generation
- **slack_integration** - Slack messaging

## 🔧 How to Add New Tools

### 1. Tool Architecture Pattern

Every tool follows this pattern:

```python
from .base import Tool

class YourNewTool(Tool):
    def __init__(self):
        super().__init__(
            name="your_tool_name",
            description="What your tool does"
        )
        # Initialize any required services/APIs
    
    def execute(self, operation: str, **kwargs) -> str:
        """Execute tool operations."""
        try:
            if operation == "action1":
                return self._action1(kwargs.get('param'))
            elif operation == "action2":
                return self._action2(kwargs.get('param'))
            else:
                return f"Unknown operation: {operation}"
        except Exception as e:
            return f"Error: {str(e)}"
    
    def _action1(self, param):
        """Implement specific action."""
        # Your logic here
        return "Result"
```

### 2. Register Your Tool

Add to `src/agent.py`:

```python
from .tools.your_new_tool import YourNewTool

# In _register_tools method:
self.register_tool(YourNewTool())
```

## 💡 Ideas for New Tools

### Communication & Social

```python
# Discord Bot Tool
class DiscordTool(Tool):
    # Send messages, manage servers, get user info

# WhatsApp/SMS Tool  
class MessagingTool(Tool):
    # Send SMS, WhatsApp messages via Twilio

# Social Media Tool
class SocialMediaTool(Tool):
    # Post to Twitter, LinkedIn, Instagram
```

### Productivity & Automation

```python
# PDF Operations Tool
class PDFTool(Tool):
    # Merge, split, extract text, convert to/from PDF

# Excel/Spreadsheet Tool
class SpreadsheetTool(Tool):
    # Read/write Excel, create charts, data analysis

# QR Code Generator
class QRCodeTool(Tool):
    # Generate QR codes, decode QR codes

# Calendar Integration
class CalendarTool(Tool):
    # Google Calendar, Outlook integration
```

### Development & DevOps

```python
# Docker Management Tool
class DockerTool(Tool):
    # Manage containers, build images, docker-compose

# AWS/Cloud Tool
class CloudTool(Tool):
    # Manage EC2, S3, Lambda functions

# Git Operations Tool (extended)
class GitTool(Tool):
    # Local git operations, branch management

# API Testing Tool
class APITestTool(Tool):
    # Test REST APIs, validate responses
```

### Data & Analytics

```python
# Data Visualization Tool
class DataVizTool(Tool):
    # Create charts with matplotlib, plotly

# Web Scraping Tool
class ScrapingTool(Tool):
    # Scrape websites, extract data

# SQL Query Tool
class SQLTool(Tool):
    # Execute SQL queries, database analysis

# CSV/JSON Tool
class DataFormatTool(Tool):
    # Convert between formats, validate data
```

### Multimedia & Creative

```python
# Video Processing Tool
class VideoTool(Tool):
    # Edit videos, extract frames, convert formats

# Audio Processing Tool
class AudioTool(Tool):
    # Edit audio, convert formats, speech-to-text

# Text-to-Speech Tool
class TTSTool(Tool):
    # Convert text to speech, voice synthesis

# OCR Tool
class OCRTool(Tool):
    # Extract text from images, PDFs
```

### Security & Utilities

```python
# Password Manager Tool
class PasswordTool(Tool):
    # Generate secure passwords, store encrypted

# Encryption Tool
class CryptoTool(Tool):
    # Encrypt/decrypt files, hash functions

# Network Scanner Tool
class NetworkTool(Tool):
    # Scan networks, port scanning, ping

# File Hash Tool
class HashTool(Tool):
    # Calculate file hashes, verify integrity
```

## 🛠️ Step-by-Step: Creating a New Tool

Let's create a **Weather Tool** as an example:

### Step 1: Create the Tool File

```bash
touch src/tools/weather.py
```

### Step 2: Implement the Tool

```python
# src/tools/weather.py
import os
import requests
from typing import Dict, Any
from .base import Tool

class WeatherTool(Tool):
    def __init__(self):
        super().__init__(
            name="weather",
            description="Get weather information for any location"
        )
        self.api_key = os.getenv('OPENWEATHER_API_KEY')
        self.base_url = "http://api.openweathermap.org/data/2.5"
    
    def execute(self, operation: str, **kwargs) -> str:
        if operation == "current":
            return self._get_current_weather(kwargs.get('location'))
        elif operation == "forecast":
            return self._get_forecast(kwargs.get('location'))
        else:
            return "Available operations: current, forecast"
    
    def _get_current_weather(self, location: str) -> str:
        if not location:
            return "Error: Location is required"
        
        try:
            url = f"{self.base_url}/weather"
            params = {
                'q': location,
                'appid': self.api_key,
                'units': 'metric'
            }
            
            response = requests.get(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            
            return f"🌤️ Weather in {data['name']}:\n" \
                   f"Temperature: {data['main']['temp']}°C\n" \
                   f"Feels like: {data['main']['feels_like']}°C\n" \
                   f"Description: {data['weather'][0]['description']}\n" \
                   f"Humidity: {data['main']['humidity']}%"
                   
        except Exception as e:
            return f"Error getting weather: {str(e)}"
```

### Step 3: Register the Tool

Add to `src/agent.py`:

```python
from .tools.weather import WeatherTool

# In _register_tools method:
self.register_tool(WeatherTool())
```

### Step 4: Add Environment Variable

Add to `.env`:

```bash
OPENWEATHER_API_KEY=your_api_key_here
```

### Step 5: Test Your Tool

```bash
source venv/bin/activate
python main.py

# Test commands:
# "What's the weather in New York?"
# "Get current weather for London"
```

## 🧪 Testing New Tools

### Create Unit Tests

```python
# tests/test_your_tool.py
import pytest
from src.tools.your_tool import YourTool

def test_tool_initialization():
    tool = YourTool()
    assert tool.name == "your_tool_name"

def test_tool_operation():
    tool = YourTool()
    result = tool.execute("test_operation", param="test")
    assert "expected_result" in result
```

### Manual Testing

```python
# Quick test script
from src.tools.your_tool import YourTool

tool = YourTool()
print(tool.execute("operation", param="value"))
```

## 📦 Dependencies Management

When adding new tools, update `requirements.txt`:

```bash
# For weather tool
requests==2.31.0

# For image processing  
Pillow==10.0.0

# For PDF operations
PyPDF2==3.0.1

# For Excel operations
openpyxl==3.1.2
pandas==2.0.3

# For Discord
discord.py==2.3.2

# For machine learning
scikit-learn==1.3.0
numpy==1.24.3
```

## 🔐 Environment Variables

Add new API keys to `.env.example`:

```bash
# Weather API
OPENWEATHER_API_KEY=your_openweather_key

# Discord Bot
DISCORD_BOT_TOKEN=your_discord_token

# AWS Credentials
AWS_ACCESS_KEY_ID=your_aws_key
AWS_SECRET_ACCESS_KEY=your_aws_secret

# Twilio (SMS)
TWILIO_ACCOUNT_SID=your_twilio_sid
TWILIO_AUTH_TOKEN=your_twilio_token
```

## 🚀 Advanced Features

### Tool Chaining

Tools can call other tools:

```python
def execute(self, operation: str, **kwargs) -> str:
    if operation == "analyze_and_send":
        # Use ML tool for analysis
        analysis = self.agent.tool_registry.get_tool("ml_tool").execute(
            "analyze", data=kwargs.get('data')
        )
        
        # Send results via email
        email_result = self.agent.tool_registry.get_tool("email_sender").execute(
            "send", 
            to=kwargs.get('recipient'),
            subject="Analysis Results",
            body=analysis
        )
        
        return f"Analysis completed and sent: {email_result}"
```

### Async Operations

For long-running tasks:

```python
import asyncio
from concurrent.futures import ThreadPoolExecutor

class AsyncTool(Tool):
    def __init__(self):
        super().__init__()
        self.executor = ThreadPoolExecutor()
    
    def execute(self, operation: str, **kwargs) -> str:
        if operation == "long_task":
            # Run in background
            future = self.executor.submit(self._long_running_task, kwargs)
            return "Task started in background..."
```

### Configuration-Based Tools

```python
class ConfigurableTool(Tool):
    def __init__(self):
        super().__init__()
        # Load tool-specific config
        self.config = self._load_config()
    
    def _load_config(self):
        config_file = "tool_configs/my_tool.json"
        if os.path.exists(config_file):
            with open(config_file) as f:
                return json.load(f)
        return {}
```

## 📚 Best Practices

1. **Error Handling**: Always wrap operations in try-catch
2. **Input Validation**: Validate all parameters before use
3. **Logging**: Add logging for debugging
4. **Documentation**: Document all operations and parameters
5. **Security**: Never expose sensitive data in responses
6. **Rate Limiting**: Respect API rate limits
7. **Caching**: Cache expensive operations when possible

## 🎯 Next Steps

1. **Choose 2-3 tools** from the ideas above that interest you most
2. **Create them one by one** following the pattern
3. **Test thoroughly** with your agent
4. **Document the operations** for users
5. **Add error handling** and validation
6. **Consider tool interactions** for powerful workflows

Your AI agent architecture is excellent and very extensible! The sky's the limit for what you can add. 🚀
