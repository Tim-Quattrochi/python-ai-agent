"""Web search tool for finding information online."""

import requests
from typing import Dict, Any
import logging
from .base import Tool

logger = logging.getLogger(__name__)


class WebSearchTool(Tool):
    """A tool for searching the web and retrieving information."""

    def __init__(self):
        super().__init__(
            name="web_search",
            description="Search the web for information on any topic. Returns relevant search results with titles, URLs, and snippets."
        )

    def execute(self, query: str, num_results: int = 5) -> str:
        """Execute a web search."""
        try:
            # For now, we'll use a simple approach with DuckDuckGo's instant answer API
            # In a production environment, you might want to use Google Custom Search API,
            # Bing Search API, or other commercial search APIs
            
            results = self._search_duckduckgo(query, num_results)
            
            if not results:
                return f"No search results found for: {query}"
            
            formatted_results = self._format_results(results, query)
            return formatted_results
            
        except Exception as e:
            logger.error(f"Web search error: {e}")
            return f"Error performing web search for '{query}': {str(e)}"

    def _search_duckduckgo(self, query: str, num_results: int) -> list:
        """Search using DuckDuckGo's API."""
        try:
            # DuckDuckGo Instant Answer API
            url = "https://api.duckduckgo.com/"
            params = {
                "q": query,
                "format": "json",
                "no_html": "1",
                "skip_disambig": "1"
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            results = []
            
            # Add abstract if available
            if data.get("Abstract"):
                results.append({
                    "title": data.get("AbstractSource", "DuckDuckGo"),
                    "url": data.get("AbstractURL", ""),
                    "snippet": data.get("Abstract", "")
                })
            
            # Add related topics
            for topic in data.get("RelatedTopics", [])[:num_results-1]:
                if isinstance(topic, dict) and topic.get("Text"):
                    results.append({
                        "title": topic.get("FirstURL", "").split("/")[-1].replace("_", " ") if topic.get("FirstURL") else "Related Topic",
                        "url": topic.get("FirstURL", ""),
                        "snippet": topic.get("Text", "")
                    })
            
            return results[:num_results]
            
        except Exception as e:
            logger.error(f"DuckDuckGo search error: {e}")
            # Fallback: return a simple message
            return [{
                "title": "Search Information",
                "url": f"https://duckduckgo.com/?q={query.replace(' ', '+')}",
                "snippet": f"Search for '{query}' on DuckDuckGo to find relevant information."
            }]

    def _format_results(self, results: list, query: str) -> str:
        """Format search results for display."""
        if not results:
            return f"No results found for: {query}"
        
        formatted = f"Web search results for '{query}':\n\n"
        
        for i, result in enumerate(results, 1):
            title = result.get("title", "No title")
            url = result.get("url", "")
            snippet = result.get("snippet", "No description available")
            
            formatted += f"{i}. **{title}**\n"
            if url:
                formatted += f"   URL: {url}\n"
            formatted += f"   {snippet}\n\n"
        
        return formatted.strip()

    def get_schema(self) -> Dict[str, Any]:
        """Get the JSON schema for this tool's parameters."""
        return {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Search query to find information about"
                },
                "num_results": {
                    "type": "integer",
                    "description": "Number of search results to return (default: 5, max: 10)",
                    "minimum": 1,
                    "maximum": 10,
                    "default": 5
                }
            },
            "required": ["query"]
        }
