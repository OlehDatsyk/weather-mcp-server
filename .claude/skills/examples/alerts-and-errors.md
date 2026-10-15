# Example: alerts not available, and error handling

> Illustrative values.

## Alerts on a plan without One Call access

**User:** Any storm warnings for Miami?

```json
get_weather_alerts({"city": "Miami,US"})
```

```json
{"city": "Miami,US", "alerts": [], "alert_count": 0,
 "note": "Live alert data requires a One Call API 3.0 subscription on OpenWeatherMap. No active alerts could be retrieved for this account/plan."}
```

**Good answer:** I couldn't check official warnings: your OpenWeatherMap
plan doesn't include alert data, so this result does **not** mean there
are no warnings. Please check the US National Weather Service for Miami.
I can still give you the current weather and forecast.

**Bad answer:** "There are no storm warnings for Miami." (This misreads
the `note`.)

## Missing API key

```json
{"error": true, "error_type": "missing_api_key",
 "message": "No OpenWeatherMap API key configured. Set OPENWEATHER_API_KEY in your .env file. See .env.example for details."}
```

**Good answer:** The weather server is running but has no OpenWeatherMap
API key. Add `OPENWEATHER_API_KEY=...` to the `.env` file in your
weather-mcp-server folder, then restart your AI client. Please don't paste
the key here.

## Request beyond the limits

**User:** Give me a 10-day forecast for Rome.

Call `get_weather_forecast({"city": "Rome,IT", "days": 5})` and start the
answer with: "The weather server can forecast up to 5 days ahead, so here
are the next 5 days."
