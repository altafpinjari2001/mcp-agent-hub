"""
MCP Agent Hub — Base Agent.

Abstract base for all AI agents that combines
MCP (tool access) with A2A (agent communication).
"""

from __future__ import annotations

import logging
from abc import ABC, abstractmethod

from ..mcp.client import MCPClient
from ..mcp.types import ToolResult
from ..a2a.types import AgentCard, AgentSkill, AgentCapabilities

logger = logging.getLogger(__name__)


class BaseAgent(ABC):
    """
    Base AI Agent.

    Every agent has:
    - An AgentCard (identity + capabilities)
    - An MCPClient (access to tools)
    - A process() method (core logic)

    Agents can:
    - Use MCP tools to interact with external resources
    - Receive tasks from other agents via A2A
    - Delegate sub-tasks to other agents via A2A
    """

    def __init__(
        self,
        name: str,
        description: str,
        skills: list[AgentSkill] | None = None,
        port: int = 8001,
    ):
        self.agent_card = AgentCard(
            name=name,
            description=description,
            url=f"http://localhost:{port}",
            skills=skills or [],
            capabilities=AgentCapabilities(streaming=True),
        )
        self.mcp_client = MCPClient()
        self._port = port

    @property
    def name(self) -> str:
        return self.agent_card.name

    async def use_tool(
        self, tool_name: str, arguments: dict
    ) -> ToolResult:
        """
        Use an MCP tool.

        The agent calls this to interact with databases,
        files, web search, code execution, etc.
        """
        logger.info(f"[{self.name}] Using tool: {tool_name}")
        return await self.mcp_client.call_tool(tool_name, arguments)

    @abstractmethod
    async def process(self, message: str) -> str:
        """
        Process a task/message.

        This is the core agent logic. Subclasses implement
        their specific behavior here.

        Args:
            message: The task description or user query

        Returns:
            The agent's response/result
        """
        ...
