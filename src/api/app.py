"""
MCP Agent Hub — FastAPI Application.

REST API for the MCP Agent Hub platform.
"""

from __future__ import annotations

import logging

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from ..orchestrator.router import AgentRegistry, AgentOrchestrator
from ..agents.data_analyst import DataAnalystAgent
from ..agents.researcher import ResearchAgent
from ..agents.code_assistant import CodeAssistantAgent
from ..mcp.servers.database import DatabaseMCPServer
from ..mcp.servers.filesystem import FilesystemMCPServer
from ..mcp.servers.code_executor import CodeExecutionMCPServer

logger = logging.getLogger(__name__)

app = FastAPI(
    title="MCP Agent Hub",
    description="AI Agent platform powered by MCP & A2A protocols",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Initialize MCP Servers ──────────────────────────
db_server = DatabaseMCPServer()
fs_server = FilesystemMCPServer()
code_server = CodeExecutionMCPServer()

# ── Initialize Agents ───────────────────────────────
data_agent = DataAnalystAgent()
data_agent.mcp_client.connect(db_server)

research_agent = ResearchAgent()

code_agent = CodeAssistantAgent()
code_agent.mcp_client.connect(code_server)
code_agent.mcp_client.connect(fs_server)

# ── Register Agents ─────────────────────────────────
registry = AgentRegistry()
registry.register(data_agent)
registry.register(research_agent)
registry.register(code_agent)

orchestrator = AgentOrchestrator(registry)


# ── Request/Response Models ─────────────────────────

class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=10000)
    agent: str | None = Field(
        default=None,
        description="Force routing to a specific agent",
    )


class ChatResponse(BaseModel):
    agent: str | None
    response: str
    error: bool = False


class ToolCallRequest(BaseModel):
    tool_name: str
    arguments: dict


# ── API Endpoints ───────────────────────────────────

@app.get("/health")
async def health():
    return {"status": "healthy", "agents": len(registry.list_agents())}


@app.get("/agents")
async def list_agents():
    """List all registered agents and their skills."""
    return [card.to_dict() for card in registry.list_agents()]


@app.get("/agents/{agent_name}/card")
async def get_agent_card(agent_name: str):
    """Get a specific agent's A2A Agent Card."""
    agent = registry.get(agent_name)
    if not agent:
        raise HTTPException(404, f"Agent not found: {agent_name}")
    return agent.agent_card.to_dict()


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Send a message to the agent hub."""
    if request.agent:
        # Direct routing
        agent = registry.get(request.agent)
        if not agent:
            raise HTTPException(404, f"Agent not found: {request.agent}")
        response = await agent.process(request.message)
        return ChatResponse(
            agent=request.agent, response=response
        )

    # Auto-routing via orchestrator
    result = await orchestrator.route(request.message)
    return ChatResponse(**result)


@app.get("/tools")
async def list_tools():
    """List all available MCP tools across all servers."""
    tools = []
    for server in [db_server, fs_server, code_server]:
        for tool in server.list_tools():
            tools.append({
                "server": server.info.name,
                "name": tool.name,
                "description": tool.description,
            })
    return tools


@app.post("/tools/call")
async def call_tool(request: ToolCallRequest):
    """Directly invoke an MCP tool."""
    for server in [db_server, fs_server, code_server]:
        for tool in server.list_tools():
            if tool.name == request.tool_name:
                result = await server.call_tool(
                    request.tool_name, request.arguments
                )
                return {
                    "content": result.content,
                    "is_error": result.is_error,
                    "metadata": result.metadata,
                }

    raise HTTPException(404, f"Tool not found: {request.tool_name}")
