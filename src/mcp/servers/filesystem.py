"""
MCP Agent Hub — Filesystem MCP Server.

Exposes filesystem operations as MCP tools.
Tools: read_file, write_file, list_directory, search_files.
"""

from __future__ import annotations

import json
import logging
from pathlib import Path

from ..server import BaseMCPServer
from ..types import ToolDefinition, ToolParameter, ToolInputType, ToolResult

logger = logging.getLogger(__name__)

# Safety: restrict to this base directory
ALLOWED_BASE = Path("workspace").resolve()


class FilesystemMCPServer(BaseMCPServer):
    """
    MCP Server for filesystem operations.

    All operations are sandboxed to a workspace directory.
    """

    def __init__(self, workspace: str = "workspace"):
        self.workspace = Path(workspace).resolve()
        self.workspace.mkdir(parents=True, exist_ok=True)
        super().__init__(
            name="filesystem-server",
            version="1.0.0",
            description="File system tools for reading, writing, and listing files",
        )

    def _register_tools(self) -> None:
        self.register_tool(ToolDefinition(
            name="read_file",
            description="Read the contents of a file",
            parameters=[
                ToolParameter(
                    name="path",
                    type=ToolInputType.STRING,
                    description="Relative path to the file within workspace",
                ),
            ],
        ))

        self.register_tool(ToolDefinition(
            name="write_file",
            description="Write content to a file (creates if not exists)",
            parameters=[
                ToolParameter(
                    name="path",
                    type=ToolInputType.STRING,
                    description="Relative path for the file",
                ),
                ToolParameter(
                    name="content",
                    type=ToolInputType.STRING,
                    description="Content to write",
                ),
            ],
        ))

        self.register_tool(ToolDefinition(
            name="list_directory",
            description="List files and directories in a path",
            parameters=[
                ToolParameter(
                    name="path",
                    type=ToolInputType.STRING,
                    description="Relative directory path",
                    required=False,
                    default=".",
                ),
            ],
        ))

        self.register_tool(ToolDefinition(
            name="search_files",
            description="Search for files matching a glob pattern",
            parameters=[
                ToolParameter(
                    name="pattern",
                    type=ToolInputType.STRING,
                    description="Glob pattern (e.g., '**/*.py')",
                ),
            ],
        ))

    def _resolve_safe_path(self, path: str) -> Path | None:
        """Resolve path and ensure it's within workspace."""
        resolved = (self.workspace / path).resolve()
        if not str(resolved).startswith(str(self.workspace)):
            return None  # Path traversal attempt
        return resolved

    async def _execute_tool(
        self, tool_name: str, arguments: dict
    ) -> ToolResult:
        match tool_name:
            case "read_file":
                return await self._read_file(arguments["path"])
            case "write_file":
                return await self._write_file(
                    arguments["path"], arguments["content"]
                )
            case "list_directory":
                return await self._list_directory(
                    arguments.get("path", ".")
                )
            case "search_files":
                return await self._search_files(arguments["pattern"])
            case _:
                return ToolResult(content="Unknown tool", is_error=True)

    async def _read_file(self, path: str) -> ToolResult:
        safe_path = self._resolve_safe_path(path)
        if not safe_path:
            return ToolResult(
                content="Path traversal not allowed", is_error=True
            )

        if not safe_path.exists():
            return ToolResult(
                content=f"File not found: {path}", is_error=True
            )

        try:
            content = safe_path.read_text(encoding="utf-8")
            return ToolResult(
                content=content,
                metadata={"path": path, "size": len(content)},
            )
        except Exception as e:
            return ToolResult(content=str(e), is_error=True)

    async def _write_file(self, path: str, content: str) -> ToolResult:
        safe_path = self._resolve_safe_path(path)
        if not safe_path:
            return ToolResult(
                content="Path traversal not allowed", is_error=True
            )

        safe_path.parent.mkdir(parents=True, exist_ok=True)
        safe_path.write_text(content, encoding="utf-8")

        return ToolResult(
            content=f"Written {len(content)} chars to {path}",
            metadata={"path": path},
        )

    async def _list_directory(self, path: str) -> ToolResult:
        safe_path = self._resolve_safe_path(path)
        if not safe_path or not safe_path.is_dir():
            return ToolResult(
                content="Invalid directory", is_error=True
            )

        entries = []
        for item in sorted(safe_path.iterdir()):
            entries.append({
                "name": item.name,
                "type": "directory" if item.is_dir() else "file",
                "size": item.stat().st_size if item.is_file() else None,
            })

        return ToolResult(content=json.dumps(entries, indent=2))

    async def _search_files(self, pattern: str) -> ToolResult:
        matches = [
            str(p.relative_to(self.workspace))
            for p in self.workspace.glob(pattern)
            if p.is_file()
        ]
        return ToolResult(
            content=json.dumps(matches[:50], indent=2),
            metadata={"total_matches": len(matches)},
        )
