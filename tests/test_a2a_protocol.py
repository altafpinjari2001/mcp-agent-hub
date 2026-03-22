"""Tests for A2A protocol."""
import pytest
from src.a2a.types import AgentCard, Task, TaskState
from src.a2a.server import A2AServer

def test_agent_card_serialization():
    card = AgentCard(
        name="TestAgent",
        description="A test agent",
        url="http://test"
    )
    data = card.to_dict()
    assert data["name"] == "TestAgent"
    assert data["url"] == "http://test"

@pytest.mark.asyncio
async def test_a2a_server_handle_task():
    card = AgentCard(name="Test", description="test", url="test")
    server = A2AServer(card)
    
    async def mock_handler(msg):
        return f"echo: {msg}"
        
    server.set_handler(mock_handler)
    
    res = await server.handle_task(None, "hello")
    
    assert res["state"] == TaskState.COMPLETED.value
    assert res["result"] == "echo: hello"
