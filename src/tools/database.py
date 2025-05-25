"""Database operations tool for SQL queries and data management."""

import sqlite3
import json
import os
from typing import Dict, Any, List
from .base import Tool


class DatabaseTool(Tool):
    """Tool for database operations."""

    def __init__(self, db_path: str = "agent_data.db"):
        super().__init__(
            name="database",
            description="Execute SQL queries, manage database tables, and store/retrieve data"
        )
        self.db_path = db_path
        self._init_database()

    def _init_database(self):
        """Initialize the database with basic tables."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS agent_data (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    key TEXT UNIQUE NOT NULL,
                    value TEXT NOT NULL,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS conversation_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_message TEXT NOT NULL,
                    agent_response TEXT NOT NULL,
                    tool_calls TEXT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)

    def execute(self, operation: str, **kwargs) -> str:
        """Execute database operations."""
        try:
            if operation == "query":
                return self._execute_query(kwargs.get('sql'), kwargs.get('params', []))
            elif operation == "store":
                return self._store_data(kwargs.get('key'), kwargs.get('value'))
            elif operation == "retrieve":
                return self._retrieve_data(kwargs.get('key'))
            elif operation == "list_tables":
                return self._list_tables()
            elif operation == "log_conversation":
                return self._log_conversation(
                    kwargs.get('user_message'),
                    kwargs.get('agent_response'),
                    kwargs.get('tool_calls')
                )
            else:
                return f"Error: Unknown operation '{operation}'"
        except Exception as e:
            return f"Database error: {str(e)}"

    def _execute_query(self, sql: str, params: List = None) -> str:
        """Execute a SQL query."""
        if not sql:
            return "Error: SQL query is required"

        # Safety check - only allow SELECT statements for security
        if not sql.strip().upper().startswith('SELECT'):
            return "Error: Only SELECT queries are allowed for security"

        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(sql, params or [])
            rows = cursor.fetchall()

            if not rows:
                return "No results found"

            # Convert to list of dictionaries
            results = [dict(row) for row in rows]
            return json.dumps(results, indent=2, default=str)

    def _store_data(self, key: str, value: str) -> str:
        """Store key-value data."""
        if not key or not value:
            return "Error: Both key and value are required"

        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "INSERT OR REPLACE INTO agent_data (key, value) VALUES (?, ?)",
                (key, value)
            )
            return f"✅ Stored data: {key} = {value}"

    def _retrieve_data(self, key: str) -> str:
        """Retrieve data by key."""
        if not key:
            return "Error: Key is required"

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                "SELECT value FROM agent_data WHERE key = ?", (key,))
            row = cursor.fetchone()

            if row:
                return f"📁 {key}: {row[0]}"
            else:
                return f"❌ No data found for key: {key}"

    def _list_tables(self) -> str:
        """List all tables in the database."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table'")
            tables = [row[0] for row in cursor.fetchall()]

            if tables:
                return f"📊 Database tables: {', '.join(tables)}"
            else:
                return "📊 No tables found in database"

    def _log_conversation(self, user_message: str, agent_response: str, tool_calls: str = None) -> str:
        """Log a conversation to the database."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "INSERT INTO conversation_logs (user_message, agent_response, tool_calls) VALUES (?, ?, ?)",
                (user_message, agent_response, tool_calls)
            )
            return "✅ Conversation logged"

    def get_schema(self) -> Dict[str, Any]:
        """Get the JSON schema for this tool."""
        return {
            "type": "object",
            "properties": {
                "operation": {
                    "type": "string",
                    "enum": ["query", "store", "retrieve", "list_tables", "log_conversation"],
                    "description": "Database operation to perform"
                },
                "sql": {
                    "type": "string",
                    "description": "SQL query for 'query' operation (SELECT only)"
                },
                "params": {
                    "type": "array",
                    "description": "Parameters for SQL query"
                },
                "key": {
                    "type": "string",
                    "description": "Key for store/retrieve operations"
                },
                "value": {
                    "type": "string",
                    "description": "Value for store operation"
                },
                "user_message": {
                    "type": "string",
                    "description": "User message for conversation logging"
                },
                "agent_response": {
                    "type": "string",
                    "description": "Agent response for conversation logging"
                },
                "tool_calls": {
                    "type": "string",
                    "description": "Tool calls made during conversation"
                }
            },
            "required": ["operation"]
        }
