# Example: current weather

> Numbers in all examples are illustrative, not real observations. They
> show the shape of the tool output and of a good answer.

**User:** What's it like in Edinburgh right now? I'm from the US.

**Tool call**

```json
get_current_weather({"city": "Edinburgh,GB", "units": "imperial"})
```

**Tool result (shortened)**

```json
{
  "city": "Edinburgh", "country": "GB",
  "temperature": 52.3, "feels_like": 49.8, "temp_min": 50.1, "temp_max": 54.0,
  "humidity": 81, "pressure": 1009, "wind_speed": 14.2,
  "cloudiness_percent": 75,
  "conditions": [{"id": 500, "main": "Rain", "description": "light rain", "icon": "10d"}],
  "sunset": "2026-10-15T17:11:00Z", "observed_at": "2026-10-15T11:50:00Z",
  "units": "imperial", "source": "OpenWeatherMap"
}
```

**Good answer**

It's 52 °F in Edinburgh, GB, with light rain - it feels more like 50 °F
because of a fresh 14 mph wind. Humidity is high (81 %) and the sky is
mostly cloudy. Sunset is at 17:11 UTC (18:11 local time). Take a
waterproof jacket.

Weather data © OpenWeather
