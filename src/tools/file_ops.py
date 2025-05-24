"""File operations tool for reading and writing files."""

import os
from pathlib import Path
from typing import Dict, Any
import logging
from .base import Tool

logger = logging.getLogger(__name__)


class FileOperationsTool(Tool):
    """A tool for file system operations like reading and writing files."""

    def __init__(self):
        super().__init__(
            name="file_operations",
            description="Read from and write to files. Supports text files and basic file operations."
        )
        # Define allowed file extensions for security
        self.allowed_extensions = {'.txt', '.md', '.json', '.csv',
                                   '.py', '.js', '.html', '.css', '.xml', '.yaml', '.yml'}
        # Define maximum file size (1MB)
        self.max_file_size = 1024 * 1024

    def execute(self, operation: str, file_path: str, content: str = None) -> str:
        """Execute a file operation."""
        try:
            if operation == "read":
                return self._read_file(file_path)
            elif operation == "write":
                if content is None:
                    return "Error: Content is required for write operation"
                return self._write_file(file_path, content)
            elif operation == "append":
                if content is None:
                    return "Error: Content is required for append operation"
                return self._append_file(file_path, content)
            elif operation == "list":
                return self._list_directory(file_path)
            else:
                return f"Error: Unsupported operation '{operation}'. Supported operations: read, write, append, list"
        except Exception as e:
            logger.error(f"File operation error: {e}")
            return f"Error performing {operation} on '{file_path}': {str(e)}"

    def _read_file(self, file_path: str) -> str:
        """Read content from a file."""
        path = Path(file_path)

        # Security checks
        if not self._is_safe_path(path):
            return f"Error: Access denied to '{file_path}'"

        if not path.exists():
            return f"Error: File '{file_path}' does not exist"

        if not path.is_file():
            return f"Error: '{file_path}' is not a file"

        # Check file size
        if path.stat().st_size > self.max_file_size:
            return f"Error: File '{file_path}' is too large (max {self.max_file_size // 1024}KB)"

        try:
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()
            return f"Content of '{file_path}':\n\n{content}"
        except UnicodeDecodeError:
            return f"Error: '{file_path}' is not a text file or has encoding issues"

    def _write_file(self, file_path: str, content: str) -> str:
        """Write content to a file."""
        path = Path(file_path)

        # Security checks
        if not self._is_safe_path(path):
            return f"Error: Access denied to '{file_path}'"

        # Create directory if it doesn't exist
        path.parent.mkdir(parents=True, exist_ok=True)

        try:
            with open(path, 'w', encoding='utf-8') as f:
                f.write(content)
            return f"Successfully wrote {len(content)} characters to '{file_path}'"
        except Exception as e:
            return f"Error writing to '{file_path}': {str(e)}"

    def _append_file(self, file_path: str, content: str) -> str:
        """Append content to a file."""
        path = Path(file_path)

        # Security checks
        if not self._is_safe_path(path):
            return f"Error: Access denied to '{file_path}'"

        # Create directory if it doesn't exist
        path.parent.mkdir(parents=True, exist_ok=True)

        try:
            with open(path, 'a', encoding='utf-8') as f:
                f.write(content)
            return f"Successfully appended {len(content)} characters to '{file_path}'"
        except Exception as e:
            return f"Error appending to '{file_path}': {str(e)}"

    def _list_directory(self, dir_path: str) -> str:
        """List contents of a directory."""
        path = Path(dir_path)

        if not self._is_safe_path(path):
            return f"Error: Access denied to '{dir_path}'"

        if not path.exists():
            return f"Error: Directory '{dir_path}' does not exist"

        if not path.is_dir():
            return f"Error: '{dir_path}' is not a directory"

        try:
            items = []
            for item in sorted(path.iterdir()):
                if item.is_dir():
                    items.append(f"📁 {item.name}/")
                else:
                    size = item.stat().st_size
                    items.append(f"📄 {item.name} ({size} bytes)")

            if not items:
                return f"Directory '{dir_path}' is empty"

            return f"Contents of '{dir_path}':\n" + "\n".join(items)
        except Exception as e:
            return f"Error listing directory '{dir_path}': {str(e)}"

    def _is_safe_path(self, path: Path) -> bool:
        """Check if the path is safe to access."""
        try:
            # Resolve the path to handle symlinks and relative paths
            resolved_path = path.resolve()

            # Check if file extension is allowed
            if path.is_file() and path.suffix.lower() not in self.allowed_extensions:
                return False

            # Prevent access to system directories
            restricted_paths = [
                Path('/etc'),
                Path('/bin'),
                Path('/usr/bin'),
                Path('/sbin'),
                Path('/usr/sbin'),
                Path('/var'),
                Path('/sys'),
                Path('/proc'),
                Path.home() / '.ssh',
                Path.home() / '.aws',
            ]

            for restricted in restricted_paths:
                try:
                    if resolved_path.is_relative_to(restricted.resolve()):
                        return False
                except (OSError, ValueError):
                    continue

            return True
        except Exception:
            return False

    def get_schema(self) -> Dict[str, Any]:
        """Get the JSON schema for this tool's parameters."""
        return {
            "type": "object",
            "properties": {
                "operation": {
                    "type": "string",
                    "enum": ["read", "write", "append", "list"],
                    "description": "File operation to perform: 'read' (read file content), 'write' (write/overwrite file), 'append' (add to end of file), 'list' (list directory contents)"
                },
                "file_path": {
                    "type": "string",
                    "description": "Path to the file or directory"
                },
                "content": {
                    "type": "string",
                    "description": "Content to write or append (required for write/append operations)"
                }
            },
            "required": ["operation", "file_path"]
        }
