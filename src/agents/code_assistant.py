"""
MCP Agent Hub — Code Assistant Agent.

Code generation, debugging, and execution agent
using MCP code execution tools.
"""

from __future__ import annotations

import json
import logging

from .base import BaseAgent
from ..a2a.types import AgentSkill

logger = logging.getLogger(__name__)


class CodeAssistantAgent(BaseAgent):
    """
    Code Assistant Agent.

    Specializes in:
    - Executing Python code
    - Analyzing code for issues
    - Reading/writing code files
    """

    def __init__(self, port: int = 8003):
        super().__init__(
            name="CodeAssistantAgent",
            description=(
                "Executes Python code, performs code analysis, "
                "and assists with programming tasks."
            ),
            skills=[
                AgentSkill(
                    id="code-execution",
                    name="Python Code Execution",
                    description="Execute Python code in a sandbox",
                    tags=["python", "execution", "code"],
                    examples=[
                        "Calculate the fibonacci sequence up to 100",
                        "Parse this JSON and extract key fields",
                    ],
                ),
                AgentSkill(
                    id="code-analysis",
                    name="Code Analysis",
                    description="Analyze code for bugs and improvements",
                    tags=["analysis", "debugging", "review"],
                ),
            ],
            port=port,
        )

    async def process(self, message: str) -> str:
        """
        Process a code-related request.

        Workflow:
        1. If code is provided, analyze it first
        2. Execute the code
        3. Return results with analysis
        """
        logger.info(f"[{self.name}] Processing: {message[:100]}")

        # Extract code block if present
        code = self._extract_code(message)

        if code:
            # Analyze the code first
            analysis = await self.use_tool(
                "analyze_code", {"code": code}
            )

            analysis_data = json.loads(analysis.content)

            # Execute if valid
            if analysis_data.get("is_valid", False):
                exec_result = await self.use_tool(
                    "execute_python", {"code": code}
                )

                response = (
                    f"## Code Execution Result\n\n"
                    f"### Analysis\n"
                    f"- Lines: {analysis_data['lines_of_code']}\n"
                    f"- Functions: {analysis_data['has_functions']}\n"
                    f"- Classes: {analysis_data['has_classes']}\n\n"
                    f"### Output\n"
                    f"```\n{exec_result.content}\n```"
                )
            else:
                issues = "\n".join(
                    f"- {i}" for i in analysis_data.get("issues", [])
                )
                response = (
                    f"## Code Analysis\n\n"
                    f"### Issues Found\n{issues}\n\n"
                    f"Please fix the issues before execution."
                )
        else:
            response = (
                f"## Code Assistant\n\n"
                f"I received your request: *{message}*\n\n"
                f"Please provide Python code to execute or analyze. "
                f"Include the code in a code block."
            )

        return response

    @staticmethod
    def _extract_code(message: str) -> str | None:
        """Extract code from markdown code blocks."""
        if "```python" in message:
            start = message.index("```python") + 9
            end = message.index("```", start)
            return message[start:end].strip()
        elif "```" in message:
            start = message.index("```") + 3
            end = message.index("```", start)
            return message[start:end].strip()
        return None
