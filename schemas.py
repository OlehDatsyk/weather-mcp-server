"""
schemas.py
==========
Pydantic v2 data models used throughout the Weather MCP Server.

These models serve three purposes:

1. **Input validation** for MCP tool arguments (via FastMCP's automatic
   JSON-Schema generation from type hints / Pydantic models).
2. **Structured output** returned by tools, so MCP clients receive
   predictable, well-typed JSON rather than ad-hoc dictionaries.
3. **Internal DTOs** for translating raw OpenWeatherMap API responses into
   clean, application-specific objects.
"""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field, field_validator


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------
class UnitSystem(str, Enum):
    """Supported unit systems for weather measurements."""

    METRIC = "metric"
    IMPERIAL = "imperial"
    STANDARD = "standard"


class AlertSeverity(str, Enum):
    """Normalized severity levels for weather alerts."""

    MINOR = "minor"
    MODERATE = "moderate"
    SEVERE = "severe"
    EXTREME = "extreme"
    UNKNOWN = "unknown"


# ---------------------------------------------------------------------------
# Shared / common sub-models
# ---------------------------------------------------------------------------
class Coordinates(BaseModel):
    """Geographic coordinates."""

    latitude: float = Field(..., ge=-90, le=90, description="Latitude in decimal degrees.")
    longitude: float = Field(..., ge=-180, le=180, description="Longitude in decimal degrees.")


class WeatherCondition(BaseModel):
    """A single weather condition descriptor (e.g. 'light rain')."""

    id: int = Field(..., description="OpenWeatherMap condition code.")
    main: str = Field(..., description="Group of weather parameters, e.g. 'Rain'.")
    description: str = Field(..., description="Human-readable description of the condition.")
    icon: str = Field(..., description="Icon code usable with OpenWeatherMap's icon CDN.")


# ---------------------------------------------------------------------------
# Tool input models
# ---------------------------------------------------------------------------
class CityQuery(BaseModel):
    """Common input for tools that operate on a single city."""

    city: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="City name, optionally 'City,CountryCode' (e.g. 'London,GB').",
    )
    units: UnitSystem = Field(
        default=UnitSystem.METRIC,
        description="Unit system for temperature and wind speed.",
    )

    @field_validator("city")
    @classmethod
    def _strip_city(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("city must not be empty or whitespace")
        return value


class ForecastQuery(CityQuery):
    """Input for the weather-forecast tool."""

    days: int = Field(
        default=3,
        ge=1,
        le=5,
        description="Number of forecast days to return (1-5, free-tier limit).",
    )


class CompareCitiesQuery(BaseModel):
    """Input for comparing current weather across multiple cities."""

    cities: list[str] = Field(
        ...,
        min_length=2,
        max_length=10,
        description="List of 2-10 city names to compare.",
    )
    units: UnitSystem = Field(default=UnitSystem.METRIC)

    @field_validator("cities")
    @classmethod
    def _clean_cities(cls, value: list[str]) -> list[str]:
        cleaned = [c.strip() for c in value if c and c.strip()]
        if len(cleaned) < 2:
            raise ValueError("at least two non-empty city names are required")
        return cleaned


class AirQualityQuery(BaseModel):
    """Input for the air-quality tool."""

    city: str = Field(..., min_length=1, max_length=100)


class WeatherAlertsQuery(BaseModel):
    """Input for the weather-alerts tool."""

    city: str = Field(..., min_length=1, max_length=100)


# ---------------------------------------------------------------------------
# Structured output models
# ---------------------------------------------------------------------------
class CurrentWeather(BaseModel):
    """Structured, normalized current-weather response."""

    city: str
    country: Optional[str] = None
    coordinates: Coordinates
    temperature: float = Field(..., description="Current temperature in requested units.")
    feels_like: float = Field(..., description="'Feels like' temperature.")
    temp_min: float
    temp_max: float
    humidity: int = Field(..., ge=0, le=100, description="Relative humidity percentage.")
    pressure: int = Field(..., description="Atmospheric pressure at sea level (hPa).")
    wind_speed: float
    wind_direction_degrees: Optional[float] = None
    cloudiness_percent: int = Field(default=0, ge=0, le=100)
    visibility_meters: Optional[int] = None
    conditions: list[WeatherCondition]
    sunrise: Optional[datetime] = None
    sunset: Optional[datetime] = None
    observed_at: datetime
    units: UnitSystem
    source: str = Field(default="OpenWeatherMap")


class ForecastEntry(BaseModel):
    """A single time-step entry within a multi-day forecast."""

    timestamp: datetime
    temperature: float
    feels_like: float
    temp_min: float
    temp_max: float
    humidity: int = Field(..., ge=0, le=100)
    wind_speed: float
    cloudiness_percent: int = Field(default=0, ge=0, le=100)
    pop_percent: float = Field(
        default=0.0, ge=0, le=100, description="Probability of precipitation, as a percentage."
    )
    conditions: list[WeatherCondition]


class WeatherForecast(BaseModel):
    """Structured, normalized multi-day forecast response."""

    city: str
    country: Optional[str] = None
    coordinates: Coordinates
    units: UnitSystem
    requested_days: int
    entries: list[ForecastEntry]
    source: str = Field(default="OpenWeatherMap")


class CityComparisonEntry(BaseModel):
    """One city's data point within a multi-city comparison."""

    city: str
    temperature: float
    feels_like: float
    humidity: int
    wind_speed: float
    conditions_summary: str
    error: Optional[str] = Field(
        default=None, description="Populated if this city's lookup failed."
    )


class CityComparison(BaseModel):
    """Structured output for the compare-cities tool."""

    units: UnitSystem
    results: list[CityComparisonEntry]
    warmest_city: Optional[str] = None
    coldest_city: Optional[str] = None
    most_humid_city: Optional[str] = None
    generated_at: datetime


class AirQualityComponent(BaseModel):
    """Concentrations of individual pollutants, in micrograms per cubic meter."""

    co: float = Field(..., description="Carbon monoxide (CO).")
    no: float = Field(..., description="Nitrogen monoxide (NO).")
    no2: float = Field(..., description="Nitrogen dioxide (NO2).")
    o3: float = Field(..., description="Ozone (O3).")
    so2: float = Field(..., description="Sulphur dioxide (SO2).")
    pm2_5: float = Field(..., description="Fine particulate matter (PM2.5).")
    pm10: float = Field(..., description="Coarse particulate matter (PM10).")
    nh3: float = Field(..., description="Ammonia (NH3).")


class AirQuality(BaseModel):
    """Structured output for the air-quality tool."""

    city: str
    coordinates: Coordinates
    aqi: int = Field(..., ge=1, le=5, description="OpenWeatherMap Air Quality Index (1-5).")
    aqi_label: str = Field(..., description="Human-readable AQI label, e.g. 'Good', 'Poor'.")
    components: AirQualityComponent
    observed_at: datetime
    source: str = Field(default="OpenWeatherMap")


class WeatherAlert(BaseModel):
    """A single official weather alert / warning."""

    sender_name: str
    event: str
    severity: AlertSeverity = AlertSeverity.UNKNOWN
    description: str
    starts_at: datetime
    ends_at: datetime


class WeatherAlertsResponse(BaseModel):
    """Structured output for the weather-alerts tool."""

    city: str
    coordinates: Coordinates
    alerts: list[WeatherAlert]
    alert_count: int
    checked_at: datetime
    note: Optional[str] = Field(
        default=None,
        description="Additional context, e.g. when alert data is unavailable for a region.",
    )


# ---------------------------------------------------------------------------
# Error model
# ---------------------------------------------------------------------------
class ToolError(BaseModel):
    """Uniform, structured error payload returned by tools on failure."""

    error: bool = True
    error_type: str = Field(..., description="Machine-readable error category.")
    message: str = Field(..., description="Human-readable error message.")
    details: Optional[str] = Field(default=None, description="Optional extra diagnostic detail.")
