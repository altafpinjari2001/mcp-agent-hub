"""
MCP Agent Hub — A2A Server.

Server-side A2A protocol implementation.
Receives tasks from other agents and processes them.
"""

from __future__ import annotations

import logging
import uuid
from typing import Callable, Awaitable

from .types import AgentCard, Task, TaskMessage, TaskState

logger = logging.getLogger(__name__)


class A2AServer:
    """
    A2A Server for receiving and processing inter-agent tasks.

    Each agent runs an A2A server that:
    1. Serves its Agent Card at /.well-known/agent.json
    2. Receives tasks at /tasks/send
    3. Returns task status at /tasks/{id}
    """

    def __init__(self, agent_card: AgentCard):
        self.agent_card = agent_card
        self._tasks: dict[str, Task] = {}
        self._handler: Callable[
            [str], Awaitable[str]
        ] | None = None

    def set_handler(
        self, handler: Callable[[str], Awaitable[str]]
    ) -> None:
        """Set the function that processes incoming tasks."""
        self._handler = handler

    def get_agent_card(self) -> dict:
        """Return the agent card as JSON."""
        return self.agent_card.to_dict()

    async def handle_task(
        self, task_id: str | None, message: str
    ) -> dict:
        """
        Handle an incoming task from another agent.

        Args:
            task_id: Optional task ID (generated if not provided)
            message: The task description/query

        Returns:
            Task state response
        """
        task_id = task_id or str(uuid.uuid4())

        # Create task
        task = Task(id=task_id)
        task.messages.append(
            TaskMessage(role="user", content=message)
        )
        task.transition(TaskState.WORKING)
        self._tasks[task_id] = task

        logger.info(f"Processing task {task_id}: {message[:100]}")

        # Execute handler
        if self._handler:
            try:
                result = await self._handler(message)
                task.result = result
                task.messages.append(
                    TaskMessage(role="agent", content=result)
                )
                task.transition(TaskState.COMPLETED)
            except Exception as e:
                task.result = f"Error: {str(e)}"
                task.transition(TaskState.FAILED)
                logger.error(f"Task {task_id} failed: {e}")
        else:
            task.result = "No handler configured"
            task.transition(TaskState.FAILED)

        return {
            "id": task.id,
            "state": task.state.value,
            "result": task.result,
        }

    def get_task_status(self, task_id: str) -> dict | None:
        """Get the status of a task."""
        task = self._tasks.get(task_id)
        if not task:
            return None

        return {
            "id": task.id,
            "state": task.state.value,
            "result": task.result,
            "history": task.history,
        }
