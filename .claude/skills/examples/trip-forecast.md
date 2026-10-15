# Example: trip planning with forecast + alerts

> Illustrative values.

**User:** I'm in Lisbon from tomorrow for 4 days. Which day is best for the
beach?

**Tool calls** (the skill asks for both on trip questions)

```json
get_weather_forecast({"city": "Lisbon,PT", "days": 5})
get_weather_alerts({"city": "Lisbon,PT"})
```

`days` is 5 because the server counts days from *now*; 4 days starting
tomorrow need the full 5-day window.

**Alerts result (shortened)**

```json
{"city": "Lisbon,PT", "alerts": [], "alert_count": 0,
 "note": "No active weather alerts for this location."}
```

**Good answer** (after grouping the 3-hour entries by local date)

| Day | High / low | Conditions | Chance of rain |
|---|---|---|---|
| Fri | 23 / 16 °C | Sunny | 0-5 % |
| Sat | 24 / 17 °C | Clear, light wind | 0 % |
| Sun | 20 / 15 °C | Showers in the afternoon | up to 70 % |
| Mon | 21 / 15 °C | Partly cloudy | 10 % |

**Saturday** is the best beach day: warmest, dry and calm. Plan
something indoors for Sunday afternoon. There are no active weather
alerts for Lisbon. Times are converted from UTC to Lisbon time.

Weather data © OpenWeather
