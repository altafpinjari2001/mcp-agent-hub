"""
MCP Agent Hub — Web Search MCP Server.

Web search and scraping tools using Tavily API.
Tools: search, scrape_url, get_news.
"""

from __future__ import annotations

import json
import logging
from typing import Any

import httpx

from ..server import BaseMCPServer
from ..types import ToolDefinition, ToolParameter, ToolInputType, ToolResult

logger = logging.getLogger(__name__)


class WebSearchMCPServer(BaseMCPServer):
    """
    MCP Server for web search operations.

    Uses Tavily API for high-quality search results
    optimized for AI agent consumption.
    """

    def __init__(self, api_key: str = ""):
        self.api_key = api_key
        self.base_url = "https://api.tavily.com"
        super().__init__(
            name="web-search-server",
            version="1.0.0",
            description="Web search and content extraction tools",
        )

    def _register_tools(self) -> None:
        self.register_tool(ToolDefinition(
            name="search",
            description=(
                "Search the web for information. Returns relevant "
                "results with titles, URLs, and content snippets."
            ),
            parameters=[
                ToolParameter(
                    name="query",
                    type=ToolInputType.STRING,
                    description="Search query",
                ),
                ToolParameter(
                    name="max_results",
                    type=ToolInputType.INTEGER,
                    description="Maximum results to return (1-10)",
                    required=False,
                    default=5,
                ),
            ],
        ))

        self.register_tool(ToolDefinition(
            name="scrape_url",
            description="Extract clean text content from a URL",
            parameters=[
                ToolParameter(
                    name="url",
                    type=ToolInputType.STRING,
                    description="URL to scrape",
                ),
            ],
        ))

    async def _execute_tool(
        self, tool_name: str, arguments: dict
    ) -> ToolResult:
        match tool_name:
            case "search":
                return await self._search(
                    arguments["query"],
                    arguments.get("max_results", 5),
                )
            case "scrape_url":
                return await self._scrape_url(arguments["url"])
            case _:
                return ToolResult(content="Unknown tool", is_error=True)

    async def _search(
        self, query: str, max_results: int = 5
    ) -> ToolResult:
        """Search the web using Tavily API."""
        if not self.api_key:
            return ToolResult(
                content="Tavily API key not configured",
                is_error=True,
            )

        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/search",
                json={
                    "api_key": self.api_key,
                    "query": query,
                    "max_results": min(max_results, 10),
                    "include_answer": True,
                },
                timeout=30,
            )
            response.raise_for_status()
            data = response.json()

        results = []
        for r in data.get("results", []):
            results.append({
                "title": r.get("title", ""),
                "url": r.get("url", ""),
                "content": r.get("content", "")[:500],
                "score": r.get("score", 0),
            })

        output = {
            "answer": data.get("answer", ""),
            "results": results,
        }

        return ToolResult(
            content=json.dumps(output, indent=2),
            metadata={"result_count": len(results)},
        )

    async def _scrape_url(self, url: str) -> ToolResult:
        """Extract content from a URL."""
        if not self.api_key:
            return ToolResult(
                content="Tavily API key not configured",
                is_error=True,
            )

        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/extract",
                json={
                    "api_key": self.api_key,
                    "urls": [url],
                },
                timeout=30,
            )
            response.raise_for_status()
            data = response.json()

        results = data.get("results", [])
        if results:
            content = results[0].get("raw_content", "")[:5000]
        else:
            content = "Could not extract content from URL"

        return ToolResult(
            content=content,
            metadata={"url": url},
        )
