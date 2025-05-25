"""Task scheduler tool for scheduling and managing tasks."""

import json
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, List, Optional
import logging
from .base import Tool

logger = logging.getLogger(__name__)


class TaskSchedulerTool(Tool):
    """A tool for scheduling and managing tasks with due dates and reminders."""

    def __init__(self, tasks_file: str = "scheduled_tasks.json"):
        super().__init__(
            name="task_scheduler",
            description="Schedule tasks with due dates, set reminders, and manage scheduled tasks. Operations: schedule, list, complete, delete, overdue"
        )
        self.tasks_file = Path(tasks_file)
        self.tasks = []  # Reset tasks for each instance
        self._load_tasks()

    def _load_tasks(self):
        """Load tasks from the JSON file."""
        if self.tasks_file.exists():
            try:
                with open(self.tasks_file, 'r') as f:
                    loaded_tasks = json.load(f)
                    # Ensure unique IDs by finding the max ID
                    if loaded_tasks:
                        max_id = max(task.get('id', 0)
                                     for task in loaded_tasks)
                        for task in loaded_tasks:
                            task['id'] = task.get('id', max_id + 1)
                    self.tasks = loaded_tasks
            except json.JSONDecodeError:
                logger.error(f"Error loading tasks from {self.tasks_file}")
                self.tasks = []  # Initialize to empty list on error
        else:
            self.tasks = []

    def _save_tasks(self):
        """Save tasks to the JSON file with deduplication."""
        # Remove any duplicates based on title and due date
        unique_tasks = []
        seen = set()
        for task in self.tasks:
            task_key = (task['title'], task['due_date'])
            if task_key not in seen:
                seen.add(task_key)
                unique_tasks.append(task)

        # Ensure unique IDs
        for i, task in enumerate(unique_tasks, 1):
            task['id'] = i

        # Save the deduplicated tasks
        with open(self.tasks_file, 'w') as f:
            json.dump(unique_tasks, f, indent=2)

        # Update the tasks list with deduplicated version
        self.tasks = unique_tasks

    def execute(self, operation: str, **kwargs) -> str:
        """Execute a task scheduling operation."""
        try:
            if operation == "schedule":
                return self._schedule_task(
                    kwargs.get('title'),
                    kwargs.get('due_date'),
                    kwargs.get('description'),
                    kwargs.get('priority', 'medium')
                )
            elif operation == "list":
                return self._list_tasks(kwargs.get('status', 'all'))
            elif operation == "complete":
                return self._complete_task(kwargs.get('task_id'))
            elif operation == "delete":
                return self._delete_task(kwargs.get('task_id'))
            elif operation == "overdue":
                return self._list_overdue_tasks()
            else:
                return f"Error: Unknown operation '{operation}'. Available: schedule, list, complete, delete, overdue"
        except Exception as e:
            logger.error(f"Task scheduler error: {e}")
            return f"Error executing {operation}: {str(e)}"

    def _schedule_task(self, title: str, due_date: str = None, description: Optional[str] = None, priority: str = 'medium') -> str:
        """Schedule a new task."""
        if not title:
            return "Error: Task title is required"

        # If no due date provided, default to tomorrow
        if not due_date:
            due_date = "tomorrow"

        # Parse due date
        try:
            due_datetime = None

            # First try relative date parsing (most common for natural language)
            try:
                due_datetime = self._parse_relative_date(due_date)
            except ValueError:
                # If relative parsing fails, try absolute date formats
                for fmt in ['%Y-%m-%d', '%Y-%m-%d %H:%M', '%d/%m/%Y', '%d-%m-%Y']:
                    try:
                        due_datetime = datetime.strptime(due_date, fmt)
                        break
                    except ValueError:
                        continue

                # If all parsing fails
                if due_datetime is None:
                    return f"Error: Could not parse due date '{due_date}'. Use formats like 'tomorrow', 'next week', '2025-05-25', etc."

        except Exception as e:
            return f"Error parsing date: {str(e)}"
        # Create task
        task = {
            'id': len(self.tasks) + 1,
            'title': title,
            'description': description or '',
            'due_date': due_datetime.isoformat(),
            'priority': priority,
            'status': 'pending',
            'created_at': datetime.now().isoformat()
        }

        self.tasks.append(task)
        self._save_tasks()

        return f"✅ Task scheduled successfully!\n" \
            f"ID: {task['id']}\n" \
            f"Title: {task['title']}\n" \
            f"Due: {due_datetime.strftime('%Y-%m-%d %H:%M')}\n" \
            f"Priority: {task['priority']}"

    def _parse_relative_date(self, date_str: str) -> datetime:
        """Parse relative date strings like 'tomorrow', 'next week', etc."""
        date_str = date_str.lower().strip()
        now = datetime.now()

        # Improved parsing with more flexible input
        try:
            # Handle "in X days/weeks/months"
            if date_str.startswith('in '):
                parts = date_str.split()
                if len(parts) >= 3:
                    amount = int(parts[1])
                    unit = parts[2]

                    if unit in ['day', 'days']:
                        return (now + timedelta(days=amount)).replace(hour=23, minute=59, second=59)
                    elif unit in ['week', 'weeks']:
                        return (now + timedelta(weeks=amount)).replace(hour=23, minute=59, second=59)
                    elif unit in ['month', 'months']:
                        return (now + timedelta(days=30*amount)).replace(hour=23, minute=59, second=59)

            # Original parsing logic
            if date_str == 'today':
                return now.replace(hour=23, minute=59, second=59)
            elif date_str == 'tomorrow':
                return (now + timedelta(days=1)).replace(hour=23, minute=59, second=59)
            elif date_str == 'next week':
                return (now + timedelta(weeks=1)).replace(hour=23, minute=59, second=59)
            elif date_str == 'next month':
                return (now + timedelta(days=30)).replace(hour=23, minute=59, second=59)

            # If no pattern matched, raise an error
            raise ValueError(f"Cannot parse relative date: {date_str}")

        except ValueError:
            # Re-raise ValueError as is
            raise
        except Exception as e:
            logger.error(f"Date parsing error: {e}")
            raise ValueError(
                f"Invalid date format. Use formats like 'in 3 days', 'tomorrow', 'next week'")

    def _list_tasks(self, status: str = 'all') -> str:
        """List tasks filtered by status."""
        if not self.tasks:
            return "📋 No tasks scheduled"

        filtered_tasks = self.tasks
        if status != 'all':
            filtered_tasks = [t for t in self.tasks if t['status'] == status]
        if not filtered_tasks:
            return f"📋 No {status} tasks found"

        # Sort by due date
        filtered_tasks.sort(key=lambda x: x['due_date'])

        result = f"📋 Tasks ({status}):\n\n"
        for task in filtered_tasks:
            due_date = datetime.fromisoformat(task['due_date'])
            status_emoji = '✅' if task['status'] == 'completed' else '⏰'
            priority_emoji = {'high': '🔴', 'medium': '🟡',
                              'low': '🟢'}.get(task['priority'], '⚪')

            result += f"{status_emoji} [{task['id']}] {task['title']}\n"
            result += f"   Due: {due_date.strftime('%Y-%m-%d %H:%M')}\n"
            result += f"   Priority: {priority_emoji} {task['priority']}\n"
            if task['description']:
                result += f"   Description: {task['description']}\n"
            result += "\n"

        return result

    def _complete_task(self, task_id: int) -> str:
        """Mark a task as completed."""
        for task in self.tasks:
            if task['id'] == task_id:
                if task['status'] == 'completed':
                    return f"Task {task_id} is already completed"

                task['status'] = 'completed'
                task['completed_at'] = datetime.now().isoformat()
                self._save_tasks()
                return f"✅ Task {task_id} '{task['title']}' marked as completed!"

        return f"Error: Task with ID {task_id} not found"

    def _delete_task(self, task_id: int) -> str:
        """Delete a task."""
        for i, task in enumerate(self.tasks):
            if task['id'] == task_id:
                deleted_task = self.tasks.pop(i)
                self._save_tasks()
                return f"🗑️ Task {task_id} '{deleted_task['title']}' deleted"

        return f"Error: Task with ID {task_id} not found"

    def _list_overdue_tasks(self) -> str:
        """List all overdue tasks."""
        now = datetime.now()
        overdue_tasks = []

        for task in self.tasks:
            if task['status'] == 'pending':
                due_date = datetime.fromisoformat(task['due_date'])
                if due_date < now:
                    overdue_tasks.append(task)

        if not overdue_tasks:
            return "✅ No overdue tasks!"

        overdue_tasks.sort(key=lambda x: x['due_date'])

        result = "⚠️ Overdue tasks:\n\n"
        for task in overdue_tasks:
            due_date = datetime.fromisoformat(task['due_date'])
            days_overdue = (now - due_date).days
            priority_emoji = {'high': '🔴', 'medium': '🟡',
                              'low': '🟢'}.get(task['priority'], '⚪')

            result += f"❗ [{task['id']}] {task['title']}\n"
            result += f"   Overdue by: {days_overdue} days\n"
            result += f"   Was due: {due_date.strftime('%Y-%m-%d')}\n"
            result += f"   Priority: {priority_emoji} {task['priority']}\n\n"
        return result

    def get_schema(self) -> Dict[str, Any]:
        """Get the JSON schema for this tool's parameters."""
        return {
            "type": "object",
            "properties": {
                "operation": {
                    "type": "string",
                    "enum": ["schedule", "list", "complete", "delete", "overdue"],
                    "description": "Operation to perform: schedule (create task), list (show tasks), complete (mark done), delete (remove task), overdue (show overdue)"
                },
                "title": {
                    "type": "string",
                    "description": "Task title (required for schedule)"
                },
                "due_date": {
                    "type": "string",
                    "description": "Due date in YYYY-MM-DD format or relative like 'tomorrow', 'next week' (required for schedule)"
                },
                "description": {
                    "type": "string",
                    "description": "Task description (optional)"
                },
                "priority": {
                    "type": "string",
                    "enum": ["high", "medium", "low"],
                    "description": "Task priority (default: medium)"
                },
                "status": {
                    "type": "string",
                    "enum": ["all", "pending", "completed"],
                    "description": "Filter for list operation (default: all)"
                },
                "task_id": {
                    "type": "integer",
                    "description": "Task ID for complete/delete operations"
                }
            },
            "required": ["operation"]
        }
