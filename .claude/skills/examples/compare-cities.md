# Example: comparing cities (with one failure)

> Illustrative values.

**User:** Compare Kyiv, Warsaw and Atlantisville.

**Tool call**

```json
compare_cities({"cities": ["Kyiv,UA", "Warsaw,PL", "Atlantisville"]})
```

**Tool result (shortened)**

```json
{
  "units": "metric",
  "results": [
    {"city": "Kyiv", "temperature": 11.2, "feels_like": 9.9, "humidity": 70, "wind_speed": 3.1, "conditions_summary": "overcast clouds", "error": null},
    {"city": "Warsaw", "temperature": 9.4, "feels_like": 7.0, "humidity": 82, "wind_speed": 4.6, "conditions_summary": "light rain", "error": null},
    {"city": "Atlantisville", "temperature": null, "feels_like": null, "humidity": 0, "wind_speed": 0.0, "conditions_summary": "unavailable",
     "error": "City 'Atlantisville' could not be found. Check spelling or try 'City,CountryCode' (e.g. 'Springfield,US')."}
  ],
  "warmest_city": "Kyiv", "coldest_city": "Warsaw", "most_humid_city": "Warsaw"
}
```

**Good answer**

| City | Temp | Feels like | Humidity | Wind | Conditions |
|---|---|---|---|---|---|
| Kyiv, UA | 11 °C | 10 °C | 70 % | 3.1 m/s | Overcast |
| Warsaw, PL | 9 °C | 7 °C | 82 % | 4.6 m/s | Light rain |
| Atlantisville | unavailable | - | - | - | City not found |

Kyiv is the warmer of the two; Warsaw is colder and more humid.
I couldn't find "Atlantisville" - can you check the spelling or add a
country code?

Weather data © OpenWeather
