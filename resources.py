"""
resources.py
============
MCP Resource definitions for the Weather MCP Server.

Resources expose read-only, addressable data via URIs (analogous to GET
endpoints) that MCP clients can list and read without invoking a tool call.
They are ideal for relatively static, reference-style information.

Resources registered here:
    - weather://cities/supported   -> curated list of well-known cities
    - weather://units              -> supported unit systems and their meaning
    - weather://api/info           -> metadata about the underlying weather API
"""

from __future__ import annotations

import json
from typing import Any

from fastmcp import FastMCP

from config import settings
from logging_config import get_logger
from weather_service import POPULAR_CITIES

logger = get_logger(__name__)


def register_resources(mcp: FastMCP) -> None:
    """Register all read-only MCP resources on the given FastMCP instance."""

    @mcp.resource(
        uri="weather://cities/supported",
        name="Supported Cities",
        description=(
            "A curated list of popular, well-known cities that are guaranteed to "
            "resolve correctly against the weather API. Note: the API actually "
            "supports virtually any geocodable city worldwide - this list is a "
            "convenient, fast-loading starting point, not an exhaustive limit."
        ),
        mime_type="application/json",
    )
    def supported_cities() -> str:
        """Return the curated list of popular cities as a JSON string."""
        payload: dict[str, Any] = {
            "description": (
                "Curated list of popular cities. Any geocodable city name is "
                "supported by the underlying API; this list simply highlights "
                "commonly requested locations."
            ),
            "count": len(POPULAR_CITIES),
            "cities": POPULAR_CITIES,
        }
        return json.dumps(payload, indent=2)

    @mcp.resource(
        uri="weather://units",
        name="Weather Units",
        description=(
            "Describes the unit systems supported by this server's tools: "
            "metric, imperial, and standard, including what each measures "
            "temperature, wind speed, and pressure in."
        ),
        mime_type="application/json",
    )
    def weather_units() -> str:
        """Return supported unit systems and their measurement details as JSON."""
        payload: dict[str, Any] = {
            "default_unit_system": settings.default_units,
            "unit_systems": {
                "metric": {
                    "temperature": "Celsius (°C)",
                    "wind_speed": "meters per second (m/s)",
                    "pressure": "hectopascals (hPa)",
                },
                "imperial": {
                    "temperature": "Fahrenheit (°F)",
                    "wind_speed": "miles per hour (mph)",
                    "pressure": "hectopascals (hPa)",
                },
                "standard": {
                    "temperature": "Kelvin (K)",
                    "wind_speed": "meters per second (m/s)",
                    "pressure": "hectopascals (hPa)",
                },
            },
        }
        return json.dumps(payload, indent=2)

    @mcp.resource(
        uri="weather://api/info",
        name="API Information",
        description=(
            "Metadata about the underlying weather data provider, including "
            "which endpoints are used, rate-limit considerations, and whether "
            "an API key is currently configured on this server."
        ),
        mime_type="application/json",
    )
    def api_info() -> str:
        """Return metadata about the configured weather data provider as JSON."""
        payload: dict[str, Any] = {
            "provider": "OpenWeatherMap",
            "base_url": settings.openweather_base_url,
            "api_key_configured": settings.has_api_key,
            "endpoints_used": {
                "current_weather": "/data/2.5/weather",
                "forecast": "/data/2.5/forecast",
                "geocoding": "/geo/1.0/direct",
                "air_pollution": "/data/2.5/air_pollution",
                "alerts": "/data/3.0/onecall (alerts field)",
            },
            "free_tier_notes": [
                "The free tier allows 60 calls/minute and 1,000,000 calls/month.",
                "The /forecast endpoint returns 3-hour steps for up to 5 days.",
                "Weather alerts via One Call API 3.0 may require a subscribed "
                "plan; this server degrades gracefully if alerts are unavailable.",
            ],
            "documentation_url": "https://openweathermap.org/api",
        }
        return json.dumps(payload, indent=2)

    logger.info("Registered 3 MCP resources: supported cities, units, api info")
