"""Tests for the zendev-validate-title CLI."""

from __future__ import annotations

from zendev.title import validate_title_cli


def test_validate_title_cli_accepts_valid_title(capsys) -> None:
    assert validate_title_cli(["✨ feat: add portable action"]) == 0
    captured = capsys.readouterr()
    assert "Title format is valid." in captured.out


def test_validate_title_cli_rejects_invalid_title(capsys) -> None:
    assert validate_title_cli(["feat: missing emoji"]) == 1
    captured = capsys.readouterr()
    assert "::error::Title does not match zendev emoji commit conventions." in captured.out
