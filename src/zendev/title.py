"""CLI entry point for validating PR titles in CI."""

from __future__ import annotations

import argparse
import sys
from collections.abc import Sequence

from zendev.commit import is_valid_commit_message, normalize_commit_message, report_invalid_commit_message


def validate_title_cli(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="zendev-validate-title",
        description="Validate a PR title against zendev emoji commit conventions.",
    )
    parser.add_argument("text", help="PR title text to validate.")
    args = parser.parse_args(argv)

    normalized = normalize_commit_message(args.text)
    print("::group::PR / title check")
    print(f"Text: {normalized!r}")
    print("::endgroup::")

    if is_valid_commit_message(normalized):
        print("Title format is valid.")
        return 0

    report_invalid_commit_message(normalized, context="ci", file=sys.stdout)
    return 1


def main() -> None:
    sys.exit(validate_title_cli())
