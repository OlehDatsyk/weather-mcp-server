# MCP Primer: Tools, Resources, and Prompts

This document is a short, practical primer on the three MCP primitives this
server implements, for readers who are new to the Model Context Protocol.

## What is the Model Context Protocol (MCP)?

MCP is an open, standardized protocol (JSON-RPC 2.0 based) that lets AI
applications ("clients" / "hosts", e.g. Claude Desktop) connect to external
systems ("servers") that expose data and capabilities in a consistent way.
Think of it as **a USB-C port for AI applications**: instead of every AI app
needing a bespoke integration with every tool or data source, both sides
just need to speak MCP.

An MCP server can expose three kinds of capabilities:

### 1. Tools — things the model can *do*

Tools are callable functions with a defined JSON Schema for their inputs
and (in this server) structured JSON outputs. The client's LLM decides
*when* to call a tool based on the tool's name, description, and the
conversation so far. In this server:

| Tool                  | Purpose                                             |
|------------------------|------------------------------------------------------|
| `get_current_weather`  | Current conditions for one city                       |
| `get_weather_forecast` | 1-5 day / 3-hour-step forecast for one city            |
| `compare_cities`       | Side-by-side comparison of 2-10 cities                 |
| `get_air_quality`      | AQI + pollutant concentrations for one city             |
| `get_weather_alerts`   | Active official weather warnings for one city           |

### 2. Resources — things the model can *read*

Resources are addressable, typically read-only pieces of data, identified
by a URI (much like a GET endpoint). Clients can list available resources
and fetch their content on demand or attach them directly to a
conversation's context. In this server:

| Resource URI                  | Content                                             |
|--------------------------------|--------------------------------------------------------|
| `weather://cities/supported`   | Curated list of well-known cities                        |
| `weather://units`              | Supported unit systems and what they measure              |
| `weather://api/info`           | Metadata about the underlying weather API and its limits  |

### 3. Prompts — reusable conversation starters

Prompts are parameterized templates a client can surface to users (e.g. as
slash-commands or quick actions) that produce a ready-made message
instructing the model how to use the server's tools/resources for a common
task. In this server:

| Prompt                     | Purpose                                                |
|------------------------------|-----------------------------------------------------------|
| `weather_summary`            | Friendly plain-language weather briefing for a city         |
| `travel_recommendation`      | Forecast-informed travel planning advice                     |
| `clothing_recommendation`    | What-to-wear advice based on current conditions               |

## Why MCP matters

Before MCP, every AI application that wanted to integrate with, say, a
weather API, a database, or a ticketing system had to write and maintain a
custom integration — and every one of those integrations had to be
re-implemented for every different AI application. This is the classic
"M×N integration problem": M AI applications × N tools/data sources = M×N
bespoke integrations.

MCP turns this into an "M+N" problem: each tool/data source implements
**one** MCP server, and each AI application implements **one** MCP client.
Any MCP client can then talk to any MCP server, immediately.

Concretely, MCP gives you:

- **Standardization** — one protocol instead of bespoke API glue code per
  application.
- **Reusability** — this weather server works unmodified with Claude
  Desktop, the MCP Inspector, or any other MCP-compatible client.
- **Discoverability** — clients can programmatically list a server's tools,
  resources, and prompts (and their schemas) rather than requiring
  hand-written documentation to be read by a human integrator.
- **Structured, typed interactions** — JSON Schema-validated tool inputs and
  (in well-built servers like this one) structured JSON outputs, instead of
  the model having to parse free-text API responses itself.
- **Separation of concerns** — the people who know a data source best (its
  API quirks, rate limits, auth) build the MCP server once; AI application
  developers just consume it.

## How a client uses this server (conceptually)

1. The client launches `python server.py` as a subprocess and communicates
   with it over stdio using JSON-RPC 2.0 messages.
2. During MCP's `initialize` handshake, the client learns the server's name,
   capabilities, and instructions.
3. The client calls `tools/list`, `resources/list`, and `prompts/list` to
   discover what's available (this is exactly what `fastmcp.Client` does in
   this project's own test suite).
4. When a user asks something like *"What's the weather like in Tokyo?"*,
   the client's LLM decides to call the `get_current_weather` tool with
   `{"city": "Tokyo"}`, receives back a structured JSON object, and uses it
   to compose a natural-language answer.
