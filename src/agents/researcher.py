"""
MCP Agent Hub — Research Agent.

Web research agent using MCP web search tools.
"""

from __future__ import annotations

import json
import logging

from .base import BaseAgent
from ..a2a.types import AgentSkill

logger = logging.getLogger(__name__)


class ResearchAgent(BaseAgent):
    """
    Research Agent.

    Specializes in:
    - Web search for current information
    - Content extraction from URLs
    - Summarizing findings with citations
    """

    def __init__(self, port: int = 8002):
        super().__init__(
            name="ResearchAgent",
            description=(
                "Researches topics using web search, gathers "
                "information, and provides cited summaries."
            ),
            skills=[
                AgentSkill(
                    id="web-research",
                    name="Web Research",
                    description="Search the web and synthesize findings",
                    tags=["search", "research", "web"],
                    examples=[
                        "What are the latest developments in MCP?",
                        "Compare RAG vs fine-tuning approaches",
                    ],
                ),
                AgentSkill(
                    id="url-extraction",
                    name="URL Content Extraction",
                    description="Extract and summarize content from URLs",
                    tags=["scraping", "extraction"],
                ),
            ],
            port=port,
        )

    async def process(self, message: str) -> str:
        """
        Process a research request.

        Workflow:
        1. Search the web for the topic
        2. Extract key findings
        3. Compile a cited summary
        """
        logger.info(f"[{self.name}] Researching: {message[:100]}")

        # Step 1: Web search
        search_result = await self.use_tool(
            "search", {"query": message, "max_results": 5}
        )

        if search_result.is_error:
            return f"Search failed: {search_result.content}"

        data = json.loads(search_result.content)
        answer = data.get("answer", "")
        results = data.get("results", [])

        # Step 2: Compile findings
        sources = []
        for i, r in enumerate(results, 1):
            sources.append(
                f"{i}. [{r['title']}]({r['url']})\n"
                f"   {r['content'][:200]}..."
            )

        response = (
            f"## Research Report: {message}\n\n"
            f"### Summary\n{answer}\n\n"
            f"### Sources\n" + "\n\n".join(sources)
        )

        return response
