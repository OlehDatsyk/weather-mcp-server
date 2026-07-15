"""
tests/conftest.py
==================
Shared pytest fixtures for the Weather MCP Server test suite.
"""

from __future__ import annotations

from typing import AsyncIterator

import pytest
import pytest_asyncio

from weather_service import WeatherService

TEST_API_KEY = "test_api_key_12345"
TEST_BASE_URL = "https://api.openweathermap.org"


@pytest_asyncio.fixture
async def weather_service() -> AsyncIterator[WeatherService]:
    """Provide a started ``WeatherService`` instance backed by a fake API key."""
    service = WeatherService(
        api_key=TEST_API_KEY,
        base_url=TEST_BASE_URL,
        timeout=5.0,
        max_retries=1,
    )
    await service.start()
    try:
        yield service
    finally:
        await service.close()


@pytest.fixture
def sample_current_weather_json() -> dict:
    """A representative raw JSON payload from /data/2.5/weather."""
    return {
        "coord": {"lon": -0.1257, "lat": 51.5085},
        "weather": [
            {"id": 800, "main": "Clear", "description": "clear sky", "icon": "01d"}
        ],
        "base": "stations",
        "main": {
            "temp": 18.5,
            "feels_like": 18.0,
            "temp_min": 16.0,
            "temp_max": 20.0,
            "pressure": 1015,
            "humidity": 60,
        },
        "visibility": 10000,
        "wind": {"speed": 3.6, "deg": 250},
        "clouds": {"all": 0},
        "dt": 1710000000,
        "sys": {
            "type": 2,
            "id": 2019646,
            "country": "GB",
            "sunrise": 1709960000,
            "sunset": 1710000000,
        },
        "timezone": 0,
        "id": 2643743,
        "name": "London",
        "cod": 200,
    }


@pytest.fixture
def sample_forecast_json() -> dict:
    """A representative raw JSON payload from /data/2.5/forecast (trimmed)."""
    entry_template = {
        "main": {
            "temp": 15.0,
            "feels_like": 14.5,
            "temp_min": 13.0,
            "temp_max": 16.0,
            "humidity": 55,
        },
        "weather": [
            {"id": 500, "main": "Rain", "description": "light rain", "icon": "10d"}
        ],
        "clouds": {"all": 40},
        "wind": {"speed": 2.1, "deg": 180},
        "pop": 0.32,
        "dt_txt": "2026-07-15 12:00:00",
    }
    entries = []
    for i in range(16):  # 2 days worth of 3-hour steps
        entry = dict(entry_template)
        entry["dt"] = 1710000000 + i * 10800
        entries.append(entry)

    return {
        "cod": "200",
        "message": 0,
        "cnt": len(entries),
        "list": entries,
        "city": {
            "id": 2643743,
            "name": "London",
            "coord": {"lat": 51.5085, "lon": -0.1257},
            "country": "GB",
            "timezone": 0,
        },
    }


@pytest.fixture
def sample_geocode_json() -> list:
    """A representative raw JSON payload from /geo/1.0/direct."""
    return [
        {
            "name": "London",
            "lat": 51.5085,
            "lon": -0.1257,
            "country": "GB",
            "state": "England",
        }
    ]


@pytest.fixture
def sample_air_pollution_json() -> dict:
    """A representative raw JSON payload from /data/2.5/air_pollution."""
    return {
        "coord": {"lon": -0.1257, "lat": 51.5085},
        "list": [
            {
                "main": {"aqi": 2},
                "components": {
                    "co": 230.31,
                    "no": 0.32,
                    "no2": 15.6,
                    "o3": 68.4,
                    "so2": 3.2,
                    "pm2_5": 8.4,
                    "pm10": 12.1,
                    "nh3": 1.1,
                },
                "dt": 1710000000,
            }
        ],
    }
