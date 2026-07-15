# Architecture

This document describes the internal architecture of `weather-mcp-server` in
more depth than the top-level README.

## Layered design

The project follows a simple, strict layering so each module has exactly one
responsibility:

```
┌─────────────────────────────────────────────────────────────┐
│                         MCP Client                            │
│        (Claude Desktop, MCP Inspector, custom client)         │
└───────────────────────────┬─────────────────────────────────┘
                             │ JSON-RPC over stdio
┌───────────────────────────▼─────────────────────────────────┐
│  server.py                                                    │
│  - Builds the FastMCP app                                     │
│  - Wires config, logging, service, tools/resources/prompts    │
│  - Owns the process lifecycle (startup / shutdown)             │
└───────────────────────────┬─────────────────────────────────┘
                             │
        ┌────────────────────┼────────────────────┐
        ▼                    ▼                    ▼
┌───────────────┐   ┌────────────────┐   ┌────────────────┐
│   tools.py     │   │  resources.py  │   │   prompts.py    │
│ 5 MCP tools    │   │ 3 MCP resources│   │ 3 MCP prompts    │
│ (actions)      │   │ (reference     │   │ (conversation    │
│                │   │  data)         │   │  starters)        │
└───────┬────────┘   └───────┬────────┘   └────────────────┘
        │                    │
        ▼                    ▼
┌─────────────────────────────────────────────────────────────┐
│  weather_service.py                                           │
│  - Owns the httpx.AsyncClient                                 │
│  - Talks to OpenWeatherMap (weather, forecast, geocoding,      │
│    air pollution, one-call/alerts)                             │
│  - Translates raw JSON -> schemas.py Pydantic models           │
│  - Translates HTTP failures -> typed WeatherServiceError       │
└───────────────────────────┬─────────────────────────────────┘
                             │
┌───────────────────────────▼─────────────────────────────────┐
│  schemas.py                                                   │
│  - Pydantic v2 models: inputs, structured outputs, errors      │
└─────────────────────────────────────────────────────────────┘

Cross-cutting: config.py (settings) and logging_config.py (Loguru) are
imported by every layer above.
```

## Why this separation?

- **`weather_service.py` never imports `fastmcp`.** It is pure business
  logic and can be unit tested (and reused in a completely different
  context, e.g. a REST API or CLI) without any MCP machinery involved.
- **`tools.py` never talks to `httpx` directly.** It only orchestrates:
  validate -> call service -> serialize -> handle errors. This keeps the
  MCP-specific glue code small and easy to audit.
- **`schemas.py` has no behavior**, only data + validation rules, so it can
  be safely imported everywhere without circular-import risk.
- **`config.py` and `logging_config.py`** are intentionally side-effect-light
  (config parsing, logger setup) and imported first by everything else.

## Error handling strategy

OpenWeatherMap failures are mapped to a small, closed set of exception types
in `weather_service.py`:

| Exception              | Meaning                                         | HTTP trigger      |
|-------------------------|--------------------------------------------------|--------------------|
| `CityNotFoundError`     | The city name could not be resolved              | 404                |
| `MissingAPIKeyError`    | No valid API key configured                       | (pre-flight check) |
| `UpstreamAPIError`      | API returned an unexpected error (auth, rate limit) | 401, 429, other 4xx |
| `NetworkError`          | Could not reach the API / 5xx after retries        | timeouts, 5xx      |

Every MCP tool in `tools.py` catches `WeatherServiceError` (the common base
class) and converts it into a structured `ToolError` Pydantic model rather
than letting a raw exception/stack trace leak to the MCP client. This keeps
tool responses **always JSON**, whether they succeed or fail, which is much
easier for downstream LLMs and clients to reason about than free-text error
strings.

## Graceful degradation: weather alerts

The OpenWeatherMap "One Call 3.0" endpoint (which carries official weather
alerts) may require a subscribed plan on some accounts. Rather than making
the whole `get_weather_alerts` tool fail for users on the free tier,
`WeatherService.get_alerts()` catches `UpstreamAPIError` specifically for
this call and returns a valid, structured `WeatherAlertsResponse` with an
empty alert list and an explanatory `note` field. This is a deliberate
design choice: **tools should degrade gracefully, not hard-fail, whenever a
partial/explained result is more useful than an error.**

## Connection pooling & lifecycle

A single `WeatherService` instance (which wraps one `httpx.AsyncClient`) is
constructed once in `server.py` and reused for the lifetime of the process.
`server.py`'s `_run()` coroutine explicitly calls `weather_service.start()`
before `mcp.run_async()` and `weather_service.close()` in a `finally` block,
guaranteeing the HTTP connection pool is cleanly torn down even if the MCP
run loop raises.

## Testing strategy

- **`tests/test_schemas.py`** — pure Pydantic validation tests, no I/O.
- **`tests/test_weather_service.py`** — service-layer tests with all HTTP
  calls intercepted by `respx`, covering both success and each error path.
- **`tests/test_tools.py`** — end-to-end tests that register tools on a real
  `FastMCP` app and invoke them through FastMCP's in-memory `Client`,
  verifying the full tool contract (JSON Schema, structured output,
  structured errors).
- **`tests/test_resources_and_prompts.py`** — verifies all resources and
  prompts are registered and return the expected shape/content.

No test requires network access or a real API key; `respx` mocks the
`httpx.AsyncClient` transport directly.
