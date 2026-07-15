"""
weather_service.py
===================
Async service layer that wraps the OpenWeatherMap REST API.

This module is the *only* place in the codebase that knows about
OpenWeatherMap's URL structure and raw JSON shape. Tools (in ``tools.py``)
call into this service and receive clean, validated Pydantic models defined
in ``schemas.py``. This separation keeps MCP-specific concerns (tool
registration, JSON-RPC) decoupled from HTTP/API concerns, and makes the
service layer independently unit-testable.
"""

from __future__ import annotations

from collections import defaultdict
from datetime import datetime, timezone
from typing import Any, Optional

import httpx

from config import settings
from logging_config import get_logger
from schemas import (
    AirQuality,
    AirQualityComponent,
    AlertSeverity,
    CityComparison,
    CityComparisonEntry,
    Coordinates,
    CurrentWeather,
    ForecastEntry,
    UnitSystem,
    WeatherAlert,
    WeatherAlertsResponse,
    WeatherCondition,
    WeatherForecast,
)

logger = get_logger(__name__)


# ---------------------------------------------------------------------------
# Exceptions
# ---------------------------------------------------------------------------
class WeatherServiceError(Exception):
    """Base exception for all weather-service failures."""

    def __init__(self, message: str, error_type: str = "service_error") -> None:
        super().__init__(message)
        self.message = message
        self.error_type = error_type


class CityNotFoundError(WeatherServiceError):
    """Raised when the upstream API cannot resolve a given city name."""

    def __init__(self, city: str) -> None:
        super().__init__(
            message=f"City '{city}' could not be found. Check spelling or try "
            f"'City,CountryCode' (e.g. 'Springfield,US').",
            error_type="city_not_found",
        )


class MissingAPIKeyError(WeatherServiceError):
    """Raised when no valid OpenWeatherMap API key is configured."""

    def __init__(self) -> None:
        super().__init__(
            message="No OpenWeatherMap API key configured. Set OPENWEATHER_API_KEY "
            "in your .env file. See .env.example for details.",
            error_type="missing_api_key",
        )


class UpstreamAPIError(WeatherServiceError):
    """Raised when the OpenWeatherMap API returns an unexpected error."""

    def __init__(self, status_code: int, detail: str) -> None:
        super().__init__(
            message=f"OpenWeatherMap API error (HTTP {status_code}): {detail}",
            error_type="upstream_api_error",
        )
        self.status_code = status_code


class NetworkError(WeatherServiceError):
    """Raised when the request could not reach the OpenWeatherMap API at all."""

    def __init__(self, detail: str) -> None:
        super().__init__(
            message=f"Network error while contacting OpenWeatherMap: {detail}",
            error_type="network_error",
        )


# ---------------------------------------------------------------------------
# AQI numeric -> label mapping (OpenWeatherMap's 1-5 scale)
# ---------------------------------------------------------------------------
_AQI_LABELS: dict[int, str] = {
    1: "Good",
    2: "Fair",
    3: "Moderate",
    4: "Poor",
    5: "Very Poor",
}

# A short list of well-known cities exposed via the "supported cities" resource.
# OpenWeatherMap technically supports any geocodable city; this curated list
# gives MCP clients a helpful, fast-loading starting point.
POPULAR_CITIES: list[dict[str, str]] = [
    {"city": "London", "country": "GB"},
    {"city": "New York", "country": "US"},
    {"city": "Tokyo", "country": "JP"},
    {"city": "Paris", "country": "FR"},
    {"city": "Sydney", "country": "AU"},
    {"city": "Cairo", "country": "EG"},
    {"city": "Mumbai", "country": "IN"},
    {"city": "Sao Paulo", "country": "BR"},
    {"city": "Toronto", "country": "CA"},
    {"city": "Berlin", "country": "DE"},
    {"city": "Dubai", "country": "AE"},
    {"city": "Singapore", "country": "SG"},
    {"city": "Cape Town", "country": "ZA"},
    {"city": "Moscow", "country": "RU"},
    {"city": "Mexico City", "country": "MX"},
]


class WeatherService:
    """
    Async client for the OpenWeatherMap API.

    A single instance is intended to be reused for the lifetime of the MCP
    server process (see ``server.py``), which allows HTTP connection pooling
    via a shared ``httpx.AsyncClient``.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        timeout: Optional[float] = None,
        max_retries: Optional[int] = None,
    ) -> None:
        self._api_key = api_key if api_key is not None else settings.openweather_api_key
        self._base_url = (base_url or settings.openweather_base_url).rstrip("/")
        self._timeout = timeout if timeout is not None else settings.request_timeout_seconds
        self._max_retries = max_retries if max_retries is not None else settings.max_retries
        self._client: Optional[httpx.AsyncClient] = None

    # -- lifecycle ---------------------------------------------------------
    async def __aenter__(self) -> "WeatherService":
        await self.start()
        return self

    async def __aexit__(self, *_exc_info: Any) -> None:
        await self.close()

    async def start(self) -> None:
        """Initialize the underlying async HTTP client (idempotent)."""
        if self._client is None:
            self._client = httpx.AsyncClient(
                base_url=self._base_url,
                timeout=self._timeout,
            )
            logger.debug("HTTPX client started (base_url={})", self._base_url)

    async def close(self) -> None:
        """Close the underlying async HTTP client (idempotent)."""
        if self._client is not None:
            await self._client.aclose()
            self._client = None
            logger.debug("HTTPX client closed")

    def _require_client(self) -> httpx.AsyncClient:
        if self._client is None:
            raise WeatherServiceError(
                "WeatherService used before start() was called.", error_type="internal_error"
            )
        return self._client

    def _require_api_key(self) -> str:
        if not self._api_key or self._api_key == "your_api_key_here":
            raise MissingAPIKeyError()
        return self._api_key

    # -- low-level HTTP helper ----------------------------------------------
    async def _get(self, path: str, params: dict[str, Any]) -> dict[str, Any]:
        """
        Perform a GET request against the OpenWeatherMap API with basic
        retry-on-transient-failure logic, and translate HTTP-level errors
        into typed ``WeatherServiceError`` subclasses.
        """
        client = self._require_client()
        api_key = self._require_api_key()
        request_params = {**params, "appid": api_key}

        last_exc: Optional[Exception] = None
        for attempt in range(1, self._max_retries + 2):  # first try + retries
            try:
                logger.debug("GET {} params={} (attempt {})", path, params, attempt)
                response = await client.get(path, params=request_params)

                if response.status_code == 404:
                    raise CityNotFoundError(str(params.get("q", params.get("city", "unknown"))))

                if response.status_code == 401:
                    raise UpstreamAPIError(
                        401,
                        "Invalid or unauthorized API key. Double-check "
                        "OPENWEATHER_API_KEY in your .env file.",
                    )

                if response.status_code == 429:
                    raise UpstreamAPIError(
                        429, "Rate limit exceeded. Slow down requests or upgrade your API plan."
                    )

                if response.status_code >= 500:
                    # Retryable server-side failure.
                    raise NetworkError(f"upstream returned HTTP {response.status_code}")

                response.raise_for_status()
                return response.json()

            except (CityNotFoundError, UpstreamAPIError) as exc:
                # Non-retryable, well-classified errors: fail fast.
                raise exc
            except (httpx.TimeoutException, httpx.TransportError, NetworkError) as exc:
                last_exc = exc
                logger.warning("Transient error on attempt {}: {}", attempt, exc)
                if attempt > self._max_retries:
                    break
            except httpx.HTTPStatusError as exc:
                raise UpstreamAPIError(
                    exc.response.status_code, exc.response.text[:300]
                ) from exc

        raise NetworkError(str(last_exc) if last_exc else "unknown network failure")

    # -- public API ----------------------------------------------------------
    async def get_current_weather(
        self, city: str, units: UnitSystem = UnitSystem.METRIC
    ) -> CurrentWeather:
        """Fetch current weather conditions for a city."""
        data = await self._get(
            "/data/2.5/weather",
            {"q": city, "units": units.value, "lang": settings.default_lang},
        )
        return self._parse_current_weather(data, units)

    async def get_forecast(
        self, city: str, units: UnitSystem = UnitSystem.METRIC, days: int = 3
    ) -> WeatherForecast:
        """Fetch a multi-day forecast (3-hour resolution) for a city."""
        data = await self._get(
            "/data/2.5/forecast",
            {"q": city, "units": units.value, "lang": settings.default_lang},
        )
        return self._parse_forecast(data, units, days)

    async def compare_cities(
        self, cities: list[str], units: UnitSystem = UnitSystem.METRIC
    ) -> CityComparison:
        """Fetch and compare current weather across multiple cities."""
        entries: list[CityComparisonEntry] = []

        for city in cities:
            try:
                weather = await self.get_current_weather(city, units)
                conditions_summary = (
                    weather.conditions[0].description if weather.conditions else "unknown"
                )
                entries.append(
                    CityComparisonEntry(
                        city=weather.city,
                        temperature=weather.temperature,
                        feels_like=weather.feels_like,
                        humidity=weather.humidity,
                        wind_speed=weather.wind_speed,
                        conditions_summary=conditions_summary,
                    )
                )
            except WeatherServiceError as exc:
                logger.warning("compare_cities: failed for '{}': {}", city, exc.message)
                entries.append(
                    CityComparisonEntry(
                        city=city,
                        temperature=float("nan"),
                        feels_like=float("nan"),
                        humidity=0,
                        wind_speed=0.0,
                        conditions_summary="unavailable",
                        error=exc.message,
                    )
                )

        successful = [e for e in entries if e.error is None]
        warmest = max(successful, key=lambda e: e.temperature, default=None)
        coldest = min(successful, key=lambda e: e.temperature, default=None)
        most_humid = max(successful, key=lambda e: e.humidity, default=None)

        return CityComparison(
            units=units,
            results=entries,
            warmest_city=warmest.city if warmest else None,
            coldest_city=coldest.city if coldest else None,
            most_humid_city=most_humid.city if most_humid else None,
            generated_at=datetime.now(timezone.utc),
        )

    async def get_air_quality(self, city: str) -> AirQuality:
        """Fetch current air-quality data for a city (via geocoding + air_pollution)."""
        coords = await self._geocode(city)
        data = await self._get(
            "/data/2.5/air_pollution",
            {"lat": coords.latitude, "lon": coords.longitude},
        )
        return self._parse_air_quality(city, coords, data)

    async def get_alerts(self, city: str) -> WeatherAlertsResponse:
        """
        Fetch official weather alerts for a city.

        OpenWeatherMap exposes alerts via the "One Call" API, which requires
        a paid/subscribed plan on some accounts. If alerts are unavailable
        (e.g. HTTP 401/403 for this endpoint specifically), we degrade
        gracefully and return an empty alert list with an explanatory note
        rather than failing the whole tool call.
        """
        coords = await self._geocode(city)
        try:
            data = await self._get(
                "/data/3.0/onecall",
                {
                    "lat": coords.latitude,
                    "lon": coords.longitude,
                    "exclude": "current,minutely,hourly,daily",
                    "units": UnitSystem.METRIC.value,
                },
            )
        except UpstreamAPIError as exc:
            logger.info("Alerts endpoint unavailable for '{}': {}", city, exc.message)
            return WeatherAlertsResponse(
                city=city,
                coordinates=coords,
                alerts=[],
                alert_count=0,
                checked_at=datetime.now(timezone.utc),
                note=(
                    "Live alert data requires a One Call API 3.0 subscription on "
                    "OpenWeatherMap. No active alerts could be retrieved for this "
                    "account/plan."
                ),
            )

        raw_alerts = data.get("alerts", [])
        alerts = [self._parse_alert(a) for a in raw_alerts]
        return WeatherAlertsResponse(
            city=city,
            coordinates=coords,
            alerts=alerts,
            alert_count=len(alerts),
            checked_at=datetime.now(timezone.utc),
            note=None if alerts else "No active weather alerts for this location.",
        )

    # -- geocoding -----------------------------------------------------------
    async def _geocode(self, city: str) -> Coordinates:
        """Resolve a city name to latitude/longitude via the Geocoding API."""
        data = await self._get("/geo/1.0/direct", {"q": city, "limit": 1})
        if not data:
            raise CityNotFoundError(city)
        entry = data[0]
        return Coordinates(latitude=entry["lat"], longitude=entry["lon"])

    # -- parsing helpers -------------------------------------------------------
    @staticmethod
    def _parse_conditions(raw_weather: list[dict[str, Any]]) -> list[WeatherCondition]:
        return [
            WeatherCondition(
                id=w["id"], main=w["main"], description=w["description"], icon=w["icon"]
            )
            for w in raw_weather
        ]

    def _parse_current_weather(
        self, data: dict[str, Any], units: UnitSystem
    ) -> CurrentWeather:
        main = data.get("main", {})
        wind = data.get("wind", {})
        sys_ = data.get("sys", {})
        coord = data.get("coord", {})

        sunrise = (
            datetime.fromtimestamp(sys_["sunrise"], tz=timezone.utc)
            if "sunrise" in sys_
            else None
        )
        sunset = (
            datetime.fromtimestamp(sys_["sunset"], tz=timezone.utc)
            if "sunset" in sys_
            else None
        )

        return CurrentWeather(
            city=data.get("name", "Unknown"),
            country=sys_.get("country"),
            coordinates=Coordinates(
                latitude=coord.get("lat", 0.0), longitude=coord.get("lon", 0.0)
            ),
            temperature=main.get("temp", 0.0),
            feels_like=main.get("feels_like", 0.0),
            temp_min=main.get("temp_min", 0.0),
            temp_max=main.get("temp_max", 0.0),
            humidity=main.get("humidity", 0),
            pressure=main.get("pressure", 0),
            wind_speed=wind.get("speed", 0.0),
            wind_direction_degrees=wind.get("deg"),
            cloudiness_percent=data.get("clouds", {}).get("all", 0),
            visibility_meters=data.get("visibility"),
            conditions=self._parse_conditions(data.get("weather", [])),
            sunrise=sunrise,
            sunset=sunset,
            observed_at=datetime.fromtimestamp(data.get("dt", 0), tz=timezone.utc),
            units=units,
        )

    def _parse_forecast(
        self, data: dict[str, Any], units: UnitSystem, days: int
    ) -> WeatherForecast:
        city_info = data.get("city", {})
        coord = city_info.get("coord", {})

        raw_entries: list[dict[str, Any]] = data.get("list", [])
        # The free /forecast endpoint returns 3-hour steps for 5 days (40 entries).
        # Trim to the requested number of days (8 entries per day).
        max_entries = max(days, 1) * 8
        trimmed = raw_entries[:max_entries]

        entries = [
            ForecastEntry(
                timestamp=datetime.fromtimestamp(item["dt"], tz=timezone.utc),
                temperature=item.get("main", {}).get("temp", 0.0),
                feels_like=item.get("main", {}).get("feels_like", 0.0),
                temp_min=item.get("main", {}).get("temp_min", 0.0),
                temp_max=item.get("main", {}).get("temp_max", 0.0),
                humidity=item.get("main", {}).get("humidity", 0),
                wind_speed=item.get("wind", {}).get("speed", 0.0),
                cloudiness_percent=item.get("clouds", {}).get("all", 0),
                pop_percent=round(item.get("pop", 0.0) * 100, 1),
                conditions=self._parse_conditions(item.get("weather", [])),
            )
            for item in trimmed
        ]

        return WeatherForecast(
            city=city_info.get("name", "Unknown"),
            country=city_info.get("country"),
            coordinates=Coordinates(
                latitude=coord.get("lat", 0.0), longitude=coord.get("lon", 0.0)
            ),
            units=units,
            requested_days=days,
            entries=entries,
        )

    def _parse_air_quality(
        self, city: str, coords: Coordinates, data: dict[str, Any]
    ) -> AirQuality:
        items = data.get("list", [])
        if not items:
            raise UpstreamAPIError(200, "Air pollution API returned no data.")
        item = items[0]
        aqi = item.get("main", {}).get("aqi", 1)
        components_raw = item.get("components", {})

        return AirQuality(
            city=city,
            coordinates=coords,
            aqi=aqi,
            aqi_label=_AQI_LABELS.get(aqi, "Unknown"),
            components=AirQualityComponent(
                co=components_raw.get("co", 0.0),
                no=components_raw.get("no", 0.0),
                no2=components_raw.get("no2", 0.0),
                o3=components_raw.get("o3", 0.0),
                so2=components_raw.get("so2", 0.0),
                pm2_5=components_raw.get("pm2_5", 0.0),
                pm10=components_raw.get("pm10", 0.0),
                nh3=components_raw.get("nh3", 0.0),
            ),
            observed_at=datetime.fromtimestamp(item.get("dt", 0), tz=timezone.utc),
        )

    @staticmethod
    def _parse_alert(raw: dict[str, Any]) -> WeatherAlert:
        tags = [t.lower() for t in raw.get("tags", [])]
        severity = AlertSeverity.UNKNOWN
        for candidate in (AlertSeverity.EXTREME, AlertSeverity.SEVERE, AlertSeverity.MODERATE, AlertSeverity.MINOR):
            if candidate.value in tags:
                severity = candidate
                break

        return WeatherAlert(
            sender_name=raw.get("sender_name", "Unknown authority"),
            event=raw.get("event", "Weather Alert"),
            severity=severity,
            description=raw.get("description", ""),
            starts_at=datetime.fromtimestamp(raw.get("start", 0), tz=timezone.utc),
            ends_at=datetime.fromtimestamp(raw.get("end", 0), tz=timezone.utc),
        )


# Type alias used for grouping comparison results by a computed metric, kept
# here for potential future use by richer comparison/reporting tools.
GroupedResults = defaultdict[str, list[CityComparisonEntry]]
