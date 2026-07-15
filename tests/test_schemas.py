"""
tests/test_schemas.py
======================
Unit tests for the Pydantic models defined in ``schemas.py``.
"""

from __future__ import annotations

from datetime import datetime, timezone

import pytest
from pydantic import ValidationError

from schemas import (
    CityComparisonEntry,
    CityQuery,
    Coordinates,
    CompareCitiesQuery,
    ForecastQuery,
    UnitSystem,
    WeatherCondition,
)


class TestCityQuery:
    def test_valid_city_defaults_to_metric(self) -> None:
        query = CityQuery(city="London")
        assert query.city == "London"
        assert query.units == UnitSystem.METRIC

    def test_strips_whitespace(self) -> None:
        query = CityQuery(city="  Paris  ")
        assert query.city == "Paris"

    def test_rejects_empty_city(self) -> None:
        with pytest.raises(ValidationError):
            CityQuery(city="")

    def test_rejects_whitespace_only_city(self) -> None:
        with pytest.raises(ValidationError):
            CityQuery(city="   ")

    def test_accepts_explicit_units(self) -> None:
        query = CityQuery(city="Tokyo", units=UnitSystem.IMPERIAL)
        assert query.units == UnitSystem.IMPERIAL


class TestForecastQuery:
    def test_default_days(self) -> None:
        query = ForecastQuery(city="Berlin")
        assert query.days == 3

    def test_days_upper_bound(self) -> None:
        with pytest.raises(ValidationError):
            ForecastQuery(city="Berlin", days=6)

    def test_days_lower_bound(self) -> None:
        with pytest.raises(ValidationError):
            ForecastQuery(city="Berlin", days=0)


class TestCompareCitiesQuery:
    def test_requires_at_least_two_cities(self) -> None:
        with pytest.raises(ValidationError):
            CompareCitiesQuery(cities=["London"])

    def test_filters_blank_entries(self) -> None:
        query = CompareCitiesQuery(cities=["London", "  ", "Paris"])
        assert query.cities == ["London", "Paris"]

    def test_max_ten_cities(self) -> None:
        with pytest.raises(ValidationError):
            CompareCitiesQuery(cities=[f"City{i}" for i in range(11)])


class TestCoordinates:
    def test_valid_coordinates(self) -> None:
        coords = Coordinates(latitude=51.5, longitude=-0.12)
        assert coords.latitude == 51.5
        assert coords.longitude == -0.12

    def test_latitude_out_of_range(self) -> None:
        with pytest.raises(ValidationError):
            Coordinates(latitude=91.0, longitude=0.0)

    def test_longitude_out_of_range(self) -> None:
        with pytest.raises(ValidationError):
            Coordinates(latitude=0.0, longitude=-181.0)


class TestWeatherCondition:
    def test_construction(self) -> None:
        condition = WeatherCondition(
            id=800, main="Clear", description="clear sky", icon="01d"
        )
        assert condition.id == 800
        assert condition.description == "clear sky"


class TestCityComparisonEntry:
    def test_error_defaults_to_none(self) -> None:
        entry = CityComparisonEntry(
            city="London",
            temperature=18.0,
            feels_like=17.5,
            humidity=60,
            wind_speed=3.6,
            conditions_summary="clear sky",
        )
        assert entry.error is None

    def test_can_carry_error(self) -> None:
        entry = CityComparisonEntry(
            city="Nowhereville",
            temperature=float("nan"),
            feels_like=float("nan"),
            humidity=0,
            wind_speed=0.0,
            conditions_summary="unavailable",
            error="City not found",
        )
        assert entry.error == "City not found"


def test_datetime_fields_serialize_to_iso8601() -> None:
    """Sanity check that datetime fields round-trip correctly via model_dump(mode='json')."""
    coords = Coordinates(latitude=0.0, longitude=0.0)
    now = datetime.now(timezone.utc)
    dumped_coords = coords.model_dump(mode="json")
    assert dumped_coords["latitude"] == 0.0
    assert isinstance(now.isoformat(), str)
