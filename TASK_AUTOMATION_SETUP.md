# Task Automation Tools Setup and Usage Guide

## Overview of New Tools

The Python AI Agent now includes three powerful task automation tools:
1. Task Scheduler
2. Email Sender
3. Todo Manager

### Prerequisites

- Python 3.8+
- Existing Python AI Agent installation
- (Optional) Email account with SMTP access

## 1. Task Scheduler Tool

### Purpose
Manage and schedule tasks with advanced features like:
- Create tasks with titles and due dates
- Set task priorities
- List and track tasks
- Mark tasks as complete
- Track overdue tasks

### Usage Examples

```python
# Schedule a task
agent.process_message("Schedule a task to review project next Monday")
# Output: Task scheduled with ID, details, and due date

# List tasks
agent.process_message("List my tasks")
# Output: Shows all pending tasks

# Complete a task
agent.process_message("Complete task 1")
# Output: Task marked as completed

# Show overdue tasks
agent.process_message("Show overdue tasks")
# Output: List of tasks past their due date
```

### Supported Operations
- `schedule`: Create a new task
- `list`: Show tasks (can filter by status)
- `complete`: Mark a task as done
- `delete`: Remove a task
- `overdue`: Show tasks past their due date

### Date Parsing Flexibility
- Absolute dates: "2024-03-25"
- Relative dates: "tomorrow", "next week", "in 5 days"

## 2. Email Sender Tool

### Purpose
Compose, draft, and send emails directly from the AI agent

### SMTP Configuration
Edit your `.env` file:
```bash
# Email Configuration
SMTP_HOST=smtp.gmail.com      # Your SMTP server
SMTP_PORT=587                 # Standard TLS port
SMTP_USER=your_email@gmail.com
SMTP_PASSWORD=your_app_password
FROM_EMAIL=your_email@gmail.com
```

#### Gmail Setup (Recommended)
1. Enable 2-Factor Authentication
2. Generate an App Password:
   - Go to Google Account > Security
   - Find "App passwords"
   - Select "Mail" and your device
   - Use generated password in SMTP_PASSWORD

### Usage Examples

```python
# Draft an email
agent.process_message("Draft an email to team about project update")
# Output: Draft saved with ID

# Send a draft
agent.process_message("Send draft 0 to team@company.com")
# Output: Email sent successfully

# Compose and send in one step
agent.process_message("Send email to john@example.com with subject 'Weekly Report' and body 'Here is the report'")
# Output: Email sent successfully
```

### Supported Operations
- `send`: Send an email
- `draft`: Save an email draft
- `list_drafts`: Show saved email drafts

## 3. Todo Manager Tool

### Purpose
Manage personal todo lists with categorization and priority tracking

### Usage Examples

```python
# Add a todo
agent.process_message("Add a todo to review quarterly reports")
# Output: Todo added with ID, category, priority

# List todos
agent.process_message("List my todos")
# Output: Shows todos, grouped by category

# Complete a todo
agent.process_message("Complete todo 1")
# Output: Todo marked as completed

# Get todo statistics
agent.process_message("Show todo stats")
# Output: Breakdown of todos by status and priority
```

### Supported Operations
- `add`: Create a new todo item
- `list`: Show todos (can filter by category/status)
- `complete`: Mark a todo as done
- `delete`: Remove a todo
- `clear`: Remove all completed todos
- `stats`: Get todo list statistics

## Configuration and Persistence

### Task and Todo Storage
- Tasks are stored in `scheduled_tasks.json`
- Todos are stored in `todos.json`
- Persistent between agent sessions
- Can be manually edited or backed up

## Best Practices

1. Use clear, specific task and todo descriptions
2. Leverage relative and absolute date parsing
3. Regularly review and update tasks/todos
4. Use categories and priorities for better organization

## Troubleshooting

### Email Sending Issues
- Verify SMTP settings
- Check app password
- Ensure less secure app access is enabled
- Check network/firewall settings

### Task/Todo Tracking
- Check JSON files for manual intervention
- Ensure proper date formats
- Restart agent if unexpected behavior occurs

## Security Considerations

- Store `.env` file securely
- Do not share SMTP credentials
- Use app passwords instead of account passwords
- Regularly rotate app passwords

## Extensibility

These tools are designed to be easily extended. You can:
- Add more date parsing formats
- Implement more complex scheduling logic
- Create custom storage backends
- Add notification mechanisms

## Changelog

### v1.1.0 - Task Automation Update
- Added TaskSchedulerTool
- Added EmailSenderTool
- Added TodoManagerTool
- Updated agent initialization
- Enhanced tool registration
- Improved conversation context handling

## Future Roadmap
- Calendar integration
- Advanced task recurrence
- Email template support
- Enhanced todo collaboration features