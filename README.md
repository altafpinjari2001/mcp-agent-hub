<div align="center">

# 🌐 MCP Agent Hub

**A cutting-edge AI Agent platform powered by Model Context Protocol (MCP) & Agent-to-Agent (A2A) communication**

[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![MCP](https://img.shields.io/badge/MCP-Protocol-FF6B6B?style=for-the-badge&logo=data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMjQiIGhlaWdodD0iMjQiIHZpZXdCb3g9IjAgMCAyNCAyNCIgZmlsbD0id2hpdGUiPjxwYXRoIGQ9Ik0xMiAyQTEwIDEwIDAgMCAyIDEyIDIyIDEwIDEwIDAgMCAyIDEyIDJNMTIgNEE4IDggMCAwIDAgNCAxMiA4IDggMCAwIDAgMTIgMjAgOCA4IDAgMCAwIDIwIDEyIDggOCAwIDAgMCAxMiA0TTEyIDZBNiA2IDAgMCAxIDE4IDEyIDYgNiAwIDAgMSAxMiAxOCA2IDYgMCAwIDEgNiAxMiA2IDYgMCAwIDEgMTIgNiIvPjwvc3ZnPg==)](https://modelcontextprotocol.io)
[![A2A](https://img.shields.io/badge/A2A-Protocol-4285F4?style=for-the-badge&logo=google&logoColor=white)](https://google.github.io/A2A)
[![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge)](LICENSE)

[Features](#-features) • [Architecture](#-architecture) • [Quick Start](#-quick-start) • [MCP Servers](#-mcp-servers) • [A2A Protocol](#-a2a-protocol)

</div>

---

## 📌 Overview

A **production-ready AI agent platform** that combines two of the most cutting-edge protocols in the AI ecosystem:

- **MCP (Model Context Protocol)** — Anthropic's open protocol for connecting AI agents to external tools, data sources, and APIs through a standardized interface
- **A2A (Agent-to-Agent)** — Google's protocol for autonomous agent communication, enabling agents to discover, negotiate, and collaborate with each other

This project demonstrates how to build **interoperable, tool-augmented AI agents** that can access databases, search the web, manage files, execute code — and delegate tasks to other specialized agents.

---

## ✨ Features

- 🔌 **4 Custom MCP Servers** — Database, filesystem, web search, and code execution tools
- 🤝 **A2A Agent Communication** — Agents discover and delegate tasks to each other
- 🧠 **Agent Orchestrator** — Routes tasks to the best-suited agent automatically
- 📋 **Agent Card Discovery** — Agents advertise their capabilities via JSON agent cards
- 🔒 **Secure Tool Execution** — Sandboxed code execution with resource limits
- ⚡ **Streaming Responses** — Server-Sent Events for real-time agent output
- 🏗️ **FastAPI Backend** — Production-grade API with OpenAPI documentation
- 🧪 **Comprehensive Tests** — Unit tests for all MCP servers and A2A protocols
- 📊 **Agent Dashboard** — Streamlit UI for interacting with agents

---

## 🏗 Architecture

```
┌────────────────────────────────────────────────────────────────────┐
│                       MCP Agent Hub                                │
│                                                                    │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │                   Agent Orchestrator                         │  │
│  │     Routes tasks │ Manages agents │ Handles A2A discovery   │  │
│  └────────────┬─────────────────────────────┬──────────────────┘  │
│               │                             │                      │
│     ┌─────────▼──────────┐       ┌──────────▼─────────┐          │
│     │   MCP Client       │       │   A2A Protocol      │          │
│     │   (Tool Access)    │       │   (Agent-to-Agent)  │          │
│     └─────────┬──────────┘       └──────────┬─────────┘          │
│               │                             │                      │
│  ┌────────────▼────────────────────────────────────────────────┐  │
│  │                    MCP Servers (Tools)                       │  │
│  │                                                              │  │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌────────────┐  │  │
│  │  │ Database │  │   File   │  │   Web    │  │   Code     │  │  │
│  │  │  Server  │  │  System  │  │  Search  │  │ Execution  │  │  │
│  │  │          │  │  Server  │  │  Server  │  │  Server    │  │  │
│  │  │ SQLite   │  │ Read/    │  │ Tavily   │  │ Sandboxed  │  │  │
│  │  │ Query    │  │ Write/   │  │ Search   │  │ Python     │  │  │
│  │  │ Schema   │  │ List     │  │ Scrape   │  │ Execution  │  │  │
│  │  └──────────┘  └──────────┘  └──────────┘  └────────────┘  │  │
│  └─────────────────────────────────────────────────────────────┘  │
│                                                                    │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │                    Agent Registry (A2A)                       │  │
│  │                                                              │  │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────────┐   │  │
│  │  │ Data Analyst │  │  Research    │  │  Code Assistant  │   │  │
│  │  │    Agent     │  │    Agent     │  │     Agent        │   │  │
│  │  │              │  │              │  │                  │   │  │
│  │  │ DB queries,  │  │ Web search,  │  │ Code gen,        │   │  │
│  │  │ analysis,    │  │ summarize,   │  │ debug, execute,  │   │  │
│  │  │ viz          │  │ cite sources │  │ explain          │   │  │
│  │  └──────────────┘  └──────────────┘  └──────────────────┘   │  │
│  └─────────────────────────────────────────────────────────────┘  │
└────────────────────────────────────────────────────────────────────┘
```

---

## 🚀 Quick Start

```bash
git clone https://github.com/altafpinjari2001/mcp-agent-hub.git
cd mcp-agent-hub

python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env
# Add your API keys

# Start the platform
python -m src.main

# Or use the API
uvicorn src.api.app:app --reload --port 8000

# Or use the Streamlit dashboard
streamlit run dashboard/app.py
```

---

## 🔌 MCP Servers

Each MCP server exposes tools through the standardized Model Context Protocol:

### 1. Database Server (`SQLite`)
```python
# Tools: query, get_schema, list_tables, insert, update
result = await db_server.call_tool("query", {
    "sql": "SELECT * FROM customers WHERE churn = 1 LIMIT 5"
})
```

### 2. Filesystem Server
```python
# Tools: read_file, write_file, list_directory, search_files
result = await fs_server.call_tool("read_file", {
    "path": "data/report.md"
})
```

### 3. Web Search Server (`Tavily`)
```python
# Tools: search, scrape_url, get_news
result = await web_server.call_tool("search", {
    "query": "latest MCP protocol updates 2025"
})
```

### 4. Code Execution Server (Sandboxed)
```python
# Tools: execute_python, analyze_code, install_package
result = await code_server.call_tool("execute_python", {
    "code": "import pandas as pd; print(pd.__version__)"
})
```

---

## 🤝 A2A Protocol

Agents discover and communicate with each other using Google's Agent-to-Agent protocol:

### Agent Card (Discovery)
```json
{
  "name": "DataAnalystAgent",
  "description": "Analyzes datasets, runs SQL queries, creates visualizations",
  "url": "http://localhost:8001",
  "capabilities": {
    "streaming": true,
    "pushNotifications": false
  },
  "skills": [
    {"id": "sql-analysis", "name": "SQL Analysis"},
    {"id": "data-viz", "name": "Data Visualization"}
  ]
}
```

### Task Delegation
```python
# Agent A discovers Agent B and delegates a task
agent_card = await a2a_client.discover("http://localhost:8001")
task = await a2a_client.send_task(
    agent_url=agent_card.url,
    message="Analyze customer churn data and find top 3 factors",
)
result = await a2a_client.get_task_result(task.id)
```

---

## 📁 Project Structure

```
mcp-agent-hub/
├── src/
│   ├── __init__.py
│   ├── main.py                    # Platform entry point
│   ├── mcp/                       # MCP Protocol Implementation
│   │   ├── __init__.py
│   │   ├── server.py              # Base MCP server class
│   │   ├── client.py              # MCP client for tool access
│   │   ├── types.py               # MCP protocol types
│   │   └── servers/               # Tool Servers
│   │       ├── database.py        # SQLite database tools
│   │       ├── filesystem.py      # File system tools
│   │       ├── web_search.py      # Web search tools
│   │       └── code_executor.py   # Code execution tools
│   ├── a2a/                       # A2A Protocol Implementation
│   │   ├── __init__.py
│   │   ├── agent_card.py          # Agent discovery cards
│   │   ├── client.py              # A2A client (task sender)
│   │   ├── server.py              # A2A server (task receiver)
│   │   └── types.py               # A2A protocol types
│   ├── agents/                    # AI Agents
│   │   ├── __init__.py
│   │   ├── base.py                # Base agent class
│   │   ├── data_analyst.py        # Data analysis agent
│   │   ├── researcher.py          # Research agent
│   │   └── code_assistant.py      # Code assistant agent
│   ├── orchestrator/              # Agent Orchestrator
│   │   ├── __init__.py
│   │   ├── router.py              # Task routing logic
│   │   └── registry.py            # Agent registry
│   └── api/                       # FastAPI Backend
│       ├── app.py                 # API application
│       └── routes.py              # API endpoints
├── dashboard/
│   └── app.py                     # Streamlit dashboard
├── tests/
│   ├── test_mcp_servers.py
│   └── test_a2a_protocol.py
├── configs/
│   └── agents.yaml                # Agent configuration
├── .env.example
├── requirements.txt
├── LICENSE
├── .gitignore
└── .github/workflows/ci.yml
```

---

## 🧩 How MCP & A2A Work Together

```
                    User Query
                        │
                        ▼
              ┌─────────────────┐
              │   Orchestrator  │  ← Routes to best agent
              └────────┬────────┘
                       │
            ┌──────────▼──────────┐
            │   Selected Agent    │
            │   (e.g. Research)   │
            └──────────┬──────────┘
                       │
         ┌─────────────┼─────────────┐
         ▼             ▼             ▼
    ┌─────────┐  ┌──────────┐  ┌─────────┐
    │ MCP     │  │ MCP      │  │ A2A     │
    │ Web     │  │ File     │  │ Delegate│
    │ Search  │  │ System   │  │ to Code │
    │ Server  │  │ Server   │  │ Agent   │
    └─────────┘  └──────────┘  └─────────┘
    (tool call)  (tool call)   (agent call)
```

1. **User asks** → Orchestrator routes to the right agent
2. **Agent uses MCP** → Calls tools (search, database, files) via MCP protocol
3. **Agent uses A2A** → Delegates sub-tasks to other specialized agents
4. **Results combine** → Final response returned to user

---

## 📄 License

MIT License — see [LICENSE](LICENSE) for details.

<div align="center"><b>⭐ Star this repo if you find it useful!</b></div>
