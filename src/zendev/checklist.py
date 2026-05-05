"""Validate PR bodies contain required GitHub-task checklist rows from the template."""

from __future__ import annotations

import argparse
import re
import sys
from collections.abc import Sequence
from pathlib import Path

# Markdown task row marked checked in the template (expected to be copied into the PR unchanged).
_CHECKED_TASK_RE = re.compile(r"^\s*-\s*\[x\]\s+.+$")


def _h2_heading_match(line_stripped: str, section_title: str) -> bool | None:
    """Return True if line is ## <section_title>, False if other H2, None if not an H2 line."""
    m = re.match(r"^##\s+(.+)$", line_stripped)
    if not m:
        return None
    return m.group(1).strip() == section_title


def extract_required_checked_tasks(template_markdown: str, *, section_heading: str) -> list[str]:
    """Return checklist lines under ``## <section_heading>`` marked ``- [x] ...`` until the next H2.

    Skips fenced code blocks.  Each entry is ``raw_line`` with only trailing ``\\r``/``\\n`` removed
    so PR bodies can be matched verbatim the way templates are written.
    """
    in_fence = False
    in_section = False
    required: list[str] = []

    for raw_line in template_markdown.splitlines():
        stripped = raw_line.strip()
        if stripped.startswith("```"):
            in_fence = not in_fence
            continue
        if in_fence:
            continue

        h2_kind = _h2_heading_match(stripped, section_heading)
        if h2_kind is not None:
            in_section = h2_kind is True
            continue

        if not in_section:
            continue

        line = raw_line.rstrip("\r\n")
        if _CHECKED_TASK_RE.match(line):
            required.append(line)

    return required


def load_required_checked_tasks(template_path: Path, *, section_heading: str) -> list[str]:
    if not template_path.is_file():
        return []
    return extract_required_checked_tasks(
        template_path.read_text(encoding="utf-8"),
        section_heading=section_heading,
    )


def checklist_items_missing(body: str, required_lines: Sequence[str]) -> list[str]:
    """Return checklist lines that must appear verbatim in ``body`` but do not."""
    return [item for item in required_lines if item not in body]


def validate_checklist_cli(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="zendev-validate-checklist",
        description=(
            "Ensure the PR body still contains every `- [x] ...` line from "
            "a chosen template section (default: Checklist)."
        ),
    )
    parser.add_argument("body", help="PR body Markdown to validate.")
    parser.add_argument(
        "--template",
        metavar="PATH",
        default=".github/pull_request_template.md",
        help="Repo-relative path to the pull request template (default: .github/pull_request_template.md).",
    )
    parser.add_argument(
        "--section",
        metavar="TITLE",
        default="Checklist",
        help='H2 title (without "##") naming the checklist section (default: Checklist).',
    )
    parser.add_argument(
        "--fail-on-empty",
        action="store_true",
        help=(
            "Exit with status 1 when the template defines no `- [x]` rows in that section "
            "(default: succeed with a skip message)."
        ),
    )
    args = parser.parse_args(argv)

    template_path = Path(args.template)
    required = load_required_checked_tasks(template_path, section_heading=args.section)

    print("::group::PR / checklist")
    print(f"Template: {args.template}")
    print(f"Section:  ## {args.section}")
    print(f"Required `- [x]` rows: {len(required)}")
    print("::endgroup::")

    if not required:
        msg = "No `- [x]` checklist rows found under that heading; " + (
            "configured to fail." if args.fail_on_empty else "nothing to validate."
        )
        print(msg)
        return 1 if args.fail_on_empty else 0

    missing = checklist_items_missing(args.body, required)
    if missing:
        print("::error::PR body is missing required checked checklist items.", file=sys.stdout)
        for item in missing:
            print(item, file=sys.stdout)
        return 1

    print("PR checklist items look good.")
    return 0


def main() -> None:
    sys.exit(validate_checklist_cli())
