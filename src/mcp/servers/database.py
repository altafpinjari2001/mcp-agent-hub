"""
MCP Agent Hub — Database MCP Server.

Exposes SQLite database operations as MCP tools.
Tools: query, get_schema, list_tables, insert_row.
"""

from __future__ import annotations

import sqlite3
import json
import logging
from pathlib import Path

from ..server import BaseMCPServer
from ..types import ToolDefinition, ToolParameter, ToolInputType, ToolResult

logger = logging.getLogger(__name__)


class DatabaseMCPServer(BaseMCPServer):
    """
    MCP Server for SQLite database operations.

    Provides tools for querying, inspecting schemas,
    and modifying SQLite databases.
    """

    def __init__(self, db_path: str = "data/database.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        super().__init__(
            name="database-server",
            version="1.0.0",
            description="SQLite database tools for querying and managing data",
        )

    def _register_tools(self) -> None:
        self.register_tool(ToolDefinition(
            name="query",
            description="Execute a SQL query and return results as JSON",
            parameters=[
                ToolParameter(
                    name="sql",
                    type=ToolInputType.STRING,
                    description="SQL query to execute (SELECT only for safety)",
                ),
            ],
        ))

        self.register_tool(ToolDefinition(
            name="get_schema",
            description="Get the schema of a specific table",
            parameters=[
                ToolParameter(
                    name="table_name",
                    type=ToolInputType.STRING,
                    description="Name of the table",
                ),
            ],
        ))

        self.register_tool(ToolDefinition(
            name="list_tables",
            description="List all tables in the database",
            parameters=[],
        ))

    async def _execute_tool(
        self, tool_name: str, arguments: dict
    ) -> ToolResult:
        match tool_name:
            case "query":
                return await self._query(arguments["sql"])
            case "get_schema":
                return await self._get_schema(arguments["table_name"])
            case "list_tables":
                return await self._list_tables()
            case _:
                return ToolResult(
                    content=f"Unknown tool: {tool_name}",
                    is_error=True,
                )

    async def _query(self, sql: str) -> ToolResult:
        """Execute a read-only SQL query."""
        # Safety: only allow SELECT statements
        if not sql.strip().upper().startswith("SELECT"):
            return ToolResult(
                content="Only SELECT queries are allowed for safety",
                is_error=True,
            )

        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(sql)
            rows = [dict(row) for row in cursor.fetchall()]
            conn.close()

            return ToolResult(
                content=json.dumps(rows, indent=2, default=str),
                metadata={"row_count": len(rows)},
            )
        except sqlite3.Error as e:
            return ToolResult(content=str(e), is_error=True)

    async def _get_schema(self, table_name: str) -> ToolResult:
        """Get table schema."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.execute(
                f"PRAGMA table_info({table_name})"
            )
            columns = [
                {
                    "name": row[1],
                    "type": row[2],
                    "nullable": not row[3],
                    "primary_key": bool(row[5]),
                }
                for row in cursor.fetchall()
            ]
            conn.close()

            return ToolResult(
                content=json.dumps(columns, indent=2),
                metadata={"table": table_name},
            )
        except sqlite3.Error as e:
            return ToolResult(content=str(e), is_error=True)

    async def _list_tables(self) -> ToolResult:
        """List all tables in the database."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.execute(
                "SELECT name FROM sqlite_master "
                "WHERE type='table' ORDER BY name"
            )
            tables = [row[0] for row in cursor.fetchall()]
            conn.close()

            return ToolResult(
                content=json.dumps(tables, indent=2),
                metadata={"table_count": len(tables)},
            )
        except sqlite3.Error as e:
            return ToolResult(content=str(e), is_error=True)
