"""Emoji commit convention for zendev — interactive commit tool."""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from collections import OrderedDict
from collections.abc import Sequence
from pathlib import Path
from typing import Literal, TextIO, TypedDict

import questionary

__all__ = [
    "COMMIT_CONVENTION_EXAMPLES",
    "EMOJI_MAP",
    "TYPE_DISPLAY_ORDER",
    "TYPE_SHORT_DESCRIPTIONS",
    "ZendevAnswers",
    "ask",
    "commit_msg_hook",
    "format_commit_convention_help_body",
    "hook_main",
    "is_valid_commit_message",
    "main",
    "message",
    "report_invalid_commit_message",
    "schema_pattern",
    "suggest_commit_message",
]

EMOJI_MAP: dict[str, str] = {
    "init": "\U0001f389",
    "feat": "\u2728",
    "fix": "\U0001f41b",
    "docs": "\U0001f4dd",
    "refactor": "\u267b\ufe0f",
    "test": "\u2705",
    "ci": "\U0001f477",
    "perf": "\u26a1",
    "chore": "\U0001f527",
    "style": "\U0001f3a8",
    "build": "\U0001f4e6",
}

_DESCRIPTIONS: dict[str, str] = {
    "init": "Project initialization",
    "feat": "A new feature",
    "fix": "A bug fix",
    "docs": "Documentation only changes",
    "refactor": "A code change that neither fixes a bug nor adds a feature",
    "test": "Adding missing or correcting existing tests",
    "ci": "Changes to CI configuration files and scripts",
    "perf": "A code change that improves performance",
    "chore": "Other changes that don't modify src or test files",
    "style": "Changes that do not affect the meaning of the code",
    "build": "Changes that affect the build system or external dependencies",
}

# Short labels for CLI / CI help tables (single source with EMOJI_MAP).
TYPE_SHORT_DESCRIPTIONS: dict[str, str] = {
    "init": "Project initialization",
    "feat": "New feature",
    "fix": "Bug fix",
    "refactor": "Refactoring",
    "perf": "Performance",
    "docs": "Documentation",
    "test": "Tests",
    "build": "Build / dependencies",
    "ci": "CI configuration",
    "chore": "Miscellaneous",
    "style": "Code style",
}

# Stable display order for help output (matches interactive type ordering intent).
TYPE_DISPLAY_ORDER: tuple[str, ...] = (
    "init",
    "feat",
    "fix",
    "refactor",
    "perf",
    "docs",
    "test",
    "build",
    "ci",
    "chore",
    "style",
)

COMMIT_CONVENTION_EXAMPLES: tuple[str, ...] = (
    "✨ feat: add JSON logging mode",
    "🐛 fix(parser): handle null token",
    "📦 build: add pytest-cov dependency",
)

BUMP_PATTERN = r"^((BREAKING[\-\ ]CHANGE|\w+)(\(.+\))?!?):"
BUMP_MAP: OrderedDict[str, str] = OrderedDict(
    (
        (r"^.+!$", "MAJOR"),
        (r"^BREAKING[\-\ ]CHANGE", "MAJOR"),
        (r"^feat", "MINOR"),
        (r"^fix", "PATCH"),
        (r"^refactor", "PATCH"),
        (r"^perf", "PATCH"),
    )
)

SPECIAL_COMMIT_PREFIXES = ("Merge ", "Revert ", "fixup! ", "squash! ")

assert set(TYPE_DISPLAY_ORDER) == set(EMOJI_MAP.keys())
assert set(TYPE_SHORT_DESCRIPTIONS.keys()) == set(EMOJI_MAP.keys())


def _parse_scope(text: str) -> str:
    return "-".join(text.strip().split())


def _parse_subject(text: str) -> str:
    subject = text.strip(".").strip()
    if not subject:
        raise ValueError("Subject is required.")
    return subject


class ZendevAnswers(TypedDict):
    prefix: str
    scope: str
    subject: str
    body: str
    footer: str
    is_breaking_change: bool


def message(answers: ZendevAnswers) -> str:
    prefix = answers["prefix"]
    scope = answers["scope"]
    subject = answers["subject"]
    body = answers["body"]
    footer = answers["footer"]
    is_breaking_change = answers["is_breaking_change"]

    emoji = EMOJI_MAP.get(prefix, "")
    formatted_scope = f"({scope})" if scope else ""
    title = f"{emoji} {prefix}{formatted_scope}"

    if is_breaking_change:
        footer = f"BREAKING CHANGE: {footer}"

    formatted_body = f"\n\n{body}" if body else ""
    formatted_footer = f"\n\n{footer}" if footer else ""

    return f"{title}: {subject}{formatted_body}{formatted_footer}"


def schema_pattern(*, require_emoji: bool = True) -> str:
    types = "|".join(EMOJI_MAP.keys())
    return (
        r"(?s)"
        + (r"(\S+ )" if require_emoji else r"(\S+ )?")
        + r"("
        + types
        + r")"
        + r"(\(\S+\))?"  # optional scope
        + r"!?"
        + r": "
        + r"([^\n\r]+)"  # subject
        + r"((\n\n.*)|(\s*))?$"
    )


def normalize_commit_message(text: str) -> str:
    lines = [line.rstrip() for line in text.splitlines() if not line.startswith("#")]
    return "\n".join(lines).strip()


def is_valid_commit_message(text: str) -> bool:
    normalized = normalize_commit_message(text)
    if not normalized:
        return False
    if normalized.startswith(SPECIAL_COMMIT_PREFIXES):
        return True
    return re.fullmatch(schema_pattern(), normalized) is not None


def suggest_commit_message(text: str) -> str | None:
    normalized = normalize_commit_message(text)
    if not normalized or is_valid_commit_message(normalized):
        return None
    if re.fullmatch(schema_pattern(require_emoji=False), normalized) is None:
        return None
    first_token = normalized.split(":", 1)[0]
    commit_type = first_token.split("(", 1)[0].rstrip("!")
    emoji = EMOJI_MAP.get(commit_type)
    if emoji is None:
        return None
    return f"{emoji} {normalized}"


def _format_type_table_lines() -> list[str]:
    lines: list[str] = []
    for name in TYPE_DISPLAY_ORDER:
        emoji = EMOJI_MAP[name]
        desc = TYPE_SHORT_DESCRIPTIONS[name]
        lines.append(f"    {emoji} {name:8} {desc}")
    return lines


def format_commit_convention_help_body(*, include_special_prefix_note: bool = True) -> str:
    parts: list[str] = [
        "",
        "  Expected: <emoji> <type>(<scope>): <description>",
        "",
        "  Type table:",
        *_format_type_table_lines(),
        "",
    ]
    if include_special_prefix_note:
        parts.append("  Merge, Revert, fixup!, and squash! prefixes are allowed (git-generated).")
        parts.append("")
    parts.extend(
        [
            "  Examples:",
            *(f"    {ex}" for ex in COMMIT_CONVENTION_EXAMPLES),
        ]
    )
    return "\n".join(parts)


def report_invalid_commit_message(
    normalized: str,
    *,
    context: Literal["hook", "ci"],
    file: TextIO,
) -> None:
    """Print a unified error for invalid messages (commit-msg hook or CI title check)."""
    suggestion = suggest_commit_message(normalized)
    if context == "hook":
        print("Invalid commit message.", file=file)
        print("An emoji prefix is required.", file=file)
    else:
        print("::error::Title does not match zendev emoji commit conventions.", file=file)

    print(format_commit_convention_help_body(), file=file)

    if suggestion:
        print(f"Maybe you meant: `{suggestion.splitlines()[0]}`.", file=file)
    elif context == "hook":
        print("Example: `✨ feat: generalize upgrade`.", file=file)

    received_line = normalized.splitlines()[0] if normalized else ""
    print(f"Received: {received_line!r}", file=file)


def commit_msg_hook(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="zendev-commit-msg",
        description="Validate commit messages against zendev emoji commit conventions.",
    )
    parser.add_argument("commit_msg_file", help="Path to the commit message file provided by git/pre-commit.")
    args = parser.parse_args(argv)

    message_text = Path(args.commit_msg_file).read_text(encoding="utf-8")
    normalized = normalize_commit_message(message_text)
    if is_valid_commit_message(normalized):
        return 0

    report_invalid_commit_message(normalized, context="hook", file=sys.stderr)
    return 1


def ask() -> ZendevAnswers:
    """Interactively prompt the user for commit details."""
    choices = [
        questionary.Choice(title=f"{emoji} {name}: {_DESCRIPTIONS[name]}", value=name)
        for name, emoji in EMOJI_MAP.items()
    ]

    prefix = questionary.select("Select the type of change you are committing", choices=choices).ask()
    if prefix is None:
        raise KeyboardInterrupt

    scope_raw = questionary.text("Scope (press enter to skip):").ask()
    if scope_raw is None:
        raise KeyboardInterrupt
    scope = _parse_scope(scope_raw)

    subject_raw = questionary.text("Short imperative summary:").ask()
    if subject_raw is None:
        raise KeyboardInterrupt
    subject = _parse_subject(subject_raw)

    body = questionary.text("Body (press enter to skip):").ask()
    if body is None:
        raise KeyboardInterrupt

    is_breaking_change = questionary.confirm("Is this a BREAKING CHANGE?", default=False).ask()
    if is_breaking_change is None:
        raise KeyboardInterrupt

    footer = questionary.text("Footer (press enter to skip):").ask()
    if footer is None:
        raise KeyboardInterrupt

    return ZendevAnswers(
        prefix=prefix,
        scope=scope,
        subject=subject,
        body=body,
        footer=footer,
        is_breaking_change=is_breaking_change,
    )


def main() -> None:
    """Entry point for zendev-commit."""
    try:
        answers = ask()
    except KeyboardInterrupt:
        print("\nAborted.")
        sys.exit(1)

    msg = message(answers)
    result = subprocess.run(["git", "commit", "-m", msg], check=False)
    sys.exit(result.returncode)


def hook_main() -> None:
    """Entry point for the reusable commit-msg hook."""
    sys.exit(commit_msg_hook())
