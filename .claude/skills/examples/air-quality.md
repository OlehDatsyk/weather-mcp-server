# Example: air quality

> Illustrative values.

**User:** Is the air OK for a run in Delhi this morning?

**Tool call**

```json
get_air_quality({"city": "Delhi,IN"})
```

**Tool result (shortened)**

```json
{"city": "Delhi,IN", "aqi": 5, "aqi_label": "Very Poor",
 "components": {"pm2_5": 182.4, "pm10": 251.0, "o3": 12.1, "no2": 48.3, "co": 1602.2, "so2": 21.0, "no": 3.2, "nh3": 19.8},
 "observed_at": "2026-10-15T05:00:00Z"}
```

**Good answer**

Air quality in Delhi is **Very Poor** right now (AQI 5 of 5). Fine
particles are very high: PM2.5 182 µg/m³ and PM10 251 µg/m³. An indoor
workout is the safer choice this morning. This is current data only - the
server has no air-quality forecast.

Weather data © OpenWeather
