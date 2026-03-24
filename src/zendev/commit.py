"""Emoji commit convention for zendev — interactive commit tool."""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from collections import OrderedDict
from collections.abc import Sequence
from pathlib import Path
from typing import TypedDict

import questionary

__all__ = [
    "EMOJI_MAP",
    "ZendevAnswers",
    "ask",
    "commit_msg_hook",
    "hook_main",
    "is_valid_commit_message",
    "main",
    "message",
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

    suggestion = suggest_commit_message(normalized)
    print("Invalid commit message.", file=sys.stderr)
    print("An emoji prefix is required.", file=sys.stderr)
    print("Expected format: `<emoji> type(scope): subject`.", file=sys.stderr)
    if suggestion:
        print(f"Maybe you meant: `{suggestion.splitlines()[0]}`.", file=sys.stderr)
    else:
        print("Example: `✨ feat: generalize upgrade`.", file=sys.stderr)
    print(f"Allowed types: {', '.join(EMOJI_MAP)}.", file=sys.stderr)
    if normalized:
        print(f"Received: {normalized.splitlines()[0]}", file=sys.stderr)
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
