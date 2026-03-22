"""
MCP Agent Hub — Main Entry Point.

Starts the platform components: API server or CLI.
"""

from __future__ import annotations

import argparse
import asyncio
import sys
import logging
import uvicorn

from .api.app import app
from .api.app import registry, orchestrator

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

logger = logging.getLogger(__name__)


async def run_cli():
    """Run the platform in interactive CLI mode."""
    print("=" * 60)
    print("🌐 MCP Agent Hub - Interactive CLI")
    print("=" * 60)
    print("Type 'exit' or 'quit' to stop.")
    print("Available agents:", ", ".join(a.name for a in registry.list_agents()))
    print()

    while True:
        try:
            user_input = input("\nYou: ").strip()
            if user_input.lower() in ("exit", "quit"):
                break
            if not user_input:
                continue

            print("\nOrchestrating...", flush=True)
            result = await orchestrator.route(user_input)

            agent_name = result["agent"]
            response = result["response"]

            print(f"\n[Agent: {agent_name}]")
            print("-" * 40)
            print(response)
            print("-" * 40)

        except KeyboardInterrupt:
            break
        except Exception as e:
            logger.error(f"Error processing query: {e}")

    print("\nGoodbye!")


def main():
    """Main application entry point."""
    parser = argparse.ArgumentParser(description="MCP Agent Hub")
    parser.add_argument(
        "--mode", 
        choices=["api", "cli"], 
        default="cli",
        help="Run mode: 'api' for REST server, 'cli' for interactive terminal"
    )
    parser.add_argument(
        "--port", 
        type=int, 
        default=8000,
        help="Port for API server (default: 8000)"
    )

    args = parser.parse_args()

    if args.mode == "api":
        logger.info(f"Starting API server on port {args.port}")
        uvicorn.run(app, host="0.0.0.0", port=args.port)
    elif args.mode == "cli":
        asyncio.run(run_cli())


if __name__ == "__main__":
    main()
