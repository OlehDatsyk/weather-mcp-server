# Tool, resource and prompt reference

This reference describes the capabilities of **weather-mcp-server** exactly
as implemented in its source code (`tools.py`, `resources.py`, `prompts.py`,
`schemas.py`, `weather_service.py`). Input schemas below were read from the
running server.

Data source: OpenWeatherMap. All timestamps are ISO 8601 in **UTC**.

---

## Tools

### `get_current_weather`

Input:

```json
{
  "city":  "string (required) - 'City' or 'City,CountryCode', e.g. 'Paris,FR'",
  "units": "metric | imperial | standard (optional, default metric)"
}
```

Output fields (`CurrentWeather`):

| Field | Meaning |
|---|---|
| `city`, `country` | Place the API matched (check this against what the user meant) |
| `coordinates.latitude`, `coordinates.longitude` | Decimal degrees |
| `temperature`, `feels_like`, `temp_min`, `temp_max` | In the requested units |
| `humidity` | Relative humidity, % |
| `pressure` | Sea-level pressure, hPa |
| `wind_speed` | m/s (metric, standard) or mph (imperial) |
| `wind_direction_degrees` | 0-360, may be null |
| `cloudiness_percent` | 0-100 |
| `visibility_meters` | May be null |
| `conditions[]` | `id`, `main` (e.g. "Rain"), `description` (e.g. "light rain"), `icon` |
| `sunrise`, `sunset`, `observed_at` | UTC timestamps |
| `units`, `source` | Echo of units; always "OpenWeatherMap" |

API calls used: `/data/2.5/weather` (1 call).

### `get_weather_forecast`

Input:

```json
{
  "city":  "string (required)",
  "units": "metric | imperial | standard (optional, default metric)",
  "days":  "integer (optional, default 3) - clamped to 1..5"
}
```

Output (`WeatherForecast`): `city`, `country`, `coordinates`, `units`,
`requested_days`, `source`, and `entries[]`. Each entry is one **3-hour**
step:

| Field | Meaning |
|---|---|
| `timestamp` | UTC start of the 3-hour step |
| `temperature`, `feels_like`, `temp_min`, `temp_max` | Requested units |
| `humidity` | % |
| `wind_speed` | m/s or mph |
| `cloudiness_percent` | 0-100 |
| `pop_percent` | Probability of precipitation, 0-100 % |
| `conditions[]` | As above |

Notes:

- The server returns `days x 8` entries counted **from now**, so "1 day"
  means the next 24 hours, not "today" by the calendar. Group entries by
  local date yourself when you summarise by day.
- Maximum 5 days (40 entries). This is a limit of the free OpenWeatherMap
  forecast endpoint used.

API calls used: `/data/2.5/forecast` (1 call).

### `compare_cities`

Input:

```json
{
  "cities": ["string", "..."],
  "units":  "metric | imperial | standard (optional, default metric)"
}
```

Send 2-10 cities. The server calls the current-weather endpoint once per
city, one after another, so 10 cities = 10 API calls.

Output (`CityComparison`):

| Field | Meaning |
|---|---|
| `results[]` | One entry per city: `city`, `temperature`, `feels_like`, `humidity`, `wind_speed`, `conditions_summary`, `error` |
| `warmest_city`, `coldest_city`, `most_humid_city` | Calculated from successful entries only; null if none succeeded |
| `units`, `generated_at` | Units and UTC time of the comparison |

If one city fails, its entry has `error` set (a message), `conditions_summary`
= "unavailable", `temperature`/`feels_like` empty (NaN on the server, received as `null`
over MCP) and
`humidity`/`wind_speed` set to 0. Ignore all its numbers. Other cities are still
valid.

### `get_air_quality`

Input: `{"city": "string (required)"}` - no units.

Output (`AirQuality`):

| Field | Meaning |
|---|---|
| `city`, `coordinates` | Place used |
| `aqi` | OpenWeatherMap index 1-5 |
| `aqi_label` | 1 Good, 2 Fair, 3 Moderate, 4 Poor, 5 Very Poor |
| `components` | `co`, `no`, `no2`, `o3`, `so2`, `pm2_5`, `pm10`, `nh3` in µg/m³ |
| `observed_at`, `source` | UTC time; "OpenWeatherMap" |

API calls used: `/geo/1.0/direct` + `/data/2.5/air_pollution` (2 calls).
Current values only - no air-quality forecast.

### `get_weather_alerts`

Input: `{"city": "string (required)"}` - no units.

Output (`WeatherAlertsResponse`):

| Field | Meaning |
|---|---|
| `city`, `coordinates` | Place used |
| `alerts[]` | `sender_name`, `event`, `severity` (minor, moderate, severe, extreme, unknown), `description`, `starts_at`, `ends_at` |
| `alert_count` | Number of alerts |
| `checked_at` | UTC time |
| `note` | Explanation when the list is empty |

API calls used: `/geo/1.0/direct` + `/data/3.0/onecall` (2 calls).

**Important:** `/data/3.0/onecall` needs a separate One Call subscription on
many OpenWeatherMap accounts. If that endpoint refuses the request, the
tool does **not** fail. It returns `alerts: []` with a `note` saying live
alert data needs a One Call subscription. Read the `note` before telling the
user there are no warnings.

---

## Error object (all tools)

```json
{
  "error": true,
  "error_type": "city_not_found | missing_api_key | upstream_api_error | network_error | internal_error | service_error",
  "message": "Human-readable explanation",
  "details": null
}
```

Behaviour behind each type (from `weather_service.py`):

- `city_not_found` - HTTP 404 from the API, or geocoding returned nothing.
  Not retried.
- `missing_api_key` - `OPENWEATHER_API_KEY` empty or still the placeholder
  `your_api_key_here`. No request is sent.
- `upstream_api_error` - HTTP 401 (bad or inactive key), 429 (rate limit),
  or another 4xx. Not retried.
- `network_error` - timeouts, connection failures or HTTP 5xx, after
  `MAX_RETRIES` retries (default 3).

---

## Resources

| URI | Content (JSON) |
|---|---|
| `weather://cities/supported` | `count` and 15 example `cities` (London GB, New York US, Tokyo JP, Paris FR, Sydney AU, Cairo EG, Mumbai IN, Sao Paulo BR, Toronto CA, Berlin DE, Dubai AE, Singapore SG, Cape Town ZA, Moscow RU, Mexico City MX). Examples only, not a limit. |
| `weather://units` | `default_unit_system` and what metric / imperial / standard use for temperature, wind speed and pressure |
| `weather://api/info` | `provider`, `base_url`, `api_key_configured` (true/false - never the key itself), `endpoints_used`, `free_tier_notes`, `documentation_url` |

## Prompts

| Name | Arguments | What it asks the model to do |
|---|---|---|
| `weather_summary` | `city` (required) | Call `get_current_weather`, write a friendly 3-5 sentence briefing |
| `travel_recommendation` | `city` (required), `days` (optional, default 3) | Call `get_weather_forecast` and `get_weather_alerts`, give travel advice with headings |
| `clothing_recommendation` | `city` (required) | Call `get_current_weather`, give a numbered list of clothes and one line of advice |
