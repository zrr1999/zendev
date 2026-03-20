"""Emoji commitizen plugin for zendev."""

from __future__ import annotations

from collections import OrderedDict
from typing import TYPE_CHECKING, Any, TypedDict

from commitizen.cz.base import BaseCommitizen
from commitizen.cz.utils import multiple_line_breaker, required_validator

if TYPE_CHECKING:
    from commitizen.question import CzQuestion

__all__ = ["EMOJI_MAP", "ZendevCz"]

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
    return required_validator(text.strip(".").strip(), msg="Subject is required.")


class ZendevAnswers(TypedDict):
    prefix: str
    scope: str
    subject: str
    body: str
    footer: str
    is_breaking_change: bool


class ZendevCz(BaseCommitizen):
    bump_pattern = BUMP_PATTERN
    bump_map = BUMP_MAP
    commit_parser = (
        r"^(?P<change_type>feat|fix|refactor|perf|BREAKING CHANGE)"
        r"(?:\((?P<scope>[^()\r\n]*)\)|\()?(?P<breaking>!)?:\s(?P<message>.*)?"
    )
    change_type_map = {"feat": "Feat", "fix": "Fix", "refactor": "Refactor", "perf": "Perf"}

    def questions(self) -> list[CzQuestion]:
        choices: list[dict[str, Any]] = []
        for type_name, emoji in EMOJI_MAP.items():
            desc = _DESCRIPTIONS.get(type_name, "")
            choices.append({"value": type_name, "name": f"{emoji} {type_name}: {desc}"})
        return [
            {"type": "list", "name": "prefix", "message": "Select the type of change you are committing", "choices": choices},
            {"type": "input", "name": "scope", "message": "Scope (press enter to skip):\n", "filter": _parse_scope},
            {"type": "input", "name": "subject", "message": "Short imperative summary:\n", "filter": _parse_subject},
            {"type": "input", "name": "body", "message": "Body (press enter to skip):\n", "filter": multiple_line_breaker},
            {"type": "confirm", "name": "is_breaking_change", "message": "Is this a BREAKING CHANGE?", "default": False},
            {"type": "input", "name": "footer", "message": "Footer (press enter to skip):\n"},
        ]

    def message(self, answers: ZendevAnswers) -> str:  # type: ignore[override]
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

    def example(self) -> str:
        return "✨ feat: add dark mode support\n\n🐛 fix(parser): resolve null pointer"

    def schema(self) -> str:
        return "<emoji> <type>(<scope>): <subject>\n\n<body>\n\n<footer>"

    def schema_pattern(self) -> str:
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

    def info(self) -> str:
        lines = ["zendev emoji commit convention\n"]
        lines.append("Format: <emoji> <type>(<scope>): <subject>\n")
        lines.append("Types:")
        for type_name, emoji in EMOJI_MAP.items():
            lines.append(f"  {emoji} {type_name}")
        return "\n".join(lines)
