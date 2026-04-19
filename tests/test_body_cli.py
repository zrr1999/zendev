"""Tests for zendev-validate-body CLI."""

from __future__ import annotations

import pytest

from zendev.body import _extract_h2_headings, validate_body


VALID_BODY = """\
## Summary

Some description here.

## Validation

- ran tests

## Notes

None.
"""

WRONG_BODY = """\
## Summary

Some description.

## Checklist

- [ ] Done
"""

EMPTY_BODY = ""

REQUIRED = ["Summary", "Validation", "Notes"]


def test_extract_h2_headings_normal():
    assert _extract_h2_headings(VALID_BODY) == ["Summary", "Validation", "Notes"]


def test_extract_h2_headings_skips_fences():
    body = "## Summary\n\n```\n## Not a heading\n```\n\n## Validation\n\n## Notes"
    assert _extract_h2_headings(body) == ["Summary", "Validation", "Notes"]


def test_validate_body_valid():
    ok, actual = validate_body(VALID_BODY, REQUIRED)
    assert ok
    assert actual == REQUIRED


def test_validate_body_wrong_sections():
    ok, actual = validate_body(WRONG_BODY, REQUIRED)
    assert not ok
    assert actual == ["Summary", "Checklist"]


def test_validate_body_empty():
    ok, actual = validate_body(EMPTY_BODY, REQUIRED)
    assert not ok
    assert actual == []
