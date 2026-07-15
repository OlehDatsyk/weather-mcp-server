"""
tests/test_weather_service.py
==============================
Unit tests for ``weather_service.py``.

All outbound HTTP calls are intercepted with ``respx`` so these tests run
fully offline and deterministically, without requiring a real
OpenWeatherMap API key.
"""

from __future__ import annotations

import httpx
import pytest
import respx

from schemas import UnitSystem
from weather_service import (
    CityNotFoundError,
    MissingAPIKeyError,
    UpstreamAPIError,
    WeatherService,
)

BASE_URL = "https://api.openweathermap.org"


# ---------------------------------------------------------------------------
# get_current_weather
# ---------------------------------------------------------------------------
class TestGetCurrentWeather:
    @pytest.mark.asyncio
    @respx.mock
    async def test_returns_parsed_weather(
        self, weather_service: WeatherService, sample_current_weather_json: dict
    ) -> None:
        respx.get(f"{BASE_URL}/data/2.5/weather").mock(
            return_value=httpx.Response(200, json=sample_current_weather_json)
        )

        result = await weather_service.get_current_weather("London", UnitSystem.METRIC)

        assert result.city == "London"
        assert result.country == "GB"
        assert result.temperature == 18.5
        assert result.humidity == 60
        assert result.units == UnitSystem.METRIC
        assert result.conditions[0].description == "clear sky"

    @pytest.mark.asyncio
    @respx.mock
    async def test_city_not_found_raises(self, weather_service: WeatherService) -> None:
        respx.get(f"{BASE_URL}/data/2.5/weather").mock(
            return_value=httpx.Response(404, json={"cod": "404", "message": "city not found"})
        )

        with pytest.raises(CityNotFoundError):
            await weather_service.get_current_weather("Nowhereville", UnitSystem.METRIC)

    @pytest.mark.asyncio
    @respx.mock
    async def test_unauthorized_raises_upstream_error(
        self, weather_service: WeatherService
    ) -> None:
        respx.get(f"{BASE_URL}/data/2.5/weather").mock(
            return_value=httpx.Response(401, json={"cod": 401, "message": "Invalid API key"})
        )

        with pytest.raises(UpstreamAPIError) as exc_info:
            await weather_service.get_current_weather("London", UnitSystem.METRIC)
        assert exc_info.value.status_code == 401

    @pytest.mark.asyncio
    async def test_missing_api_key_raises(self) -> None:
        service = WeatherService(api_key="", base_url=BASE_URL)
        await service.start()
        try:
            with pytest.raises(MissingAPIKeyError):
                await service.get_current_weather("London")
        finally:
            await service.close()


# ---------------------------------------------------------------------------
# get_forecast
# ---------------------------------------------------------------------------
class TestGetForecast:
    @pytest.mark.asyncio
    @respx.mock
    async def test_returns_parsed_forecast(
        self, weather_service: WeatherService, sample_forecast_json: dict
    ) -> None:
        respx.get(f"{BASE_URL}/data/2.5/forecast").mock(
            return_value=httpx.Response(200, json=sample_forecast_json)
        )

        result = await weather_service.get_forecast("London", UnitSystem.METRIC, days=2)

        assert result.city == "London"
        assert result.requested_days == 2
        # 2 days * 8 entries/day = 16 entries expected (matches fixture size).
        assert len(result.entries) == 16
        assert result.entries[0].temperature == 15.0

    @pytest.mark.asyncio
    @respx.mock
    async def test_trims_to_requested_days(
        self, weather_service: WeatherService, sample_forecast_json: dict
    ) -> None:
        respx.get(f"{BASE_URL}/data/2.5/forecast").mock(
            return_value=httpx.Response(200, json=sample_forecast_json)
        )

        result = await weather_service.get_forecast("London", UnitSystem.METRIC, days=1)

        assert len(result.entries) == 8


# ---------------------------------------------------------------------------
# compare_cities
# ---------------------------------------------------------------------------
class TestCompareCities:
    @pytest.mark.asyncio
    @respx.mock
    async def test_compares_multiple_cities(
        self, weather_service: WeatherService, sample_current_weather_json: dict
    ) -> None:
        respx.get(f"{BASE_URL}/data/2.5/weather").mock(
            return_value=httpx.Response(200, json=sample_current_weather_json)
        )

        result = await weather_service.compare_cities(
            ["London", "Paris"], UnitSystem.METRIC
        )

        assert len(result.results) == 2
        assert result.warmest_city is not None
        assert result.coldest_city is not None

    @pytest.mark.asyncio
    @respx.mock
    async def test_partial_failure_does_not_raise(
        self, weather_service: WeatherService, sample_current_weather_json: dict
    ) -> None:
        route = respx.get(f"{BASE_URL}/data/2.5/weather")
        route.side_effect = [
            httpx.Response(200, json=sample_current_weather_json),
            httpx.Response(404, json={"cod": "404", "message": "not found"}),
        ]

        result = await weather_service.compare_cities(
            ["London", "Nowhereville"], UnitSystem.METRIC
        )

        assert len(result.results) == 2
        successes = [r for r in result.results if r.error is None]
        failures = [r for r in result.results if r.error is not None]
        assert len(successes) == 1
        assert len(failures) == 1


# ---------------------------------------------------------------------------
# get_air_quality
# ---------------------------------------------------------------------------
class TestGetAirQuality:
    @pytest.mark.asyncio
    @respx.mock
    async def test_returns_parsed_air_quality(
        self,
        weather_service: WeatherService,
        sample_geocode_json: list,
        sample_air_pollution_json: dict,
    ) -> None:
        respx.get(f"{BASE_URL}/geo/1.0/direct").mock(
            return_value=httpx.Response(200, json=sample_geocode_json)
        )
        respx.get(f"{BASE_URL}/data/2.5/air_pollution").mock(
            return_value=httpx.Response(200, json=sample_air_pollution_json)
        )

        result = await weather_service.get_air_quality("London")

        assert result.city == "London"
        assert result.aqi == 2
        assert result.aqi_label == "Fair"
        assert result.components.pm2_5 == 8.4

    @pytest.mark.asyncio
    @respx.mock
    async def test_city_not_found_during_geocode(
        self, weather_service: WeatherService
    ) -> None:
        respx.get(f"{BASE_URL}/geo/1.0/direct").mock(
            return_value=httpx.Response(200, json=[])
        )

        with pytest.raises(CityNotFoundError):
            await weather_service.get_air_quality("Nowhereville")


# ---------------------------------------------------------------------------
# get_alerts
# ---------------------------------------------------------------------------
class TestGetAlerts:
    @pytest.mark.asyncio
    @respx.mock
    async def test_degrades_gracefully_when_onecall_unavailable(
        self, weather_service: WeatherService, sample_geocode_json: list
    ) -> None:
        respx.get(f"{BASE_URL}/geo/1.0/direct").mock(
            return_value=httpx.Response(200, json=sample_geocode_json)
        )
        respx.get(f"{BASE_URL}/data/3.0/onecall").mock(
            return_value=httpx.Response(401, json={"cod": 401, "message": "unauthorized"})
        )

        result = await weather_service.get_alerts("London")

        assert result.alert_count == 0
        assert result.note is not None
        assert "One Call API" in result.note

    @pytest.mark.asyncio
    @respx.mock
    async def test_returns_active_alerts(
        self, weather_service: WeatherService, sample_geocode_json: list
    ) -> None:
        respx.get(f"{BASE_URL}/geo/1.0/direct").mock(
            return_value=httpx.Response(200, json=sample_geocode_json)
        )
        respx.get(f"{BASE_URL}/data/3.0/onecall").mock(
            return_value=httpx.Response(
                200,
                json={
                    "lat": 51.5085,
                    "lon": -0.1257,
                    "alerts": [
                        {
                            "sender_name": "UK Met Office",
                            "event": "Flood Warning",
                            "start": 1710000000,
                            "end": 1710086400,
                            "description": "Heavy rainfall expected.",
                            "tags": ["Flood", "Moderate"],
                        }
                    ],
                },
            )
        )

        result = await weather_service.get_alerts("London")

        assert result.alert_count == 1
        assert result.alerts[0].event == "Flood Warning"
