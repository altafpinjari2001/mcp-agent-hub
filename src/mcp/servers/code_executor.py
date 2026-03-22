"""
MCP Agent Hub — Code Execution MCP Server.

Sandboxed Python code execution as an MCP tool.
Tools: execute_python, analyze_code.
"""

from __future__ import annotations

import io
import sys
import json
import logging
import traceback
from contextlib import redirect_stdout, redirect_stderr

from ..server import BaseMCPServer
from ..types import ToolDefinition, ToolParameter, ToolInputType, ToolResult

logger = logging.getLogger(__name__)

# Safety: blocked modules and builtins
BLOCKED_MODULES = {"os", "subprocess", "shutil", "pathlib", "socket"}
BLOCKED_BUILTINS = {"exec", "eval", "compile", "__import__"}


class CodeExecutionMCPServer(BaseMCPServer):
    """
    MCP Server for sandboxed Python code execution.

    Provides a safe environment for running Python code
    with restricted access to system resources.
    """

    def __init__(self, timeout: int = 10):
        self.timeout = timeout
        super().__init__(
            name="code-execution-server",
            version="1.0.0",
            description="Sandboxed Python code execution",
        )

    def _register_tools(self) -> None:
        self.register_tool(ToolDefinition(
            name="execute_python",
            description=(
                "Execute Python code in a sandboxed environment. "
                "Returns stdout output. Has access to standard "
                "libraries like math, json, datetime, collections, "
                "itertools, and data science libs if installed."
            ),
            parameters=[
                ToolParameter(
                    name="code",
                    type=ToolInputType.STRING,
                    description="Python code to execute",
                ),
            ],
        ))

        self.register_tool(ToolDefinition(
            name="analyze_code",
            description=(
                "Analyze Python code for potential issues "
                "without executing it."
            ),
            parameters=[
                ToolParameter(
                    name="code",
                    type=ToolInputType.STRING,
                    description="Python code to analyze",
                ),
            ],
        ))

    async def _execute_tool(
        self, tool_name: str, arguments: dict
    ) -> ToolResult:
        match tool_name:
            case "execute_python":
                return await self._execute_python(arguments["code"])
            case "analyze_code":
                return await self._analyze_code(arguments["code"])
            case _:
                return ToolResult(content="Unknown tool", is_error=True)

    async def _execute_python(self, code: str) -> ToolResult:
        """Execute Python code in a restricted environment."""

        # Safety check: block dangerous imports
        for module in BLOCKED_MODULES:
            if f"import {module}" in code or f"from {module}" in code:
                return ToolResult(
                    content=f"Blocked: cannot import '{module}'",
                    is_error=True,
                )

        # Capture stdout and stderr
        stdout_capture = io.StringIO()
        stderr_capture = io.StringIO()

        # Create restricted globals
        safe_globals = {
            "__builtins__": {
                k: v for k, v in __builtins__.items()
                if k not in BLOCKED_BUILTINS
            } if isinstance(__builtins__, dict) else {
                k: getattr(__builtins__, k)
                for k in dir(__builtins__)
                if k not in BLOCKED_BUILTINS
            },
        }

        try:
            with redirect_stdout(stdout_capture), redirect_stderr(stderr_capture):
                compiled = compile(code, "<mcp-sandbox>", "exec")
                exec(compiled, safe_globals)  # noqa: S102

            stdout = stdout_capture.getvalue()
            stderr = stderr_capture.getvalue()

            output = stdout
            if stderr:
                output += f"\n[stderr]: {stderr}"

            return ToolResult(
                content=output or "(no output)",
                metadata={"executed": True},
            )

        except Exception as e:
            return ToolResult(
                content=f"Execution error: {traceback.format_exc()}",
                is_error=True,
            )

    async def _analyze_code(self, code: str) -> ToolResult:
        """Analyze Python code without executing it."""
        issues = []

        # Check syntax
        try:
            compile(code, "<analysis>", "exec")
        except SyntaxError as e:
            issues.append(f"Syntax error at line {e.lineno}: {e.msg}")

        # Check for dangerous patterns
        for module in BLOCKED_MODULES:
            if f"import {module}" in code:
                issues.append(f"Uses blocked module: {module}")

        # Basic metrics
        lines = code.strip().split("\n")
        metrics = {
            "lines_of_code": len(lines),
            "has_functions": "def " in code,
            "has_classes": "class " in code,
            "has_imports": "import " in code,
            "issues": issues,
            "is_valid": len(issues) == 0,
        }

        return ToolResult(
            content=json.dumps(metrics, indent=2),
            metadata={"analyzed": True},
        )
