"""Loguru configuration for all projects."""

from __future__ import annotations

import os
import sys

from loguru import logger

_configured = False


def setup_log(*, verbose: bool = False, json: bool = False) -> None:
    """Configure loguru for CLI usage. Safe to call multiple times.

    Args:
        verbose: If True, set log level to DEBUG. Defaults to False (INFO).
        json: If True, use JSON serialization (CI-friendly). Defaults to False.
    """
    global _configured  # noqa: PLW0603
    if _configured:
        return
    _configured = True

    logger.remove()

    env_level = os.environ.get("ZENDEV_LOG_LEVEL")
    if env_level:
        level = env_level.upper()
    else:
        level = "DEBUG" if verbose else "INFO"

    if json:
        logger.add(sys.stderr, level=level, serialize=True)
    else:
        fmt = "<green>{time:HH:mm:ss.SSS}</green> | <level>{level: <7}</level> | <level>{message}</level>"
        logger.add(sys.stderr, format=fmt, level=level, colorize=True)
