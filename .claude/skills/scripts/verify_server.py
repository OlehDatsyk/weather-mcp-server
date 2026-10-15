#!/usr/bin/env python3
"""
verify_server.py - read-only health check for a local weather-mcp-server.

What it does
------------
1. Starts YOUR existing weather-mcp-server (server.py) as a child process
   over stdio, exactly as an MCP client would.
2. Lists the tools, resources and prompts it exposes and checks that the
   names this skill relies on are all present.
3. Optionally (with --city) calls `get_current_weather` once and prints
   the JSON result, so you can confirm your API key works.

What it does NOT do
-------------------
- It does not install anything, edit any file, or read your .env file.
  The server process reads its own configuration, as it always does.
- It does not contact any network address itself. Only the server makes
  requests to OpenWeatherMap, and only when --city is given.

Usage (run with the Python interpreter from the project's own virtual
environment, because it needs the `fastmcp` package installed there):

    macOS / Linux:
        /path/to/weather-mcp-server/.venv/bin/python verify_server.py \
            --project /path/to/weather-mcp-server

    Windows (PowerShell):
        C:\\path\\to\\weather-mcp-server\\.venv\\Scripts\\python.exe verify_server.py `
            --project C:\\path\\to\\weather-mcp-server

    Add  --city "London,GB"  to make one live tool call.

Exit codes: 0 = all expected capabilities found (and the optional call
returned data); 1 = something is missing or the call returned an error;
2 = the server could not be started.
"""

from __future__ import annotations

import argparse
import asyncio
import json
import sys
from pathlib import Path

EXPECTED_TOOLS = {
    "get_current_weather",
    "get_weather_forecast",
    "compare_cities",
    "get_air_quality",
    "get_weather_alerts",
}
EXPECTED_RESOURCES = {
    "weather://cities/supported",
    "weather://units",
    "weather://api/info",
}
EXPECTED_PROMPTS = {
    "weather_summary",
    "travel_recommendation",
    "clothing_recommendation",
}


def _report(label: str, found: set[str], expected: set[str]) -> bool:
    """Print found vs expected names; return True when nothing is missing."""
    missing = expected - found
    print(f"{label}: {', '.join(sorted(found)) or '(none)'}")
    if missing:
        print(f"  MISSING: {', '.join(sorted(missing))}")
    return not missing


async def _run(server_py: Path, city: str | None) -> int:
    try:
        from fastmcp import Client  # provided by the project's requirements.txt
    except ImportError:
        print(
            "ERROR: 'fastmcp' is not importable. Run this script with the Python "
            "from the weather-mcp-server virtual environment (.venv)."
        )
        return 2

    try:
        async with Client(str(server_py)) as client:
            tools = {t.name for t in await client.list_tools()}
            resources = {str(r.uri) for r in await client.list_resources()}
            prompts = {p.name for p in await client.list_prompts()}

            ok = _report("Tools", tools, EXPECTED_TOOLS)
            ok &= _report("Resources", resources, EXPECTED_RESOURCES)
            ok &= _report("Prompts", prompts, EXPECTED_PROMPTS)

            info = await client.read_resource("weather://api/info")
            api_info = json.loads(info[0].text)
            print(f"API key configured on server: {api_info.get('api_key_configured')}")

            if city:
                result = await client.call_tool("get_current_weather", {"city": city})
                data = result.data if result.data is not None else result.structured_content
                print(json.dumps(data, indent=2, default=str))
                if isinstance(data, dict) and data.get("error"):
                    ok = False

            print("RESULT:", "OK" if ok else "PROBLEMS FOUND")
            return 0 if ok else 1
    except Exception as exc:  # report start-up failures plainly
        print(f"ERROR: could not start or talk to the server: {exc}")
        return 2


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[1])
    parser.add_argument(
        "--project",
        required=True,
        help="Path to your weather-mcp-server folder (the one containing server.py).",
    )
    parser.add_argument(
        "--city",
        default=None,
        help="Optional city for one live get_current_weather call, e.g. 'London,GB'.",
    )
    args = parser.parse_args()

    server_py = Path(args.project).expanduser().resolve() / "server.py"
    if not server_py.is_file():
        print(f"ERROR: server.py not found at {server_py}")
        sys.exit(2)

    sys.exit(asyncio.run(_run(server_py, args.city)))


if __name__ == "__main__":
    main()
