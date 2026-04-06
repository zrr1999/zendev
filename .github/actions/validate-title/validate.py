#!/usr/bin/env python3
"""Validate title text using zendev.commit (CI / composite action)."""

from __future__ import annotations

import os
import sys

from zendev.commit import (
    is_valid_commit_message,
    normalize_commit_message,
    report_invalid_commit_message,
)


def main() -> int:
    text = os.environ.get("INPUT_TEXT", "")
    normalized = normalize_commit_message(text)
    print("::group::PR / title check")
    print(f"Text: {normalized!r}")
    print("::endgroup::")

    if is_valid_commit_message(normalized):
        print("Title format is valid.")
        return 0

    report_invalid_commit_message(normalized, context="ci", file=sys.stdout)
    return 1


if __name__ == "__main__":
    sys.exit(main())
