# weather-mcp-server

A production-ready **Model Context Protocol (MCP) server** that provides
weather-related **tools**, **resources**, and **prompts** to any
MCP-compatible client (Claude Desktop, the MCP Inspector, or a custom
client), backed by the OpenWeatherMap API.

Built with **Python 3.12+**, **FastMCP**, **HTTPX**, **Pydantic v2**,
**python-dotenv**, and **Loguru**, with a full **Pytest** test suite.

---

## Table of Contents

- [Project Overview](#project-overview)
- [What is MCP?](#what-is-mcp)
- [Why MCP Matters](#why-mcp-matters)
- [Architecture](#architecture)
- [Folder Structure](#folder-structure)
- [Capabilities](#capabilities)
  - [Tools](#tools)
  - [Resources](#resources)
  - [Prompts](#prompts)
- [Installation Guide](#installation-guide)
  - [1. Install Python](#1-install-python)
  - [2. Visual Studio Code Setup](#2-visual-studio-code-setup)
  - [3. Clone / Open the Project](#3-clone--open-the-project)
  - [4. Create a Virtual Environment](#4-create-a-virtual-environment)
  - [5. Install Dependencies](#5-install-dependencies)
  - [6. API Key Setup](#6-api-key-setup)
- [Running the MCP Server](#running-the-mcp-server)
- [Connecting with an MCP Client](#connecting-with-an-mcp-client)
  - [Claude Desktop](#claude-desktop)
  - [MCP Inspector](#mcp-inspector)
- [Testing](#testing)
- [Troubleshooting](#troubleshooting)
- [Future Improvements](#future-improvements)
- [License](#license)

---

## Project Overview

`weather-mcp-server` exposes weather data - current conditions, forecasts,
multi-city comparisons, air quality, and severe weather alerts - as
standardized **MCP tools, resources, and prompts**. It is designed as a
reference-quality example of a real-world MCP server: cleanly layered,
fully typed, structured-output-first, thoroughly logged, gracefully
error-handled, and fully unit/integration tested.

Key design goals:

- **Clean architecture** - HTTP/API concerns, business logic, and MCP glue
  code live in separate, single-responsibility modules (see
  [Architecture](#architecture) and [`docs/architecture.md`](docs/architecture.md)).
- **Structured everything** - every tool returns a well-typed, validated
  Pydantic model (dumped to JSON), including a *structured error* shape on
  failure - never a raw exception or free-text error string.
- **Production hygiene** - environment-based configuration, rotating file
  logs via Loguru, retry logic for transient HTTP failures, and graceful
  degradation (e.g. when weather alerts require a paid API plan).
- **Fully tested** - `pytest` + `respx` mock all outbound HTTP calls, so the
  entire suite runs offline, deterministically, with no API key required.

## What is MCP?

The **Model Context Protocol (MCP)** is an open, JSON-RPC 2.0-based
standard that lets AI applications ("clients") connect to external systems
("servers") that expose data and capabilities in a uniform way - tools the
model can call, resources it can read, and prompts it can use as
conversation starters. See [`docs/mcp-primer.md`](docs/mcp-primer.md) for a
deeper, example-driven explanation of all three primitives as implemented
in this project.

## Why MCP Matters

Without a shared protocol, every AI application needs a bespoke integration
with every external tool or data source - the classic **MxN problem** (M
applications x N tools = MxN integrations). MCP turns this into an
**M+N problem**: build one MCP server per data source, one MCP client per
application, and any client can talk to any server. This yields:

- **Standardization** instead of bespoke glue code per application.
- **Reusability** - this server works unmodified with any MCP client.
- **Discoverability** - clients can programmatically enumerate tools,
  resources, and prompts along with their JSON Schemas.
- **Structured, typed interactions** rather than the model having to parse
  ad-hoc API responses itself.

## Architecture

```
MCP Client (Claude Desktop / MCP Inspector / custom)
        │  JSON-RPC over stdio
        ▼
server.py  - builds FastMCP app, owns lifecycle, wires everything together
        │
   ┌────┼──────────────┬───────────────┐
   ▼                   ▼               ▼
tools.py         resources.py     prompts.py
(5 MCP tools)   (3 MCP resources) (3 MCP prompts)
   │
   ▼
weather_service.py  - httpx.AsyncClient wrapper around OpenWeatherMap
   │
   ▼
schemas.py  - Pydantic v2 models (inputs, structured outputs, errors)

Cross-cutting: config.py (Pydantic Settings) + logging_config.py (Loguru)
```

`weather_service.py` never imports `fastmcp`, and `tools.py` never talks to
`httpx` directly - this separation keeps business logic independently
testable and the MCP-specific glue code minimal. Full details, including
the error-handling strategy and graceful-degradation behavior for weather
alerts, are documented in [`docs/architecture.md`](docs/architecture.md).

## Folder Structure

```
weather-mcp-server/
├── README.md # This file
├── INSTRUCTION.md # Quick-start / operational instructions
├── LICENSE # MIT License
├── .gitignore
├── requirements.txt # Python dependencies
├── .env.example # Documented environment variable template
├── pytest.ini # Pytest configuration
├── server.py # MCP server entry point
├── config.py # Pydantic Settings (env-based configuration)
├── weather_service.py # OpenWeatherMap API client + business logic
├── tools.py # MCP tool registrations
├── resources.py # MCP resource registrations
├── prompts.py # MCP prompt registrations
├── schemas.py # Pydantic v2 models (I/O + errors)
├── logging_config.py # Loguru configuration
├── tests/
│   ├── __init__.py
│   ├── conftest.py # Shared fixtures (fake API responses, etc.)
│   ├── test_schemas.py # Pydantic model validation tests
│   ├── test_weather_service.py # Service-layer tests (respx-mocked HTTP)
│   ├── test_tools.py # End-to-end MCP tool tests
│   └── test_resources_and_prompts.py
├── docs/
│   ├── architecture.md # Deep-dive architecture documentation
│   └── mcp-primer.md # MCP concepts primer (tools/resources/prompts)
└── .vscode/
    ├── settings.json # Python interpreter, test discovery, linting
    ├── launch.json # Run/debug configurations
    └── extensions.json # Recommended VS Code extensions
```

## Capabilities

### Tools

| Tool                    | Description                                                                 |
|--------------------------|-------------------------------------------------------------------------------|
| `get_current_weather`    | Current temperature, humidity, wind, cloudiness, and conditions for a city.    |
| `get_weather_forecast`   | 1-5 day / 3-hour-resolution forecast for a city.                                |
| `compare_cities`         | Side-by-side current-weather comparison across 2-10 cities.                     |
| `get_air_quality`        | Air Quality Index (1-5) and pollutant concentrations (CO, NO2, O3, PM2.5, etc). |
| `get_weather_alerts`     | Active official severe-weather alerts/warnings for a city.                       |

Every tool:

- Validates input via type hints (FastMCP auto-generates JSON Schema).
- Returns a **structured, JSON-serializable Pydantic model** on success.
- Returns a **structured `ToolError`** object (`error`, `error_type`,
  `message`) on failure - never an unhandled exception.

### Resources

| Resource URI                 | Description                                                          |
|--------------------------------|--------------------------------------------------------------------------|
| `weather://cities/supported`   | Curated list of popular, well-known cities.                                |
| `weather://units`              | Supported unit systems (`metric`, `imperial`, `standard`) and their meaning. |
| `weather://api/info`           | Metadata about the underlying weather API: endpoints used, rate limits, key status. |

### Prompts

| Prompt                      | Description                                                             |
|-------------------------------|-------------------------------------------------------------------------|
| `weather_summary`             | Friendly, plain-language weather briefing for a city.                     |
| `travel_recommendation`       | Forecast- and alert-informed travel planning advice.                       |
| `clothing_recommendation`     | Practical what-to-wear advice based on current conditions.                  |

---

## Installation Guide

### 1. Install Python

This project requires **Python 3.12 or newer**.

- **Windows**: Download the installer from
  [python.org/downloads](https://www.python.org/downloads/) and make sure
  to check **"Add python.exe to PATH"** during installation.
- **macOS**: `brew install python@3.12` (via [Homebrew](https://brew.sh)),
  or download from [python.org](https://www.python.org/downloads/).
- **Linux**: Use your distribution's package manager, e.g.
  `sudo apt install python3.12 python3.12-venv` on Debian/Ubuntu.

Verify the installation:

```bash
python3 --version
# Python 3.12.x (or newer)
```

### 2. Visual Studio Code Setup

1. Install [Visual Studio Code](https://code.visualstudio.com/).
2. Install the following extensions (also listed in
   `.vscode/extensions.json`, which VS Code will prompt you to install
   automatically when you open the project):
   - **Python** (`ms-python.python`)
   - **Pylance** (`ms-python.vscode-pylance`)
   - **Python Debugger** (`ms-python.debugpy`)
   - **Ruff** (`charliermarsh.ruff`) - optional, for linting/formatting

### 3. Clone / Open the Project

```bash
git clone https://github.com/your-username/weather-mcp-server.git
cd weather-mcp-server
code .
```

(Or simply extract the project archive and open the folder in VS Code via
**File -> Open Folder...**.)

### 4. Create a Virtual Environment

From the integrated terminal in VS Code (**Terminal -> New Terminal**):

**macOS / Linux:**

```bash
python3 -m venv .venv
source .venv/bin/activate
```

**Windows (PowerShell):**

```powershell
py -3.12 -m venv .venv
.venv\Scripts\Activate.ps1
```

Once activated, VS Code should automatically detect `.venv` as the
workspace interpreter (configured in `.vscode/settings.json`). If it
doesn't, open the Command Palette (`Ctrl+Shift+P` / `Cmd+Shift+P`), run
**Python: Select Interpreter**, and choose `.venv`.

### 5. Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 6. API Key Setup

1. Create a free account at
   [OpenWeatherMap](https://home.openweathermap.org/users/sign_up).
2. Generate an API key from your
   [API keys dashboard](https://home.openweathermap.org/api_keys).
   > New keys can take a few minutes to a couple of hours to activate.
3. Copy the environment template and add your key:

   ```bash
   cp .env.example .env
   ```

4. Open `.env` and set:

   ```dotenv
   OPENWEATHER_API_KEY=your_actual_api_key_here
   ```

   All other variables in `.env` have sensible defaults (see
   `.env.example` for the full, documented list) and typically do not need
   to change.

---

## Running the MCP Server

MCP servers communicate over **stdio**, so running `server.py` directly in
a terminal will appear to "hang" - that's expected, it's waiting for an MCP
client to connect and speak JSON-RPC over stdin/stdout. This is still
useful to sanity-check that the server starts without errors:

```bash
python server.py
```

You should see Loguru startup logs on **stderr** (never stdout, which is
reserved for the MCP protocol), for example:

```
2026-07-15 12:00:00.000 | INFO     | server:_run:70 - Starting 'weather-mcp-server' (API key configured: True)
```

Press `Ctrl+C` to stop it.

To actually interact with it, use an MCP client - see the next section - or
launch it via the **"Run Weather MCP Server"** configuration already
defined in `.vscode/launch.json` (press `F5` in VS Code).

## Connecting with an MCP Client

### Claude Desktop

Add this server to Claude Desktop's MCP configuration file
(`claude_desktop_config.json`; on macOS at
`~/Library/Application Support/Claude/claude_desktop_config.json`, on
Windows at `%APPDATA%\Claude\claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "weather": {
      "command": "/absolute/path/to/weather-mcp-server/.venv/bin/python",
      "args": ["/absolute/path/to/weather-mcp-server/server.py"],
      "env": {
        "OPENWEATHER_API_KEY": "your_actual_api_key_here"
      }
    }
  }
}
```

> On Windows, use the path to `.venv\Scripts\python.exe`. Restart Claude
> Desktop after editing the config. You should then see this server's tools
> available in the 🔨 (tools) menu within a conversation.

### MCP Inspector

The [MCP Inspector](https://github.com/modelcontextprotocol/inspector) is
the standard interactive debugging tool for MCP servers. With Node.js
installed:

```bash
npx @modelcontextprotocol/inspector python server.py
```

This opens a browser UI where you can:

- Browse and invoke all 5 tools with live JSON Schema-driven forms.
- Read all 3 resources.
- Render all 3 prompts with sample arguments.
- Inspect raw JSON-RPC traffic for debugging.

---

## Testing

The full test suite runs **offline** - all HTTP calls to OpenWeatherMap are
intercepted by [`respx`](https://lundberg.github.io/respx/), so no API key
or network access is required to run the tests.

Run everything:

```bash
pytest
```

Run a specific file, with verbose output:

```bash
pytest tests/test_weather_service.py -v
```

Run with a coverage report (requires `pip install pytest-cov`):

```bash
pytest --cov=. --cov-report=term-missing
```

Test suite layout:

| File                                     | Covers                                                       |
|--------------------------------------------|------------------------------------------------------------------|
| `tests/test_schemas.py`                    | Pydantic model validation rules (no I/O).                          |
| `tests/test_weather_service.py`            | Service layer: success paths + every error path, HTTP-mocked.       |
| `tests/test_tools.py`                      | End-to-end MCP tool behavior via FastMCP's in-memory `Client`.       |
| `tests/test_resources_and_prompts.py`      | Resource/prompt registration and content correctness.               |

You can also run tests directly from VS Code's **Testing** sidebar (the
beaker icon), thanks to the pytest configuration in `.vscode/settings.json`.

---

## Troubleshooting

**`ModuleNotFoundError: No module named 'fastmcp'` (or similar)**
Your virtual environment isn't activated, or dependencies weren't
installed. Run `source .venv/bin/activate` (or the Windows equivalent) and
`pip install -r requirements.txt` again.

**Tools return `{"error": true, "error_type": "missing_api_key", ...}`**
`OPENWEATHER_API_KEY` is not set (or still the placeholder value) in your
`.env` file. Double-check `.env` exists (copied from `.env.example`) and
contains a real key.

**Tools return `{"error": true, "error_type": "upstream_api_error", ...}` with HTTP 401**
Your API key is invalid, or hasn't finished activating yet - new
OpenWeatherMap keys can take up to a couple of hours to become active.

**`get_weather_alerts` always returns an empty list with a note about "One Call API"**
This is expected on OpenWeatherMap's free tier for many accounts - the
alerts data comes from the "One Call API 3.0" endpoint, which may require a
separate (still free, but explicitly subscribed) plan. The server degrades
gracefully instead of failing; see
[`docs/architecture.md`](docs/architecture.md#graceful-degradation-weather-alerts).

**The server process seems to "hang" when run with `python server.py`**
This is expected - MCP servers communicate over stdio and wait for a
client to connect and issue JSON-RPC requests. Use the MCP Inspector or a
real client to interact with it (see
[Connecting with an MCP Client](#connecting-with-an-mcp-client)).

**Claude Desktop doesn't show the weather tools**
Double-check the absolute paths in `claude_desktop_config.json` (both the
Python interpreter path and the `server.py` path), that the JSON is valid,
and fully restart Claude Desktop (not just close the window) after editing
the config.

**`pytest` fails with connection errors**
All tests should be fully offline via `respx` mocking. If you see real
network errors, ensure you're running the tests as-is (don't remove the
`@respx.mock` decorators) and that `respx` is installed
(`pip install -r requirements.txt`).

---

## Future Improvements

- **Caching layer** - add a short-TTL in-memory (or Redis) cache for
  `get_current_weather` / `get_air_quality` to reduce redundant API calls
  for repeated queries within a short window.
- **Additional providers** - add an alternate weather data provider (e.g.
  Open-Meteo, which requires no API key) as a fallback for resilience.
- **Historical weather tool** - expose historical weather data for trend
  analysis, where supported by the underlying API plan.
- **Geolocation-based queries** - accept latitude/longitude directly, in
  addition to city names, for tools that currently require geocoding.
- **Rate-limit-aware backoff** - track OpenWeatherMap's rate-limit headers
  and proactively throttle rather than only reactively retrying.
- **Streaming/subscription resources** - explore MCP resource
  subscriptions to push severe weather alert updates to clients in
  near-real-time rather than requiring polling.
- **Packaging** - publish as an installable package (`pip install
  weather-mcp-server`) with a console-script entry point.
- **CI pipeline** - add a GitHub Actions workflow to run `pytest` and
  linting (`ruff`) on every push/PR.

---

## License

Released under the [MIT License](LICENSE).
