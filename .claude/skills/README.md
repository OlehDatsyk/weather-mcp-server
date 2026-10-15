# Weather MCP Server - Agent Skill

Live weather, forecasts, city comparisons, air quality and official
weather alerts for your AI agent, powered by your own
[weather-mcp-server](references/setup.md) and the OpenWeatherMap API.

This skill teaches an agent **when** and **how** to use the five tools of
the weather-mcp-server: which tool fits which question, which arguments to
send, how to read the results, how to recover from errors, and how to
present the answer clearly.

## What you need

This is an instruction-only skill. It works **together with** the
weather-mcp-server MCP server, which you install separately:

1. Python 3.12+ and the weather-mcp-server project.
2. A free OpenWeatherMap API key.
3. An AI client that supports MCP servers and SKILL.md skills (for example
   Claude Code or the Claude desktop app).

Installing the skill does not install the server. Full steps:
[`references/setup.md`](references/setup.md).

## Features

| Tool | What the agent can do |
|---|---|
| `get_current_weather` | Current temperature, feels-like, humidity, wind, clouds, visibility, sunrise/sunset |
| `get_weather_forecast` | 1-5 day forecast in 3-hour steps, incl. chance of rain |
| `compare_cities` | Compare 2-10 cities side by side; names the warmest, coldest and most humid |
| `get_air_quality` | AQI (1-5) and PM2.5, PM10, O3, NO2, SO2, CO, NO, NH3 |
| `get_weather_alerts` | Official warnings (needs a One Call subscription on OpenWeatherMap; otherwise returns a clear note) |

The skill also covers the server's three resources
(`weather://cities/supported`, `weather://units`, `weather://api/info`) and
three prompts (`weather_summary`, `travel_recommendation`,
`clothing_recommendation`).

## Limits (honest list)

- City names only - no coordinates, postcodes or airport codes.
- No historical weather, no forecasts beyond 5 days, no maps or radar.
- Air quality is current only.
- Alerts depend on your OpenWeatherMap plan.

## Quick start

1. Install and configure the server - see `references/setup.md`.
2. Copy this folder to your agent's skills directory (Claude Code:
   `~/.claude/skills/weather-mcp-server/`).
3. Restart your client and ask: *"What's the weather in London, GB?"*

## Folder contents

| Path | Purpose |
|---|---|
| `SKILL.md` | The skill: activation rules, workflow, tool choice, output format, error handling, security |
| `references/tools.md` | Exact inputs and outputs of every tool, resource and prompt |
| `references/setup.md` | Server installation, client configuration, troubleshooting |
| `examples/` | Example questions, tool calls, results and good answers |
| `scripts/verify_server.py` | Optional read-only self-test you can run against your server |
| `LICENSE` | MIT |

## Security and privacy

- No API keys or secrets are included. Your key stays in your server's
  `.env` file on your machine.
- The skill tells the agent never to ask for, print or repeat your key.
- Only city names are sent to OpenWeatherMap (by the server, not the
  skill). The server logs city names in its local `logs/` folder.
- `scripts/verify_server.py` installs nothing, edits nothing and makes no
  network calls itself.

## Data attribution and licence

Weather data © OpenWeather, provided under OpenWeather's terms (the
self-service plans state commercial use is allowed and require visible
attribution). Check the current terms at <https://openweathermap.org/full-price>
before commercial use.

This skill is released under the MIT licence (see `LICENSE`).
