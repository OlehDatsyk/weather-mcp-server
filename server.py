"""
server.py
=========
Entry point for the Weather MCP Server.

This module wires together configuration, logging, the weather service
layer, and all MCP tools/resources/prompts into a single ``FastMCP``
application, then runs it over stdio so any MCP-compatible client (Claude
Desktop, the MCP Inspector, custom clients, etc.) can connect to it.

Run directly:
    python server.py

Or via the MCP Inspector for interactive debugging:
    npx @modelcontextprotocol/inspector python server.py
"""

from __future__ import annotations

import asyncio
import os
import sys

from fastmcp import FastMCP

from config import settings
from logging_config import configure_logging, get_logger
from prompts import register_prompts
from resources import register_resources
from tools import register_tools
from weather_service import WeatherService

configure_logging()
logger = get_logger(__name__)

# ---------------------------------------------------------------------------
# Build the FastMCP application
# ---------------------------------------------------------------------------
mcp: FastMCP = FastMCP(
    name=settings.mcp_server_name,
    instructions=(
        "This server provides weather-related tools, resources, and prompts. "
        "Use `get_current_weather` for current conditions, "
        "`get_weather_forecast` for multi-day forecasts, `compare_cities` to "
        "compare multiple locations, `get_air_quality` for pollution data, and "
        "`get_weather_alerts` for active official warnings. Read the "
        "`weather://cities/supported`, `weather://units`, and "
        "`weather://api/info` resources for reference data. Prompts "
        "`weather_summary`, `travel_recommendation`, and "
        "`clothing_recommendation` provide ready-made conversation starters."
    ),
)

# A single, shared WeatherService instance reused across all tool calls for
# the lifetime of the process, enabling HTTP connection pooling.
weather_service = WeatherService()

# Register all MCP capabilities against the shared app + service.
register_tools(mcp, weather_service)
register_resources(mcp)
register_prompts(mcp)


async def _run() -> None:
    """
    Start the shared HTTP client, run the MCP server until the client
    disconnects, and guarantee the HTTP client is cleanly closed afterward.
    """
    logger.info(
        "Starting '{}' (API key configured: {})",
        settings.mcp_server_name,
        settings.has_api_key,
    )
    if not settings.has_api_key:
        logger.warning(
            "OPENWEATHER_API_KEY is not set. Tools will return a structured "
            "error until a valid key is configured in your .env file."
        )

    await weather_service.start()
    try:
        # Render (and most hosting platforms) set PORT to tell the app which
        # port to listen on. When it's present, run over streamable HTTP so
        # the server is reachable as a normal web service. Otherwise (e.g.
        # when launched locally by Claude Desktop or the MCP Inspector),
        # fall back to the default stdio transport used for local clients.
        port = os.environ.get("PORT")
        if port:
            logger.info("PORT is set ({}); running over HTTP transport.", port)
            await mcp.run_async(transport="http", host="0.0.0.0", port=int(port))
        else:
            await mcp.run_async()
    finally:
        await weather_service.close()
        logger.info("Weather MCP Server stopped cleanly.")


def main() -> None:
    """Synchronous entry point used by ``python server.py``."""
    try:
        asyncio.run(_run())
    except KeyboardInterrupt:
        logger.info("Interrupted by user (Ctrl+C). Shutting down.")
        sys.exit(0)


if __name__ == "__main__":
    main()
