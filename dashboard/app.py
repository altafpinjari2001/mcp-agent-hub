"""
MCP Agent Hub — Streamlit Dashboard.

Visual interface for interacting with the agent hub.
"""

import streamlit as st
import asyncio
import httpx
import sys
from pathlib import Path

# Add project root to path for direct imports if needed
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

st.set_page_config(
    page_title="MCP Agent Hub Dashboard",
    page_icon="🤖",
    layout="wide",
)

API_URL = "http://localhost:8000"

st.title("🌐 MCP Agent Hub")
st.markdown("""
A cutting-edge AI Agent platform powered by **Model Context Protocol (MCP)** & **Agent-to-Agent (A2A)** communication.
""")

# Setup session state
if "messages" not in st.session_state:
    st.session_state.messages = []

# Sidebar
with st.sidebar:
    st.header("Hub Status")
    
    try:
        response = httpx.get(f"{API_URL}/health", timeout=2)
        if response.status_code == 200:
            st.success("API Server: Online")
            data = response.json()
            st.metric("Active Agents", data.get("agents", 0))
    except Exception:
        st.error("API Server: Offline")
        st.caption("Please start the API server first: `python -m src.main --mode api`")
        
    st.divider()
    
    st.header("Available Agents")
    try:
        agents = httpx.get(f"{API_URL}/agents", timeout=5).json()
        selected_agent = st.selectbox(
            "Force route to agent (optional)",
            options=["Auto (Orchestrator)"] + [a["name"] for a in agents]
        )
        
        for agent in agents:
            with st.expander(f"🤖 {agent['name']}"):
                st.caption(agent["description"])
                st.markdown("**Skills:**")
                for skill in agent.get("skills", []):
                    st.markdown(f"- {skill['name']}")
    except Exception:
        st.caption("Could not load agents.")
        selected_agent = "Auto (Orchestrator)"
        
    st.divider()
    
    st.header("Available Tools (MCP)")
    try:
        tools = httpx.get(f"{API_URL}/tools", timeout=5).json()
        
        # Group by server
        servers = {}
        for tool in tools:
            srv = tool["server"]
            if srv not in servers:
                servers[srv] = []
            servers[srv].append(tool)
            
        for server, srv_tools in servers.items():
            with st.expander(f"🔌 {server}"):
                for tool in srv_tools:
                    st.markdown(f"**`{tool['name']}`**")
                    st.caption(tool["description"])
    except Exception:
        st.caption("Could not load tools.")

# Main chat interface
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if "agent" in msg:
            st.caption(f"Handling Agent: {msg['agent']}")

prompt = st.chat_input("Ask the agent hub a question...")

if prompt:
    # Add user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Process via API
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        message_placeholder.markdown("*(Processing your request...)*")
        
        try:
            payload = {"message": prompt}
            if selected_agent != "Auto (Orchestrator)":
                payload["agent"] = selected_agent
                
            response = httpx.post(f"{API_URL}/chat", json=payload, timeout=60)
            
            if response.status_code == 200:
                data = response.json()
                reply = data.get("response", "")
                agent_used = data.get("agent", "Unknown")
                
                message_placeholder.markdown(reply)
                st.caption(f"Handled by: **{agent_used}**")
                
                st.session_state.messages.append({
                    "role": "assistant", 
                    "content": reply,
                    "agent": agent_used
                })
            else:
                error_msg = f"Error: {response.status_code} - {response.text}"
                message_placeholder.markdown(error_msg)
                st.session_state.messages.append({"role": "assistant", "content": error_msg})
                
        except httpx.ReadTimeout:
            err = "Request timed out. The agent took too long to respond."
            message_placeholder.error(err)
            st.session_state.messages.append({"role": "assistant", "content": err})
        except Exception as e:
            err = f"API connection error: {e}"
            message_placeholder.error(err)
            st.session_state.messages.append({"role": "assistant", "content": err})
