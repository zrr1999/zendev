"""Emoji commit convention for zendev — interactive commit tool."""

from __future__ import annotations

import subprocess
import sys
from collections import OrderedDict
from typing import TypedDict

import questionary

__all__ = ["EMOJI_MAP", "ZendevAnswers", "ask", "main", "message", "schema_pattern"]

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


def schema_pattern() -> str:
    types = "|".join(EMOJI_MAP.keys())
    return (
        r"(?s)"
        r"(\S+ )?"  # optional emoji
        r"(" + types + r")"
        r"(\(\S+\))?"  # optional scope
        r"!?"
        r": "
        r"([^\n\r]+)"  # subject
        r"((\n\n.*)|(\s*))?$"
    )


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
