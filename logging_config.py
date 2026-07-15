"""
logging_config.py
==================
Centralized Loguru configuration for the Weather MCP Server.

MCP servers that communicate over stdio MUST NOT write anything other than
protocol messages to stdout. All human-readable logs are therefore sent to
``stderr`` and to rotating log files on disk, never to ``stdout``.

Usage
-----
    from logging_config import configure_logging, get_logger

    configure_logging()
    logger = get_logger(__name__)
    logger.info("Server starting")
"""

from __future__ import annotations

import sys
from typing import Any

from loguru import logger as _logger

from config import settings

_CONFIGURED: bool = False


def configure_logging() -> None:
    """
    Configure Loguru sinks for console (stderr) and rotating file output.

    Safe to call multiple times; subsequent calls are no-ops so that
    importing this module from several places does not duplicate sinks.
    """
    global _CONFIGURED
    if _CONFIGURED:
        return

    _logger.remove()  # Remove Loguru's default handler.

    # Console sink -> stderr only (stdout is reserved for MCP JSON-RPC).
    _logger.add(
        sys.stderr,
        level=settings.log_level,
        colorize=True,
        format=(
            "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
            "<level>{level: <8}</level> | "
            "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> "
            "- <level>{message}</level>"
        ),
        backtrace=False,
        diagnose=False,
    )

    # File sink -> rotating, retained, compressed.
    settings.log_dir_path.mkdir(parents=True, exist_ok=True)
    log_file = settings.log_dir_path / "weather_mcp_server.log"
    _logger.add(
        str(log_file),
        level=settings.log_level,
        rotation="10 MB",
        retention="14 days",
        compression="zip",
        enqueue=True,
        backtrace=True,
        diagnose=False,
        format=(
            "{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | "
            "{name}:{function}:{line} - {message}"
        ),
    )

    _CONFIGURED = True
    _logger.debug("Logging configured (level={})", settings.log_level)


def get_logger(name: str | None = None) -> Any:
    """
    Return a Loguru logger bound with a ``name`` context field.

    Parameters
    ----------
    name:
        Typically ``__name__`` of the calling module.
    """
    configure_logging()
    return _logger.bind(module=name or "weather_mcp_server")


# Configure immediately on import so any early log calls are captured.
configure_logging()
logger = get_logger(__name__)
