"""Tests for MCP servers."""
import pytest
from src.mcp.servers.filesystem import FilesystemMCPServer
from src.mcp.servers.code_executor import CodeExecutionMCPServer

@pytest.mark.asyncio
async def test_fs_server_read_write(tmp_path):
    server = FilesystemMCPServer(workspace=str(tmp_path))
    
    # Write test
    write_res = await server.call_tool("write_file", {
        "path": "test.txt",
        "content": "hello world"
    })
    assert not write_res.is_error
    
    # Read test 
    read_res = await server.call_tool("read_file", {
        "path": "test.txt"
    })
    assert not read_res.is_error
    assert read_res.content == "hello world"

@pytest.mark.asyncio
async def test_code_server_execute():
    server = CodeExecutionMCPServer()
    
    res = await server.call_tool("execute_python", {
        "code": "print('hello from sandbox')"
    })
    
    assert not res.is_error
    assert "hello from sandbox" in res.content

@pytest.mark.asyncio
async def test_code_server_safety():
    server = CodeExecutionMCPServer()
    
    res = await server.call_tool("execute_python", {
        "code": "import os"
    })
    
    assert res.is_error
    assert "Blocked" in res.content
