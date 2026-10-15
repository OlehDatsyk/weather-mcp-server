"""
tests/test_tools.py
====================
Tests for the MCP tool wrappers in ``tools.py``.

These tests register the tools on a real ``FastMCP`` instance and invoke
them through FastMCP's in-memory client, verifying both the "happy path"
and structured-error behavior end-to-end (service layer -> tool wrapper ->
JSON-serializable output), with all HTTP calls mocked via ``respx``.
"""

from __future__ import annotations

import httpx
import pytest
import respx
from fastmcp import Client, FastMCP

from tools import register_tools
from weather_service import WeatherService

BASE_URL = "https://api.openweathermap.org"


@pytest.fixture
def mcp_app() -> tuple[FastMCP, WeatherService]:
    """Build a fresh FastMCP app with tools registered against a test service."""
    app = FastMCP(name="test-weather-mcp-server")
    service = WeatherService(api_key="test_key", base_url=BASE_URL, max_retries=0)
    register_tools(app, service)
    return app, service


class TestGetCurrentWeatherTool:
    @pytest.mark.asyncio
    @respx.mock
    async def test_success(
        self, mcp_app: tuple[FastMCP, WeatherService], sample_current_weather_json: dict
    ) -> None:
        app, service = mcp_app
        respx.get(f"{BASE_URL}/data/2.5/weather").mock(
            return_value=httpx.Response(200, json=sample_current_weather_json)
        )

        await service.start()
        try:
            async with Client(app) as client:
                result = await client.call_tool(
                    "get_current_weather", {"city": "London", "units": "metric"}
                )
            data = result.data
            assert data["city"] == "London"
            assert data["temperature"] == 18.5
        finally:
            await service.close()

    @pytest.mark.asyncio
    @respx.mock
    async def test_city_not_found_returns_structured_error(
        self, mcp_app: tuple[FastMCP, WeatherService]
    ) -> None:
        app, service = mcp_app
        respx.get(f"{BASE_URL}/data/2.5/weather").mock(
            return_value=httpx.Response(404, json={"cod": "404", "message": "not found"})
        )

        await service.start()
        try:
            async with Client(app) as client:
                result = await client.call_tool(
                    "get_current_weather", {"city": "Nowhereville"}
                )
            data = result.data
            assert data["error"] is True
            assert data["error_type"] == "city_not_found"
        finally:
            await service.close()


class TestCompareCitiesTool:
    @pytest.mark.asyncio
    @respx.mock
    async def test_success(
        self, mcp_app: tuple[FastMCP, WeatherService], sample_current_weather_json: dict
    ) -> None:
        app, service = mcp_app
        respx.get(f"{BASE_URL}/data/2.5/weather").mock(
            return_value=httpx.Response(200, json=sample_current_weather_json)
        )

        await service.start()
        try:
            async with Client(app) as client:
                result = await client.call_tool(
                    "compare_cities", {"cities": ["London", "Paris"], "units": "metric"}
                )
            data = result.data
            assert len(data["results"]) == 2
            assert data["warmest_city"] is not None
        finally:
            await service.close()


class TestInputValidation:
    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        ("tool", "args"),
        [
            ("get_current_weather", {"city": "   "}),
            ("get_weather_forecast", {"city": ""}),
            ("get_air_quality", {"city": ""}),
            ("get_weather_alerts", {"city": " "}),
            ("compare_cities", {"cities": ["London"]}),
            ("compare_cities", {"cities": ["London", " "]}),
            ("compare_cities", {"cities": [f"City{i}" for i in range(11)]}),
        ],
    )
    async def test_invalid_input_returns_structured_error_without_api_call(
        self, mcp_app: tuple[FastMCP, WeatherService], tool: str, args: dict
    ) -> None:
        app, service = mcp_app

        await service.start()
        try:
            with respx.mock(assert_all_called=False) as router:
                route = router.get(url__startswith=BASE_URL).mock(
                    return_value=httpx.Response(200, json={})
                )
                async with Client(app) as client:
                    result = await client.call_tool(tool, args)
            data = result.data
            assert data["error"] is True
            assert data["error_type"] == "invalid_input"
            assert not route.called
        finally:
            await service.close()


class TestGetAirQualityTool:
    @pytest.mark.asyncio
    @respx.mock
    async def test_success(
        self,
        mcp_app: tuple[FastMCP, WeatherService],
        sample_geocode_json: list,
        sample_air_pollution_json: dict,
    ) -> None:
        app, service = mcp_app
        respx.get(f"{BASE_URL}/geo/1.0/direct").mock(
            return_value=httpx.Response(200, json=sample_geocode_json)
        )
        respx.get(f"{BASE_URL}/data/2.5/air_pollution").mock(
            return_value=httpx.Response(200, json=sample_air_pollution_json)
        )

        await service.start()
        try:
            async with Client(app) as client:
                result = await client.call_tool("get_air_quality", {"city": "London"})
            data = result.data
            assert data["aqi"] == 2
            assert data["aqi_label"] == "Fair"
        finally:
            await service.close()


class TestToolRegistration:
    @pytest.mark.asyncio
    async def test_all_five_tools_registered(
        self, mcp_app: tuple[FastMCP, WeatherService]
    ) -> None:
        app, _service = mcp_app
        async with Client(app) as client:
            tools = await client.list_tools()
        tool_names = {t.name for t in tools}
        assert tool_names == {
            "get_current_weather",
            "get_weather_forecast",
            "compare_cities",
            "get_air_quality",
            "get_weather_alerts",
        }
