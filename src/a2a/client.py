"""
MCP Agent Hub — A2A Client.

Client for agent-to-agent communication.
Discovers remote agents and sends tasks to them.
"""

from __future__ import annotations

import logging
import uuid

import httpx

from .types import AgentCard, AgentCapabilities, AgentSkill, Task, TaskMessage, TaskState

logger = logging.getLogger(__name__)


class A2AClient:
    """
    A2A Client for inter-agent communication.

    Enables an agent to:
    1. Discover remote agents via their Agent Card
    2. Send tasks to remote agents
    3. Poll for task results
    4. Handle streaming responses
    """

    def __init__(self, timeout: int = 60):
        self.timeout = timeout
        self._known_agents: dict[str, AgentCard] = {}

    async def discover(self, agent_url: str) -> AgentCard:
        """
        Discover a remote agent by fetching its Agent Card.

        GET {agent_url}/.well-known/agent.json
        """
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{agent_url}/.well-known/agent.json",
                timeout=self.timeout,
            )
            response.raise_for_status()
            data = response.json()

        card = AgentCard(
            name=data["name"],
            description=data["description"],
            url=data["url"],
            version=data.get("version", "1.0.0"),
            capabilities=AgentCapabilities(
                streaming=data.get("capabilities", {}).get(
                    "streaming", False
                ),
            ),
            skills=[
                AgentSkill(
                    id=s["id"],
                    name=s["name"],
                    description=s.get("description", ""),
                    tags=s.get("tags", []),
                )
                for s in data.get("skills", [])
            ],
        )

        self._known_agents[card.name] = card
        logger.info(f"Discovered agent: {card.name} at {card.url}")
        return card

    async def send_task(
        self,
        agent_url: str,
        message: str,
        task_id: str | None = None,
    ) -> Task:
        """
        Send a task to a remote agent.

        POST {agent_url}/tasks/send
        """
        task_id = task_id or str(uuid.uuid4())

        payload = {
            "id": task_id,
            "message": {
                "role": "user",
                "parts": [{"type": "text", "text": message}],
            },
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{agent_url}/tasks/send",
                json=payload,
                timeout=self.timeout,
            )
            response.raise_for_status()
            data = response.json()

        task = Task(
            id=data.get("id", task_id),
            state=TaskState(data.get("state", "submitted")),
        )

        if "result" in data:
            task.result = data["result"]

        logger.info(
            f"Task {task.id} sent → state: {task.state.value}"
        )
        return task

    async def get_task(
        self, agent_url: str, task_id: str
    ) -> Task:
        """
        Get the current state of a task.

        GET {agent_url}/tasks/{task_id}
        """
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{agent_url}/tasks/{task_id}",
                timeout=self.timeout,
            )
            response.raise_for_status()
            data = response.json()

        return Task(
            id=data["id"],
            state=TaskState(data["state"]),
            result=data.get("result"),
        )

    @property
    def known_agents(self) -> list[AgentCard]:
        """List all discovered agents."""
        return list(self._known_agents.values())
