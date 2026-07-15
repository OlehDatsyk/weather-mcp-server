# INSTRUCTION.md

Quick operational reference for `weather-mcp-server`. For full details
(architecture, MCP background, troubleshooting), see [`README.md`](README.md).

## Quick Start (TL;DR)

```bash
# 1. Clone and enter the project
git clone https://github.com/your-username/weather-mcp-server.git
cd weather-mcp-server

# 2. Create and activate a virtual environment
python3 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\Activate.ps1

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure your API key
cp .env.example .env
# then edit .env and set OPENWEATHER_API_KEY

# 5. Run the tests (fully offline, no API key required)
pytest

# 6. Run the server (waits for an MCP client over stdio)
python server.py

# 7. Or launch it with the interactive MCP Inspector
npx @modelcontextprotocol/inspector python server.py
```

## What This Server Provides

- **5 tools**: `get_current_weather`, `get_weather_forecast`,
  `compare_cities`, `get_air_quality`, `get_weather_alerts`.
- **3 resources**: `weather://cities/supported`, `weather://units`,
  `weather://api/info`.
- **3 prompts**: `weather_summary`, `travel_recommendation`,
  `clothing_recommendation`.

## Required Environment Variable

| Variable               | Required | Description                                 |
|--------------------------|:----------:|------------------------------------------------|
| `OPENWEATHER_API_KEY`    | ✅         | Your OpenWeatherMap API key (free tier works). |

All other variables in `.env.example` have working defaults.

## Common Commands

| Task                                  | Command                                              |
|------------------------------------------|-----------------------------------------------------------|
| Install dependencies                      | `pip install -r requirements.txt`                          |
| Run the server                            | `python server.py`                                          |
| Run all tests                             | `pytest`                                                     |
| Run tests with verbose output             | `pytest -v`                                                  |
| Run a single test file                    | `pytest tests/test_tools.py`                                  |
| Launch the MCP Inspector                  | `npx @modelcontextprotocol/inspector python server.py`         |
| Debug in VS Code                          | Press `F5` (uses `.vscode/launch.json`)                        |

## Verifying the Setup

After installing dependencies and setting your API key, confirm everything
works end-to-end:

```bash
# Confirm the interpreter and dependencies are correct
python -c "import fastmcp, httpx, pydantic, loguru; print('OK')"

# Confirm configuration loads without error
python -c "from config import settings; print(settings.mcp_server_name, settings.has_api_key)"

# Run the full offline test suite
pytest -v

# Smoke-test the server starts (Ctrl+C to stop)
python server.py
```

If `pytest -v` passes and `python server.py` logs a "Starting
'weather-mcp-server'" message without a traceback, the project is correctly
set up.

## Where to Look Next

- [`README.md`](README.md) — full documentation, including MCP client setup.
- [`docs/architecture.md`](docs/architecture.md) — internal architecture and
  error-handling design.
- [`docs/mcp-primer.md`](docs/mcp-primer.md) — background on MCP tools,
  resources, and prompts.
