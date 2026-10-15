"""
tools.py
========
MCP Tool definitions for the Weather MCP Server.

Each tool is a thin, well-documented wrapper around ``WeatherService`` that:

1. Accepts validated arguments (FastMCP generates JSON Schema from the type
   hints below).
2. Delegates to the service layer for the actual API interaction.
3. Returns structured, JSON-serializable output (Pydantic models, dumped to
   plain dicts) so MCP clients receive predictable, typed responses.
4. Catches and translates known errors into a structured ``ToolError``
   payload instead of letting exceptions propagate as opaque failures.

Tools registered here:
    - get_current_weather
    - get_weather_forecast
    - compare_cities
    - get_air_quality
    - get_weather_alerts
"""

from __future__ import annotations

from typing import Any

from fastmcp import FastMCP

from logging_config import get_logger
from schemas import ToolError, UnitSystem
from weather_service import WeatherService, WeatherServiceError

logger = get_logger(__name__)


def _error_payload(exc: WeatherServiceError) -> dict[str, Any]:
    """Convert a ``WeatherServiceError`` into a structured, JSON-safe dict."""
    logger.error("Tool error [{}]: {}", exc.error_type, exc.message)
    return ToolError(
        error_type=exc.error_type,
        message=exc.message,
    ).model_dump()


def _clean_city(city: str) -> str:
    """Strip a city name and reject empty input before any API call is made."""
    cleaned = city.strip()
    if not cleaned:
        raise WeatherServiceError(
            "City name must not be empty.", error_type="invalid_input"
        )
    return cleaned


def _clean_cities(cities: list[str]) -> list[str]:
    """Strip city names, drop blanks, and enforce the documented 2-10 limit."""
    cleaned = [c.strip() for c in cities if c and c.strip()]
    if not 2 <= len(cleaned) <= 10:
        raise WeatherServiceError(
            f"compare_cities needs 2 to 10 non-empty city names (got {len(cleaned)}).",
            error_type="invalid_input",
        )
    return cleaned


def register_tools(mcp: FastMCP, weather_service: WeatherService) -> None:
    """
    Register all weather-related MCP tools on the given FastMCP instance.

    Parameters
    ----------
    mcp:
        The FastMCP server instance to register tools on.
    weather_service:
        A shared, already-started ``WeatherService`` used by all tools.
    """

    @mcp.tool(
        name="get_current_weather",
        description=(
            "Get the current weather conditions for a city, including temperature, "
            "humidity, wind, cloudiness, and a short description (e.g. 'clear sky'). "
            "Accepts city names like 'London' or 'London,GB' for disambiguation."
        ),
    )
    async def get_current_weather(
        city: str, units: UnitSystem = UnitSystem.METRIC
    ) -> dict[str, Any]:
        """
        Get current weather for a city.

        Args:
            city: City name, optionally 'City,CountryCode' (e.g. 'Paris,FR').
            units: Unit system - 'metric' (Celsius), 'imperial' (Fahrenheit),
                or 'standard' (Kelvin). Defaults to 'metric'.

        Returns:
            A structured current-weather object, or a structured error object
            if the lookup failed.
        """
        logger.info("Tool call: get_current_weather(city={!r}, units={})", city, units)
        try:
            result = await weather_service.get_current_weather(
                city=_clean_city(city), units=units
            )
            return result.model_dump(mode="json")
        except WeatherServiceError as exc:
            return _error_payload(exc)

    @mcp.tool(
        name="get_weather_forecast",
        description=(
            "Get a multi-day weather forecast (3-hour resolution) for a city, "
            "for 1 to 5 days ahead. Useful for trip planning and 'what will the "
            "weather be like this week' style questions."
        ),
    )
    async def get_weather_forecast(
        city: str, units: UnitSystem = UnitSystem.METRIC, days: int = 3
    ) -> dict[str, Any]:
        """
        Get a weather forecast for a city.

        Args:
            city: City name, optionally 'City,CountryCode'.
            units: Unit system - 'metric', 'imperial', or 'standard'.
            days: Number of days to forecast (1-5). Defaults to 3.

        Returns:
            A structured forecast object with a list of time-stepped entries,
            or a structured error object if the lookup failed.
        """
        logger.info(
            "Tool call: get_weather_forecast(city={!r}, units={}, days={})",
            city,
            units,
            days,
        )
        try:
            days_clamped = max(1, min(days, 5))
            result = await weather_service.get_forecast(
                city=_clean_city(city), units=units, days=days_clamped
            )
            return result.model_dump(mode="json")
        except WeatherServiceError as exc:
            return _error_payload(exc)

    @mcp.tool(
        name="compare_cities",
        description=(
            "Compare current weather conditions across 2-10 cities side by side. "
            "Returns per-city data plus the warmest, coldest, and most humid city "
            "in the set. Individual city failures do not fail the whole comparison."
        ),
    )
    async def compare_cities(
        cities: list[str], units: UnitSystem = UnitSystem.METRIC
    ) -> dict[str, Any]:
        """
        Compare current weather across multiple cities.

        Args:
            cities: List of 2-10 city names to compare.
            units: Unit system - 'metric', 'imperial', or 'standard'.

        Returns:
            A structured comparison object summarizing each city's weather.
        """
        logger.info("Tool call: compare_cities(cities={}, units={})", cities, units)
        try:
            result = await weather_service.compare_cities(
                cities=_clean_cities(cities), units=units
            )
            return result.model_dump(mode="json")
        except WeatherServiceError as exc:
            return _error_payload(exc)

    @mcp.tool(
        name="get_air_quality",
        description=(
            "Get current air quality data for a city, including the Air Quality "
            "Index (AQI, 1=Good to 5=Very Poor) and pollutant concentrations "
            "(CO, NO2, O3, SO2, PM2.5, PM10, NH3)."
        ),
    )
    async def get_air_quality(city: str) -> dict[str, Any]:
        """
        Get current air quality for a city.

        Args:
            city: City name, optionally 'City,CountryCode'.

        Returns:
            A structured air-quality object, or a structured error object if
            the lookup failed.
        """
        logger.info("Tool call: get_air_quality(city={!r})", city)
        try:
            result = await weather_service.get_air_quality(city=_clean_city(city))
            return result.model_dump(mode="json")
        except WeatherServiceError as exc:
            return _error_payload(exc)

    @mcp.tool(
        name="get_weather_alerts",
        description=(
            "Get active official weather alerts/warnings (e.g. storm, flood, heat "
            "warnings) for a city, issued by national weather authorities. Returns "
            "an empty list with an explanatory note if no alerts are active or if "
            "alert data is unavailable for the configured API plan."
        ),
    )
    async def get_weather_alerts(city: str) -> dict[str, Any]:
        """
        Get active weather alerts for a city.

        Args:
            city: City name, optionally 'City,CountryCode'.

        Returns:
            A structured alerts object containing zero or more active alerts.
        """
        logger.info("Tool call: get_weather_alerts(city={!r})", city)
        try:
            result = await weather_service.get_alerts(city=_clean_city(city))
            return result.model_dump(mode="json")
        except WeatherServiceError as exc:
            return _error_payload(exc)

    logger.info("Registered 5 MCP tools: current weather, forecast, compare, air quality, alerts")
