"""
config.py
=========
Centralized, type-safe configuration for the Weather MCP Server.

All runtime configuration is loaded from environment variables (optionally
via a local ``.env`` file) and validated with Pydantic Settings. Importing
``settings`` anywhere in the codebase guarantees a single, validated source
of truth for configuration values.

Usage
-----
    from config import settings

    print(settings.openweather_api_key)
    print(settings.default_units)
"""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

# Root directory of the project (directory containing this file).
PROJECT_ROOT: Path = Path(__file__).resolve().parent


class Settings(BaseSettings):
    """
    Strongly typed application settings.

    Values are read from environment variables first, falling back to the
    ``.env`` file at the project root if present. See ``.env.example`` for
    a documented list of all supported variables.
    """

    model_config = SettingsConfigDict(
        env_file=str(PROJECT_ROOT / ".env"),
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # --- OpenWeatherMap API ---------------------------------------------
    openweather_api_key: str = Field(
        default="",
        description="API key for OpenWeatherMap. Required for live requests.",
    )
    openweather_base_url: str = Field(
        default="https://api.openweathermap.org",
        description="Base URL for the OpenWeatherMap REST API.",
    )

    # --- Defaults ---------------------------------------------------------
    default_units: Literal["metric", "imperial", "standard"] = Field(
        default="metric",
        description="Default unit system used when a tool call omits units.",
    )
    default_lang: str = Field(
        default="en",
        description="Default ISO 639-1 language code for weather descriptions.",
    )

    # --- HTTP behavior ------------------------------------------------------
    request_timeout_seconds: float = Field(
        default=10.0,
        gt=0,
        description="Timeout (seconds) applied to all outbound HTTP requests.",
    )
    max_retries: int = Field(
        default=3,
        ge=0,
        le=10,
        description="Maximum number of retries for transient HTTP failures.",
    )

    # --- Logging -----------------------------------------------------------
    log_level: Literal[
        "TRACE", "DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"
    ] = Field(default="INFO", description="Minimum log level to emit.")
    log_dir: str = Field(
        default="logs", description="Directory (relative or absolute) for log files."
    )

    # --- MCP server identity -------------------------------------------------
    mcp_server_name: str = Field(
        default="weather-mcp-server",
        description="Name advertised to MCP clients during initialization.",
    )

    @field_validator("openweather_api_key")
    @classmethod
    def _strip_api_key(cls, value: str) -> str:
        return value.strip()

    @property
    def has_api_key(self) -> bool:
        """Whether a (non-placeholder) API key has been configured."""
        return bool(self.openweather_api_key) and self.openweather_api_key != "your_api_key_here"

    @property
    def log_dir_path(self) -> Path:
        """Resolved, absolute path to the log directory."""
        path = Path(self.log_dir)
        if not path.is_absolute():
            path = PROJECT_ROOT / path
        return path


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """
    Return a cached ``Settings`` instance.

    Using ``lru_cache`` ensures the environment is parsed once per process
    while still allowing tests to bypass the cache by constructing
    ``Settings()`` directly.
    """
    return Settings()


# Convenient module-level singleton for typical application code.
settings: Settings = get_settings()
