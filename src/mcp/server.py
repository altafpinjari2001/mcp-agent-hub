"""
MCP Agent Hub — Base MCP Server.

Abstract base class for all MCP tool servers.
Each server exposes a set of tools that AI agents can invoke.
"""

from __future__ import annotations

import logging
from abc import ABC, abstractmethod

from .types import ToolDefinition, ToolCall, ToolResult, MCPServerInfo

logger = logging.getLogger(__name__)


class BaseMCPServer(ABC):
    """
    Base MCP Server.

    An MCP server exposes tools through a standardized interface.
    AI agents connect to servers via the MCP protocol and invoke
    tools to perform actions (query databases, read files, etc.).

    Lifecycle:
        1. Server initializes and registers tools
        2. Client connects and discovers available tools
        3. Client sends ToolCall, server executes and returns ToolResult
    """

    def __init__(self, name: str, version: str, description: str):
        self.info = MCPServerInfo(
            name=name,
            version=version,
            description=description,
        )
        self._tools: dict[str, ToolDefinition] = {}
        self._register_tools()

    @abstractmethod
    def _register_tools(self) -> None:
        """Register all tools this server exposes."""
        ...

    def register_tool(self, tool: ToolDefinition) -> None:
        """Register a tool with this server."""
        self._tools[tool.name] = tool
        self.info.tools.append(tool)
        logger.info(f"[{self.info.name}] Registered tool: {tool.name}")

    def list_tools(self) -> list[ToolDefinition]:
        """List all available tools."""
        return list(self._tools.values())

    async def call_tool(
        self, tool_name: str, arguments: dict
    ) -> ToolResult:
        """
        Execute a tool by name.

        Args:
            tool_name: Name of the tool to invoke
            arguments: Tool arguments

        Returns:
            ToolResult with the execution output
        """
        if tool_name not in self._tools:
            return ToolResult(
                content=f"Unknown tool: {tool_name}",
                is_error=True,
            )

        try:
            logger.info(
                f"[{self.info.name}] Calling tool: {tool_name}"
            )
            result = await self._execute_tool(tool_name, arguments)
            return result
        except Exception as e:
            logger.error(f"Tool execution failed: {e}")
            return ToolResult(
                content=f"Error executing {tool_name}: {str(e)}",
                is_error=True,
            )

    @abstractmethod
    async def _execute_tool(
        self, tool_name: str, arguments: dict
    ) -> ToolResult:
        """Execute a specific tool. Subclasses implement this."""
        ...
