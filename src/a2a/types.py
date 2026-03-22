"""
MCP Agent Hub — A2A Protocol Types.

Type definitions for Google's Agent-to-Agent (A2A) protocol.
Enables agents to discover each other's capabilities and
delegate tasks between themselves.

Reference: https://google.github.io/A2A
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
from typing import Any


class TaskState(str, Enum):
    """A2A Task states."""
    SUBMITTED = "submitted"
    WORKING = "working"
    INPUT_REQUIRED = "input-required"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELED = "canceled"


@dataclass
class AgentSkill:
    """A specific capability of an agent."""
    id: str
    name: str
    description: str
    tags: list[str] = field(default_factory=list)
    examples: list[str] = field(default_factory=list)


@dataclass
class AgentCapabilities:
    """What an agent can do."""
    streaming: bool = True
    push_notifications: bool = False
    state_transition_history: bool = True


@dataclass
class AgentCard:
    """
    A2A Agent Card.

    This is the agent's "business card" — it advertises the
    agent's identity, capabilities, and skills so other agents
    can discover what it can do.

    Other agents fetch this card from:
    GET /.well-known/agent.json
    """
    name: str
    description: str
    url: str
    version: str = "1.0.0"
    capabilities: AgentCapabilities = field(
        default_factory=AgentCapabilities
    )
    skills: list[AgentSkill] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "description": self.description,
            "url": self.url,
            "version": self.version,
            "capabilities": {
                "streaming": self.capabilities.streaming,
                "pushNotifications": self.capabilities.push_notifications,
                "stateTransitionHistory": (
                    self.capabilities.state_transition_history
                ),
            },
            "skills": [
                {
                    "id": s.id,
                    "name": s.name,
                    "description": s.description,
                    "tags": s.tags,
                    "examples": s.examples,
                }
                for s in self.skills
            ],
        }


@dataclass
class TaskMessage:
    """A message within an A2A task."""
    role: str  # "user" or "agent"
    content: str
    timestamp: str = field(
        default_factory=lambda: datetime.utcnow().isoformat()
    )


@dataclass
class Task:
    """
    A2A Task.

    Represents a unit of work sent between agents.
    Tasks go through state transitions as work progresses.
    """
    id: str
    state: TaskState = TaskState.SUBMITTED
    messages: list[TaskMessage] = field(default_factory=list)
    result: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)
    history: list[dict] = field(default_factory=list)

    def transition(self, new_state: TaskState) -> None:
        """Transition task to a new state."""
        self.history.append({
            "from": self.state.value,
            "to": new_state.value,
            "timestamp": datetime.utcnow().isoformat(),
        })
        self.state = new_state
