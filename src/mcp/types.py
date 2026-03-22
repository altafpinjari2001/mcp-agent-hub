"""
MCP Agent Hub — MCP Protocol Types.

Type definitions for the Model Context Protocol (MCP).
Follows the MCP specification for tool definitions,
tool calls, and responses.

Reference: https://spec.modelcontextprotocol.io
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class ToolInputType(str, Enum):
    """Supported MCP tool input types."""
    STRING = "string"
    NUMBER = "number"
    INTEGER = "integer"
    BOOLEAN = "boolean"
    OBJECT = "object"
    ARRAY = "array"


@dataclass
class ToolParameter:
    """A single parameter for an MCP tool."""
    name: str
    type: ToolInputType
    description: str
    required: bool = True
    default: Any = None


@dataclass
class ToolDefinition:
    """
    MCP Tool Definition.

    Describes a tool that an MCP server exposes.
    The LLM uses this to decide which tool to call.
    """
    name: str
    description: str
    parameters: list[ToolParameter] = field(default_factory=list)

    def to_schema(self) -> dict:
        """Convert to JSON Schema format for LLM function calling."""
        properties = {}
        required = []

        for param in self.parameters:
            properties[param.name] = {
                "type": param.type.value,
                "description": param.description,
            }
            if param.required:
                required.append(param.name)

        return {
            "type": "object",
            "properties": properties,
            "required": required,
        }


@dataclass
class ToolCall:
    """An invocation of an MCP tool."""
    tool_name: str
    arguments: dict[str, Any]
    call_id: str | None = None


@dataclass
class ToolResult:
    """Result from an MCP tool execution."""
    content: str
    is_error: bool = False
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class MCPServerInfo:
    """Information about an MCP server."""
    name: str
    version: str
    description: str
    tools: list[ToolDefinition] = field(default_factory=list)
