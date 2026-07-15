"""
tests/test_resources_and_prompts.py
====================================
Tests for the MCP resource and prompt registrations in ``resources.py``
and ``prompts.py``.
"""

from __future__ import annotations

import json

import pytest
from fastmcp import Client, FastMCP

from prompts import register_prompts
from resources import register_resources


@pytest.fixture
def resources_app() -> FastMCP:
    app = FastMCP(name="test-weather-mcp-server-resources")
    register_resources(app)
    return app


@pytest.fixture
def prompts_app() -> FastMCP:
    app = FastMCP(name="test-weather-mcp-server-prompts")
    register_prompts(app)
    return app


class TestResources:
    @pytest.mark.asyncio
    async def test_all_resources_listed(self, resources_app: FastMCP) -> None:
        async with Client(resources_app) as client:
            resources = await client.list_resources()
        uris = {str(r.uri) for r in resources}
        assert uris == {
            "weather://cities/supported",
            "weather://units",
            "weather://api/info",
        }

    @pytest.mark.asyncio
    async def test_supported_cities_content(self, resources_app: FastMCP) -> None:
        async with Client(resources_app) as client:
            result = await client.read_resource("weather://cities/supported")
        payload = json.loads(result[0].text)
        assert payload["count"] > 0
        assert any(c["city"] == "London" for c in payload["cities"])

    @pytest.mark.asyncio
    async def test_weather_units_content(self, resources_app: FastMCP) -> None:
        async with Client(resources_app) as client:
            result = await client.read_resource("weather://units")
        payload = json.loads(result[0].text)
        assert "metric" in payload["unit_systems"]
        assert "imperial" in payload["unit_systems"]
        assert "standard" in payload["unit_systems"]

    @pytest.mark.asyncio
    async def test_api_info_content(self, resources_app: FastMCP) -> None:
        async with Client(resources_app) as client:
            result = await client.read_resource("weather://api/info")
        payload = json.loads(result[0].text)
        assert payload["provider"] == "OpenWeatherMap"
        assert "endpoints_used" in payload


class TestPrompts:
    @pytest.mark.asyncio
    async def test_all_prompts_listed(self, prompts_app: FastMCP) -> None:
        async with Client(prompts_app) as client:
            prompts = await client.list_prompts()
        names = {p.name for p in prompts}
        assert names == {
            "weather_summary",
            "travel_recommendation",
            "clothing_recommendation",
        }

    @pytest.mark.asyncio
    async def test_weather_summary_prompt_renders(self, prompts_app: FastMCP) -> None:
        async with Client(prompts_app) as client:
            result = await client.get_prompt("weather_summary", {"city": "Tokyo"})
        assert len(result.messages) == 1
        assert "Tokyo" in result.messages[0].content.text

    @pytest.mark.asyncio
    async def test_travel_recommendation_prompt_renders(self, prompts_app: FastMCP) -> None:
        async with Client(prompts_app) as client:
            result = await client.get_prompt(
                "travel_recommendation", {"city": "Rome", "days": 4}
            )
        text = result.messages[0].content.text
        assert "Rome" in text
        assert "4-day" in text

    @pytest.mark.asyncio
    async def test_clothing_recommendation_prompt_renders(self, prompts_app: FastMCP) -> None:
        async with Client(prompts_app) as client:
            result = await client.get_prompt(
                "clothing_recommendation", {"city": "Reykjavik"}
            )
        assert "Reykjavik" in result.messages[0].content.text
