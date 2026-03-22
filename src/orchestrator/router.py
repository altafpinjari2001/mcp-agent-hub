"""
MCP Agent Hub — Agent Orchestrator.

Routes tasks to the most capable agent based on
intent classification and agent skill matching.
"""

from __future__ import annotations

import logging
from typing import Any

from ..agents.base import BaseAgent
from ..a2a.types import AgentCard

logger = logging.getLogger(__name__)


class AgentRegistry:
    """Manages agent registration and discovery."""

    def __init__(self):
        self._agents: dict[str, BaseAgent] = {}

    def register(self, agent: BaseAgent) -> None:
        self._agents[agent.name] = agent
        logger.info(f"Registered agent: {agent.name}")

    def get(self, name: str) -> BaseAgent | None:
        return self._agents.get(name)

    def list_agents(self) -> list[AgentCard]:
        return [a.agent_card for a in self._agents.values()]

    def list_all_skills(self) -> list[dict]:
        skills = []
        for agent in self._agents.values():
            for skill in agent.agent_card.skills:
                skills.append({
                    "agent": agent.name,
                    "skill_id": skill.id,
                    "skill_name": skill.name,
                    "description": skill.description,
                    "tags": skill.tags,
                })
        return skills


class AgentOrchestrator:
    """
    Routes tasks to the most capable agent.

    Uses keyword-based intent classification to match
    user queries with agent skills.
    """

    # Keyword → Agent mapping for intent classification
    INTENT_KEYWORDS: dict[str, list[str]] = {
        "DataAnalystAgent": [
            "data", "sql", "query", "database", "table",
            "analyze", "analytics", "chart", "visualization",
            "churn", "revenue", "metrics", "statistics",
        ],
        "ResearchAgent": [
            "search", "research", "find", "latest", "news",
            "compare", "what is", "explain", "trends",
            "article", "paper", "web",
        ],
        "CodeAssistantAgent": [
            "code", "python", "execute", "run", "function",
            "debug", "script", "programming", "implement",
            "calculate", "algorithm",
        ],
    }

    def __init__(self, registry: AgentRegistry):
        self.registry = registry

    async def route(self, message: str) -> dict[str, Any]:
        """
        Route a message to the best agent and get a response.

        Args:
            message: User query or task description

        Returns:
            Dict with agent name, response, and metadata
        """
        # Find best agent
        agent_name = self._classify_intent(message)
        agent = self.registry.get(agent_name)

        if not agent:
            return {
                "agent": None,
                "response": "No suitable agent found for this query.",
                "error": True,
            }

        logger.info(f"Routing to: {agent_name}")

        # Process the task
        try:
            response = await agent.process(message)
            return {
                "agent": agent_name,
                "response": response,
                "error": False,
            }
        except Exception as e:
            logger.error(f"Agent {agent_name} failed: {e}")
            return {
                "agent": agent_name,
                "response": f"Error: {str(e)}",
                "error": True,
            }

    def _classify_intent(self, message: str) -> str:
        """
        Classify user intent using keyword matching.

        Returns the name of the best-matching agent.
        """
        message_lower = message.lower()
        scores: dict[str, int] = {}

        for agent_name, keywords in self.INTENT_KEYWORDS.items():
            score = sum(
                1 for kw in keywords if kw in message_lower
            )
            scores[agent_name] = score

        # Return agent with highest score, default to Research
        best = max(scores, key=scores.get)  # type: ignore
        if scores[best] == 0:
            return "ResearchAgent"  # Default fallback

        return best
