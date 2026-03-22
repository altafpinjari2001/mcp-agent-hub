"""
MCP Agent Hub — Data Analyst Agent.

Specialized agent for database queries, data analysis,
and insights generation using MCP database tools.
"""

from __future__ import annotations

import json
import logging

from .base import BaseAgent
from ..a2a.types import AgentSkill

logger = logging.getLogger(__name__)


class DataAnalystAgent(BaseAgent):
    """
    Data Analyst Agent.

    Specializes in:
    - Querying databases via MCP Database Server
    - Analyzing query results
    - Generating insights and summaries
    - Creating data visualizations (via Code Execution Server)
    """

    def __init__(self, port: int = 8001):
        super().__init__(
            name="DataAnalystAgent",
            description=(
                "Analyzes datasets, runs SQL queries, generates "
                "insights, and creates data visualizations."
            ),
            skills=[
                AgentSkill(
                    id="sql-analysis",
                    name="SQL Data Analysis",
                    description="Run SQL queries and analyze results",
                    tags=["sql", "database", "analytics"],
                    examples=[
                        "What are the top 10 customers by revenue?",
                        "Show me the churn rate by contract type",
                    ],
                ),
                AgentSkill(
                    id="data-insights",
                    name="Data Insights",
                    description="Generate actionable insights from data",
                    tags=["insights", "analysis", "summary"],
                ),
            ],
            port=port,
        )

    async def process(self, message: str) -> str:
        """
        Process a data analysis request.

        Workflow:
        1. List available tables
        2. Get relevant table schemas
        3. Construct and run SQL queries
        4. Analyze results and generate insights
        """
        logger.info(f"[{self.name}] Processing: {message[:100]}")

        # Step 1: Discover available data
        tables_result = await self.use_tool("list_tables", {})

        if tables_result.is_error:
            return f"Could not access database: {tables_result.content}"

        tables = json.loads(tables_result.content)

        if not tables:
            return "No tables found in the database."

        # Step 2: Get schema of first relevant table
        schemas = {}
        for table in tables[:3]:  # Limit to first 3 tables
            schema_result = await self.use_tool(
                "get_schema", {"table_name": table}
            )
            if not schema_result.is_error:
                schemas[table] = json.loads(schema_result.content)

        # Step 3: Build analysis context
        schema_summary = "\n".join(
            f"Table '{t}': {[c['name'] for c in cols]}"
            for t, cols in schemas.items()
        )

        # Step 4: Run a basic query
        if tables:
            query_result = await self.use_tool(
                "query",
                {"sql": f"SELECT * FROM {tables[0]} LIMIT 5"},
            )
            sample_data = query_result.content
        else:
            sample_data = "No data available"

        # Step 5: Generate analysis response
        response = (
            f"## Data Analysis Report\n\n"
            f"### Available Tables\n"
            f"{', '.join(tables)}\n\n"
            f"### Schema Overview\n"
            f"{schema_summary}\n\n"
            f"### Sample Data\n"
            f"```json\n{sample_data}\n```\n\n"
            f"### Query Request\n"
            f"{message}\n\n"
            f"*For detailed analysis, connect an LLM to this agent "
            f"to generate SQL queries dynamically based on the schema.*"
        )

        return response
