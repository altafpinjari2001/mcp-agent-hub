"""
MCP Agent Hub — MCP Client.

Client for connecting to MCP servers and invoking tools.
Handles server discovery, tool listing, and remote invocation.
"""

from __future__ import annotations

import logging
from typing import Any

from .server import BaseMCPServer
from .types import ToolCall, ToolResult, ToolDefinition

logger = logging.getLogger(__name__)


class MCPClient:
    """
    MCP Client.

    Connects to one or more MCP servers and provides a unified
    interface for discovering and invoking tools.

    Usage:
        client = MCPClient()
        client.connect(database_server)
        client.connect(filesystem_server)

        # List all available tools
        tools = client.list_all_tools()

        # Call a specific tool
        result = await client.call_tool("query", {"sql": "SELECT ..."})
    """

    def __init__(self):
        self._servers: dict[str, BaseMCPServer] = {}
        self._tool_to_server: dict[str, str] = {}

    def connect(self, server: BaseMCPServer) -> None:
        """Connect to an MCP server."""
        self._servers[server.info.name] = server

        # Index tools for fast lookup
        for tool in server.list_tools():
            self._tool_to_server[tool.name] = server.info.name

        logger.info(
            f"Connected to MCP server: {server.info.name} "
            f"({len(server.list_tools())} tools)"
        )

    def disconnect(self, server_name: str) -> None:
        """Disconnect from an MCP server."""
        if server_name in self._servers:
            server = self._servers.pop(server_name)
            for tool in server.list_tools():
                self._tool_to_server.pop(tool.name, None)

    def list_all_tools(self) -> list[ToolDefinition]:
        """List all tools across all connected servers."""
        tools = []
        for server in self._servers.values():
            tools.extend(server.list_tools())
        return tools

    def list_tools_for_llm(self) -> list[dict]:
        """
        Get tool definitions formatted for LLM function calling.

        Returns a list compatible with OpenAI's function calling format.
        """
        return [
            {
                "type": "function",
                "function": {
                    "name": tool.name,
                    "description": tool.description,
                    "parameters": tool.to_schema(),
                },
            }
            for tool in self.list_all_tools()
        ]

    async def call_tool(
        self, tool_name: str, arguments: dict[str, Any]
    ) -> ToolResult:
        """
        Route a tool call to the correct MCP server.

        Args:
            tool_name: Name of the tool
            arguments: Tool arguments

        Returns:
            ToolResult from the server
        """
        server_name = self._tool_to_server.get(tool_name)
        if not server_name:
            return ToolResult(
                content=f"No server found for tool: {tool_name}",
                is_error=True,
            )

        server = self._servers[server_name]
        return await server.call_tool(tool_name, arguments)

    @property
    def connected_servers(self) -> list[str]:
        """Names of all connected servers."""
        return list(self._servers.keys())
