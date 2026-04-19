"""CLI entry point for validating PR bodies in CI."""

from __future__ import annotations

import argparse
import re
import sys
from collections.abc import Sequence
from pathlib import Path
from typing import TextIO

from zendev.commit import format_commit_convention_help_body

REQUIRED_SECTIONS: tuple[str, ...] = ("Summary", "Validation", "Notes")


def _extract_h2_headings(text: str) -> list[str]:
    """Return H2 heading text (without the `## ` prefix), skipping fenced code blocks."""
    in_fence = False
    headings: list[str] = []
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("```"):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        if re.match(r"^##\s+\S", stripped):
            headings.append(re.sub(r"^##\s+", "", stripped))
    return headings


def _load_template_headings(template_path: Path | None) -> list[str]:
    """Return required H2 headings from the PR template file, or fall back to defaults."""
    if template_path is not None and template_path.exists():
        return _extract_h2_headings(template_path.read_text(encoding="utf-8"))
    return list(REQUIRED_SECTIONS)


def validate_body(body: str, required_headings: list[str]) -> tuple[bool, list[str]]:
    """Validate PR body sections.  Returns (is_valid, actual_headings)."""
    actual = _extract_h2_headings(body)
    return actual == required_headings, actual


def report_invalid_body(
    actual: list[str],
    expected: list[str],
    *,
    file: TextIO,
) -> None:
    print("::error::PR body headings do not match the repository template.", file=file)
    print(f"\n  Expected headings: {expected}", file=file)
    print(f"  Actual headings:   {actual}", file=file)
    print(file=file)
    print("  Each PR body should contain exactly these H2 sections:", file=file)
    for section in expected:
        print(f"    ## {section}", file=file)
    print(file=file)
    print("  Commit convention reference (for the Summary section):", file=file)
    print(format_commit_convention_help_body(include_special_prefix_note=False), file=file)


def validate_body_cli(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="zendev-validate-body",
        description="Validate a PR body against required section headings.",
    )
    parser.add_argument("body", help="PR body text to validate.")
    parser.add_argument(
        "--template",
        metavar="PATH",
        default=".github/pull_request_template.md",
        help="Path to the PR template file (default: .github/pull_request_template.md).",
    )
    args = parser.parse_args(argv)

    template_path = Path(args.template)
    required = _load_template_headings(template_path)

    print("::group::PR / body check")
    print(f"Required headings: {required}")
    print("::endgroup::")

    is_valid, actual = validate_body(args.body, required)
    if is_valid:
        print("PR body headings are valid.")
        return 0

    report_invalid_body(actual, required, file=sys.stdout)
    return 1


def main() -> None:
    sys.exit(validate_body_cli())
