"""Tests for zendev-validate-checklist."""

from __future__ import annotations

from pathlib import Path

from zendev.checklist import (
    checklist_items_missing,
    extract_required_checked_tasks,
    validate_checklist_cli,
)

_TEMPLATE = """\
## Proposal summary

x

## Checklist

- [x] First item here.
- [ ] Unchecked skip.
- [x] Second item here.

## Notes for reviewers

done
"""

_TEMPLATE_FENCE = """\
## Checklist

```text
- [x] inside a fence
```

- [x] Real item one.
"""


def test_extract_required_checked_tasks_filters_unchecked_and_heading() -> None:
    assert extract_required_checked_tasks(_TEMPLATE, section_heading="Checklist") == [
        "- [x] First item here.",
        "- [x] Second item here.",
    ]


def test_extract_skips_fenced_checklist_lookalikes() -> None:
    assert extract_required_checked_tasks(_TEMPLATE_FENCE, section_heading="Checklist") == [
        "- [x] Real item one.",
    ]


def test_checklist_items_missing() -> None:
    body = "## Checklist\n\n- [x] First item here.\n\nMissing second.\n"
    required = ["- [x] First item here.", "- [x] Second item here."]
    missing = checklist_items_missing(body, required)
    assert missing == ["- [x] Second item here."]


def test_validate_checklist_cli_success(tmp_path: Path) -> None:
    template = tmp_path / "pull_request_template.md"
    template.write_text(_TEMPLATE, encoding="utf-8")
    body = "\n".join(
        [
            "## Checklist",
            "",
            "- [x] First item here.",
            "- [x] Second item here.",
            "",
        ]
    )
    assert validate_checklist_cli([body, "--template", str(template)]) == 0


def test_validate_checklist_cli_reports_missing(tmp_path: Path) -> None:
    template = tmp_path / "pull_request_template.md"
    template.write_text(_TEMPLATE, encoding="utf-8")
    body = "## Checklist\n\n- [x] First item here.\n"
    assert validate_checklist_cli([body, "--template", str(template)]) == 1


def test_validate_checklist_cli_fail_on_empty(tmp_path: Path) -> None:
    template = tmp_path / "t.md"
    template.write_text("# no checklist\n", encoding="utf-8")
    assert (
        validate_checklist_cli(
            [
                "any",
                "--template",
                str(template),
                "--fail-on-empty",
            ]
        )
        == 1
    )

    assert validate_checklist_cli(["any", "--template", str(template)]) == 0


def test_validate_checklist_cli_missing_template_is_noop(tmp_path: Path) -> None:
    missing = tmp_path / "missing.md"
    assert validate_checklist_cli(["body", "--template", str(missing)]) == 0
