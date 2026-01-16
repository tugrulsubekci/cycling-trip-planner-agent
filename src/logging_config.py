"""Centralized logging configuration for Cycling Trip Planner Agent."""

import logging
import sys
from typing import Literal

LogLevel = Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]


def setup_logging(
    level: LogLevel | str = "INFO",
    format_string: str | None = None,
    date_format: str | None = None,
) -> None:
    """Configure logging for the application.

    Args:
        level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        format_string: Custom log format string. Defaults to standard format.
        date_format: Custom date format string. Defaults to standard format.
    """
    # Normalize log level
    log_level = getattr(logging, level.upper(), logging.INFO)

    # Default format strings
    if format_string is None:
        format_string = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    if date_format is None:
        date_format = "%Y-%m-%d %H:%M:%S"

    # Configure root logger
    logging.basicConfig(
        level=log_level,
        format=format_string,
        datefmt=date_format,
        stream=sys.stdout,
        force=True,  # Override any existing configuration
    )
