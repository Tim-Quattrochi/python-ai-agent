"""GitHub integration tool for repository management and operations."""

import os
import requests
import json
from typing import Dict, Any, Optional
from .base import Tool


class GitHubTool(Tool):
    """Tool for GitHub repository operations."""

    def __init__(self):
        super().__init__(
            name="github",
            description="Interact with GitHub: create repos, manage issues, search code, get repo info"
        )
        self.token = os.getenv('GITHUB_TOKEN')
        self.base_url = "https://api.github.com"

        if not self.token:
            print("⚠️  Warning: GITHUB_TOKEN not set. GitHub operations will be limited.")

    def execute(self, operation: str, **kwargs) -> str:
        """Execute GitHub operations."""
        try:
            if operation == "create_repo":
                return self._create_repository(
                    kwargs.get('name'),
                    kwargs.get('description', ''),
                    kwargs.get('private', False)
                )
            elif operation == "search_repos":
                return self._search_repositories(kwargs.get('query'))
            elif operation == "get_repo_info":
                return self._get_repository_info(kwargs.get('owner'), kwargs.get('repo'))
            elif operation == "list_issues":
                return self._list_issues(kwargs.get('owner'), kwargs.get('repo'))
            elif operation == "create_issue":
                return self._create_issue(
                    kwargs.get('owner'),
                    kwargs.get('repo'),
                    kwargs.get('title'),
                    kwargs.get('body', '')
                )
            elif operation == "search_code":
                return self._search_code(kwargs.get('query'))
            elif operation == "get_user_info":
                return self._get_user_info(kwargs.get('username'))
            else:
                return f"Error: Unknown operation '{operation}'"
        except Exception as e:
            return f"GitHub API error: {str(e)}"

    def _make_request(self, method: str, endpoint: str, data: Optional[Dict] = None) -> Dict:
        """Make a request to the GitHub API."""
        headers = {
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "Python-AI-Agent"
        }

        if self.token:
            headers["Authorization"] = f"token {self.token}"

        url = f"{self.base_url}{endpoint}"

        if method == "GET":
            response = requests.get(url, headers=headers)
        elif method == "POST":
            response = requests.post(url, headers=headers, json=data)
        else:
            raise ValueError(f"Unsupported HTTP method: {method}")

        response.raise_for_status()
        return response.json()

    def _create_repository(self, name: str, description: str, private: bool) -> str:
        """Create a new GitHub repository."""
        if not self.token:
            return "❌ Error: GITHUB_TOKEN required for repository creation"

        if not name:
            return "❌ Error: Repository name is required"

        data = {
            "name": name,
            "description": description,
            "private": private
        }

        result = self._make_request("POST", "/user/repos", data)

        return f"✅ Repository created successfully!\n" \
            f"📁 Name: {result['name']}\n" \
            f"🔗 URL: {result['html_url']}\n" \
            f"🔒 Private: {result['private']}"

    def _search_repositories(self, query: str) -> str:
        """Search for repositories."""
        if not query:
            return "❌ Error: Search query is required"

        result = self._make_request(
            "GET", f"/search/repositories?q={query}&sort=stars&order=desc")

        if not result['items']:
            return f"🔍 No repositories found for query: {query}"

        output = f"🔍 Top repositories for '{query}':\n\n"
        for i, repo in enumerate(result['items'][:5], 1):
            output += f"{i}. **{repo['full_name']}**\n"
            output += f"   ⭐ {repo['stargazers_count']} stars\n"
            output += f"   📝 {repo['description'] or 'No description'}\n"
            output += f"   🔗 {repo['html_url']}\n\n"

        return output

    def _get_repository_info(self, owner: str, repo: str) -> str:
        """Get detailed information about a repository."""
        if not all([owner, repo]):
            return "❌ Error: Both owner and repo are required"

        result = self._make_request("GET", f"/repos/{owner}/{repo}")

        info = f"📁 **{result['full_name']}**\n\n"
        info += f"📝 Description: {result['description'] or 'No description'}\n"
        info += f"🏷️  Language: {result['language'] or 'Not specified'}\n"
        info += f"⭐ Stars: {result['stargazers_count']}\n"
        info += f"🍴 Forks: {result['forks_count']}\n"
        info += f"🐛 Open Issues: {result['open_issues_count']}\n"
        info += f"📅 Created: {result['created_at'][:10]}\n"
        info += f"📅 Updated: {result['updated_at'][:10]}\n"
        info += f"🔗 URL: {result['html_url']}\n"

        if result['license']:
            info += f"⚖️  License: {result['license']['name']}\n"

        return info

    def _list_issues(self, owner: str, repo: str) -> str:
        """List issues for a repository."""
        if not all([owner, repo]):
            return "❌ Error: Both owner and repo are required"

        result = self._make_request("GET", f"/repos/{owner}/{repo}/issues")

        if not result:
            return f"✅ No open issues found in {owner}/{repo}"

        output = f"🐛 Open issues in {owner}/{repo}:\n\n"
        for i, issue in enumerate(result[:10], 1):
            output += f"{i}. **#{issue['number']}** {issue['title']}\n"
            output += f"   👤 By: {issue['user']['login']}\n"
            output += f"   📅 Created: {issue['created_at'][:10]}\n"
            output += f"   🔗 {issue['html_url']}\n\n"

        if len(result) > 10:
            output += f"... and {len(result) - 10} more issues\n"

        return output

    def _create_issue(self, owner: str, repo: str, title: str, body: str) -> str:
        """Create a new issue in a repository."""
        if not self.token:
            return "❌ Error: GITHUB_TOKEN required for issue creation"

        if not all([owner, repo, title]):
            return "❌ Error: owner, repo, and title are required"

        data = {
            "title": title,
            "body": body
        }

        result = self._make_request(
            "POST", f"/repos/{owner}/{repo}/issues", data)

        return f"✅ Issue created successfully!\n" \
            f"🐛 #{result['number']}: {result['title']}\n" \
            f"🔗 {result['html_url']}"

    def _search_code(self, query: str) -> str:
        """Search for code across GitHub."""
        if not query:
            return "❌ Error: Search query is required"

        result = self._make_request("GET", f"/search/code?q={query}")

        if not result['items']:
            return f"🔍 No code found for query: {query}"

        output = f"🔍 Code search results for '{query}':\n\n"
        for i, item in enumerate(result['items'][:5], 1):
            output += f"{i}. **{item['name']}** in {item['repository']['full_name']}\n"
            output += f"   📁 Path: {item['path']}\n"
            output += f"   🔗 {item['html_url']}\n\n"

        return output

    def _get_user_info(self, username: str) -> str:
        """Get information about a GitHub user."""
        if not username:
            return "❌ Error: Username is required"

        result = self._make_request("GET", f"/users/{username}")

        info = f"👤 **{result['login']}**\n\n"
        if result.get('name'):
            info += f"📝 Name: {result['name']}\n"
        if result.get('bio'):
            info += f"📄 Bio: {result['bio']}\n"
        if result.get('company'):
            info += f"🏢 Company: {result['company']}\n"
        if result.get('location'):
            info += f"📍 Location: {result['location']}\n"

        info += f"📊 Public Repos: {result['public_repos']}\n"
        info += f"👥 Followers: {result['followers']}\n"
        info += f"👤 Following: {result['following']}\n"
        info += f"📅 Joined: {result['created_at'][:10]}\n"
        info += f"🔗 Profile: {result['html_url']}\n"

        return info

    def get_schema(self) -> Dict[str, Any]:
        """Get the JSON schema for this tool."""
        return {
            "type": "object",
            "properties": {
                "operation": {
                    "type": "string",
                    "enum": ["create_repo", "search_repos", "get_repo_info", "list_issues",
                             "create_issue", "search_code", "get_user_info"],
                    "description": "GitHub operation to perform"
                },
                "name": {
                    "type": "string",
                    "description": "Repository name for creation"
                },
                "description": {
                    "type": "string",
                    "description": "Repository description"
                },
                "private": {
                    "type": "boolean",
                    "description": "Whether repository should be private"
                },
                "query": {
                    "type": "string",
                    "description": "Search query for repos or code"
                },
                "owner": {
                    "type": "string",
                    "description": "Repository owner/username"
                },
                "repo": {
                    "type": "string",
                    "description": "Repository name"
                },
                "title": {
                    "type": "string",
                    "description": "Issue title"
                },
                "body": {
                    "type": "string",
                    "description": "Issue body/description"
                },
                "username": {
                    "type": "string",
                    "description": "GitHub username"
                }
            },
            "required": ["operation"]
        }
