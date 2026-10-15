---
name: weather-mcp-server
description: Answers weather questions with live OpenWeatherMap data through the weather-mcp-server MCP tools - current conditions, 1-5 day forecasts, multi-city comparisons, air quality and official weather alerts. Use when the user asks "what's the weather in...", "will it rain this week in...", "compare the weather in X and Y", "what's the air quality in...", "are there any storm warnings for...", or wants trip-planning or what-to-wear advice based on the weather.
---

# Weather MCP Server Skill

This skill tells you how to use the **weather-mcp-server** MCP server well.
The server is a separate Python program that the user installs and runs
locally. It exposes five tools, three resources and three prompts, all
backed by the OpenWeatherMap API.

**This skill does not contain the server.** If the tools listed below are
not available in your session, follow "Setup check" before doing anything
else. Never invent weather data.

## When to use this skill

Use it when the user wants **current or near-future weather facts** for a
named place:

- Current conditions: temperature, "feels like", humidity, wind, cloud
  cover, visibility, sunrise and sunset.
- A forecast for the next 1-5 days in 3-hour steps.
- A side-by-side comparison of 2-10 cities right now.
- Current air quality (AQI 1-5 and pollutant levels).
- Active official weather alerts (storms, floods, heat, etc.).
- Advice built on the above: what to wear, which day is best for a trip,
  whether to pack an umbrella.

## When NOT to use this skill

Do not use these tools, and say plainly that the server cannot do it, when
the user asks for:

- **Historical weather** or climate averages (e.g. "how hot was July 2019").
  The server only returns current data and a forecast.
- **Forecasts beyond 5 days**, hourly-only (1-hour) forecasts, or minute-by-
  minute rain.
- **Coordinates, postcodes or airport codes** as input. Every tool takes a
  city name only.
- Weather maps, radar images, marine, aviation or pollen data.
- Air-quality forecasts or historical air quality (only current values).
- Anything not about weather.

## Setup check (do this first)

1. Look for tools named `get_current_weather`, `get_weather_forecast`,
   `compare_cities`, `get_air_quality` and `get_weather_alerts`. Some
   clients add a prefix, for example `mcp__weather__get_current_weather`
   in Claude Code. Treat prefixed names as the same tools.
2. If none are available, tell the user the weather-mcp-server is not
   connected and point them to `references/setup.md` in this skill. Do not
   guess the weather instead.
3. If unsure whether an API key is set, read the resource
   `weather://api/info`. If `api_key_configured` is `false`, tell the user
   to set `OPENWEATHER_API_KEY` (see `references/setup.md`) before calling
   any tool.

## Step-by-step workflow

1. **Identify the place.** Use the city name the user gave. If the name is
   ambiguous (Springfield, Paris in Texas, London in Ontario), add an ISO
   country code: `"Springfield,US"`, `"London,GB"`. If you cannot tell which
   one they mean, ask once.
2. **Choose units.** Use the unit system the user asks for or clearly
   implies (°F for a US user -> `imperial`). Otherwise leave the default
   (`metric`). Valid values: `metric`, `imperial`, `standard` (Kelvin).
3. **Pick the right tool** using the table below. Use one call where one
   call is enough.
4. **Check the result for an error** before using it (see "Error handling").
5. **Answer in plain language**, using the output format below.

## Tool selection

| User wants | Tool | Key arguments |
|---|---|---|
| Weather now in one city | `get_current_weather` | `city`, optional `units` |
| Weather over the next days | `get_weather_forecast` | `city`, optional `units`, `days` 1-5 (default 3) |
| Several cities now, side by side | `compare_cities` | `cities` (list of 2-10 names), optional `units` |
| Air quality / pollution | `get_air_quality` | `city` |
| Storm/flood/heat warnings | `get_weather_alerts` | `city` |

Parameter rules:

- `days` outside 1-5 is silently clamped by the server. If the user asks
  for 7 or 10 days, call with `days: 5` and tell them 5 days is the limit.
- `compare_cities` needs at least 2 and at most 10 cities. For one city use
  `get_current_weather`. For more than 10, split into several calls and say
  so.
- `get_air_quality` and `get_weather_alerts` take no `units` argument.
- For "trip" questions, call `get_weather_forecast` **and**
  `get_weather_alerts` for the destination.

Full schemas and every output field: `references/tools.md`.

## Resources and prompts

Resources (read-only, no API call to OpenWeatherMap):

- `weather://cities/supported` - 15 example cities. This is **not** a limit;
  any city OpenWeatherMap can geocode works.
- `weather://units` - what each unit system measures in.
- `weather://api/info` - provider, endpoints used, free-tier notes, and
  whether an API key is configured.

Prompts (the user may start these from their client, e.g. as slash
commands): `weather_summary(city)`, `travel_recommendation(city, days=3)`,
`clothing_recommendation(city)`. If a prompt is used, follow its
instructions; they call the same tools.

## Expected output

- Lead with the direct answer ("It's 14 °C and light rain in London").
- Always state the **units** (°C/°F/K, m/s or mph) and the **city and
  country** returned by the tool, so the user can spot a wrong match.
- Forecast and observation timestamps from the server are in **UTC**. Say
  so, or convert to the city's local time if you are sure of its offset.
- For forecasts, summarise by day (high/low, main conditions, chance of
  rain from `pop_percent`), then highlight the best and worst periods. Do
  not paste all 3-hour entries unless asked.
- For comparisons, give a short table and name the warmest, coldest and
  most humid city from the result fields.
- For air quality, give the `aqi_label` (Good, Fair, Moderate, Poor, Very
  Poor) and mention PM2.5 and PM10 in µg/m³.
- For alerts, list each alert's event, severity, issuing body and time
  window. If the list is empty, repeat the server's `note` accurately - an
  empty list may mean "no alerts" **or** "alerts not available on this API
  plan"; never claim "no warnings" when the note says alerts are
  unavailable.
- End with the attribution line **"Weather data © OpenWeather"**
  (OpenWeather's licence asks for visible attribution).

Examples: see the `examples/` folder.

## Error handling and recovery

On failure a tool returns a JSON object with `"error": true`, an
`error_type` and a `message` instead of weather data. Handle it like this:

| `error_type` | What to do |
|---|---|
| `city_not_found` | Ask the user to check the spelling, or retry once with a country code (`"City,CC"`). |
| `missing_api_key` | Stop. Tell the user to set `OPENWEATHER_API_KEY` for the server and restart their client. |
| `upstream_api_error` | Read the message. HTTP 401: key invalid or not yet active (new keys can take up to a few hours). HTTP 429: rate limit - wait before retrying, do not loop. Other codes: report the message. |
| `network_error` | The server already retried. Tell the user OpenWeatherMap could not be reached; suggest trying again later. |
| `internal_error` / `service_error` | Report the message and suggest restarting the server. |

In `compare_cities`, one city failing does **not** fail the whole call:
that entry has an `error` text and should be reported as "unavailable"
while the other cities are still shown.

Never retry the same failing call more than once. Never fill gaps with
estimated or remembered weather.

## Security and privacy

- **Never ask the user to paste their API key into the chat**, and never
  print, log or repeat a key. The key belongs in the server's `.env` file or
  in the client's MCP config `env` block on the user's own machine.
- The only data sent to OpenWeatherMap is the city name (and coordinates
  derived from it). Do not add other personal details to the `city`
  argument.
- City names are logged by the server in its local `logs/` folder. Mention
  this if the user asks about privacy.
- This skill gives no instructions to run shell commands. The optional
  `scripts/verify_server.py` is for the user to run themselves; it is
  read-only.

## Quick examples

- "What's the weather in Kyiv?" -> `get_current_weather({"city": "Kyiv,UA"})`
- "Will it rain in Edinburgh this weekend?" ->
  `get_weather_forecast({"city": "Edinburgh,GB", "days": 5})`, then report
  only the weekend days.
- "Is it warmer in Lisbon or Madrid?" ->
  `compare_cities({"cities": ["Lisbon,PT", "Madrid,ES"]})`
- "Is the air safe to run in Delhi today?" ->
  `get_air_quality({"city": "Delhi,IN"})` - report the AQI label; do not give
  medical advice beyond the AQI category.
- "Any storm warnings for Miami?" -> `get_weather_alerts({"city": "Miami,US"})`
