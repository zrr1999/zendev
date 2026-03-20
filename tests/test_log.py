"""Tests for zendev.log."""

from __future__ import annotations

import zendev.log as log_mod
from loguru import logger

from zendev.log import setup_log


class TestSetupLog:
    """Tests for setup_log()."""

    def setup_method(self) -> None:
        """Reset loguru state before each test."""
        logger.remove()
        log_mod._configured = False

    def test_default_adds_stderr_handler(self) -> None:
        setup_log()
        assert len(logger._core.handlers) == 1

    def test_idempotent(self) -> None:
        setup_log()
        setup_log()
        assert len(logger._core.handlers) == 1

    def test_verbose_sets_debug_level(self) -> None:
        setup_log(verbose=True)
        handler = next(iter(logger._core.handlers.values()))
        assert handler.levelno <= 10  # DEBUG = 10

    def test_json_mode(self) -> None:
        setup_log(json=True)
        handler = next(iter(logger._core.handlers.values()))
        assert handler.serialize is True

    def test_env_override(self, monkeypatch: object) -> None:
        monkeypatch.setenv("ZENDEV_LOG_LEVEL", "WARNING")  # type: ignore[attr-defined]
        setup_log()
        handler = next(iter(logger._core.handlers.values()))
        assert handler.levelno == 30  # WARNING = 30
