"""Todo list manager tool for managing simple todo items."""

import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Optional
import logging
from .base import Tool

logger = logging.getLogger(__name__)


class TodoManagerTool(Tool):
    """A tool for managing simple todo lists with categories and priorities."""
    
    def __init__(self, todos_file: str = "todos.json"):
        super().__init__(
            name="todo_manager",
            description="Manage todo lists with categories. Operations: add, list, complete, delete, clear, stats"
        )
        self.todos_file = Path(todos_file)
        self._load_todos()
    
    def _load_todos(self):
        """Load todos from the JSON file."""
        if self.todos_file.exists():
            try:
                with open(self.todos_file, 'r') as f:
                    self.todos = json.load(f)
            except json.JSONDecodeError:
                logger.error(f"Error loading todos from {self.todos_file}")
                self.todos = []
        else:
            self.todos = []
    
    def _save_todos(self):
        """Save todos to the JSON file."""
        with open(self.todos_file, 'w') as f:
            json.dump(self.todos, f, indent=2)
    
    def execute(self, operation: str, **kwargs) -> str:
        """Execute a todo operation."""
        try:
            if operation == "add":
                return self._add_todo(
                    kwargs.get('item'),
                    kwargs.get('category', 'general'),
                    kwargs.get('priority', 'normal')
                )
            elif operation == "list":
                return self._list_todos(
                    kwargs.get('category'),
                    kwargs.get('status', 'pending')
                )
            elif operation == "complete":
                return self._complete_todo(kwargs.get('todo_id'))
            elif operation == "delete":
                return self._delete_todo(kwargs.get('todo_id'))
            elif operation == "clear":
                return self._clear_completed()
            elif operation == "stats":
                return self._get_stats()
            else:
                return f"Error: Unknown operation '{operation}'. Available: add, list, complete, delete, clear, stats"
        except Exception as e:
            logger.error(f"Todo manager error: {e}")
            return f"Error executing {operation}: {str(e)}"
    
    def _add_todo(self, item: str, category: str = 'general', priority: str = 'normal') -> str:
        """Add a new todo item."""
        if not item:
            return "Error: Todo item text is required"
        
        todo = {
            'id': len(self.todos) + 1,
            'item': item,
            'category': category.lower(),
            'priority': priority.lower(),
            'status': 'pending',
            'created_at': datetime.now().isoformat()
        }
        
        self.todos.append(todo)
        self._save_todos()
        
        priority_emoji = {'high': '🔴', 'normal': '🟡', 'low': '🟢'}.get(priority.lower(), '⚪')
        
        return f"✅ Todo added!\n" \
               f"ID: {todo['id']}\n" \
               f"Item: {todo['item']}\n" \
               f"Category: {todo['category']}\n" \
               f"Priority: {priority_emoji} {todo['priority']}"
    
    def _list_todos(self, category: Optional[str] = None, status: str = 'pending') -> str:
        """List todos filtered by category and status."""
        filtered_todos = self.todos
        
        # Filter by status
        if status != 'all':
            filtered_todos = [t for t in filtered_todos if t['status'] == status]
        
        # Filter by category
        if category:
            filtered_todos = [t for t in filtered_todos if t['category'] == category.lower()]
        
        if not filtered_todos:
            return f"📋 No {status} todos" + (f" in category '{category}'" if category else "")
        
        # Group by category
        categories = {}
        for todo in filtered_todos:
            cat = todo['category']
            if cat not in categories:
                categories[cat] = []
            categories[cat].append(todo)
        
        result = f"📋 Todo List ({status})" + (f" - Category: {category}" if category else "") + ":\n\n"
        
        for cat, todos in sorted(categories.items()):
            result += f"📁 {cat.upper()}\n"
            for todo in todos:
                status_mark = '✅' if todo['status'] == 'completed' else '⬜'
                priority_emoji = {'high': '🔴', 'normal': '🟡', 'low': '🟢'}.get(todo['priority'], '⚪')
                result += f"  {status_mark} [{todo['id']}] {todo['item']} {priority_emoji}\n"
            result += "\n"
        
        return result
    
    def _complete_todo(self, todo_id: int) -> str:
        """Mark a todo as completed."""
        for todo in self.todos:
            if todo['id'] == todo_id:
                if todo['status'] == 'completed':
                    return f"Todo {todo_id} is already completed"
                
                todo['status'] = 'completed'
                todo['completed_at'] = datetime.now().isoformat()
                self._save_todos()
                return f"✅ Todo {todo_id} '{todo['item']}' marked as completed!"
        
        return f"Error: Todo with ID {todo_id} not found"
    
    def _delete_todo(self, todo_id: int) -> str:
        """Delete a todo item."""
        for i, todo in enumerate(self.todos):
            if todo['id'] == todo_id:
                deleted_todo = self.todos.pop(i)
                self._save_todos()
                return f"🗑️ Todo {todo_id} '{deleted_todo['item']}' deleted"
        
        return f"Error: Todo with ID {todo_id} not found"
    
    def _clear_completed(self) -> str:
        """Clear all completed todos."""
        original_count = len(self.todos)
        self.todos = [t for t in self.todos if t['status'] != 'completed']
        cleared_count = original_count - len(self.todos)
        
        if cleared_count > 0:
            self._save_todos()
            return f"🧹 Cleared {cleared_count} completed todo(s)"
        else:
            return "No completed todos to clear"
    
    def _get_stats(self) -> str:
        """Get statistics about todos."""
        if not self.todos:
            return "📊 No todos to analyze"
        
        total = len(self.todos)
        completed = len([t for t in self.todos if t['status'] == 'completed'])
        pending = total - completed
        
        # Count by category
        categories = {}
        priorities = {'high': 0, 'normal': 0, 'low': 0}
        
        for todo in self.todos:
            if todo['status'] == 'pending':
                cat = todo['category']
                categories[cat] = categories.get(cat, 0) + 1
                priorities[todo['priority']] = priorities.get(todo['priority'], 0) + 1
        
        result = "📊 Todo Statistics:\n\n"
        result += f"Total todos: {total}\n"
        result += f"✅ Completed: {completed} ({completed/total*100:.1f}%)\n"
        result += f"⏳ Pending: {pending} ({pending/total*100:.1f}%)\n\n"
        
        if categories:
            result += "📁 Pending by category:\n"
            for cat, count in sorted(categories.items(), key=lambda x: x[1], reverse=True):
                result += f"  {cat}: {count}\n"
            result += "\n"
        
        if any(priorities.values()):
            result += "🎯 Pending by priority:\n"
            result += f"  🔴 High: {priorities['high']}\n"
            result += f"  🟡 Normal: {priorities['normal']}\n"
            result += f"  🟢 Low: {priorities['low']}\n"
        
        return result
    
    def get_schema(self) -> Dict[str, Any]:
        """Get the JSON schema for this tool's parameters."""
        return {
            "type": "object",
            "properties": {
                "operation": {
                    "type": "string",
                    "enum": ["add", "list", "complete", "delete", "clear", "stats"],
                    "description": "Operation: add (new todo), list (show todos), complete (mark done), delete (remove), clear (remove completed), stats (statistics)"
                },
                "item": {
                    "type": "string",
                    "description": "Todo item text (required for add)"
                },
                "category": {
                    "type": "string",
                    "description": "Category for the todo (default: general)"
                },
                "priority": {
                    "type": "string",
                    "enum": ["high", "normal", "low"],
                    "description": "Priority level (default: normal)"
                },
                "status": {
                    "type": "string",
                    "enum": ["all", "pending", "completed"],
                    "description": "Filter for list operation (default: pending)"
                },
                "todo_id": {
                    "type": "integer",
                    "description": "Todo ID for complete/delete operations"
                }
            },
            "required": ["operation"]
        }