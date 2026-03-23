"""Tests for zendev.commit — emoji commit convention."""

from __future__ import annotations

import re

from zendev.commit import EMOJI_MAP, ZendevAnswers, message, schema_pattern


def _answers(
    prefix: str = "feat",
    scope: str = "",
    subject: str = "test",
    body: str = "",
    footer: str = "",
    is_breaking_change: bool = False,
) -> ZendevAnswers:
    return ZendevAnswers(
        prefix=prefix,
        scope=scope,
        subject=subject,
        body=body,
        footer=footer,
        is_breaking_change=is_breaking_change,
    )


class TestEmojiMap:
    """Tests for emoji mapping."""

    def test_all_types_have_emoji(self) -> None:
        expected_types = {
            "init",
            "feat",
            "fix",
            "docs",
            "refactor",
            "test",
            "ci",
            "perf",
            "chore",
            "style",
            "build",
        }
        assert set(EMOJI_MAP.keys()) == expected_types

    def test_emoji_values_are_nonempty(self) -> None:
        for type_name, emoji in EMOJI_MAP.items():
            assert len(emoji) > 0, f"{type_name} has empty emoji"


class TestMessage:
    """Tests for the message() function."""

    def test_message_format(self) -> None:
        msg = message(_answers(prefix="feat", subject="add dark mode"))
        assert msg == "\u2728 feat: add dark mode"

    def test_message_with_scope(self) -> None:
        msg = message(_answers(prefix="fix", scope="parser", subject="null pointer"))
        assert msg == "\U0001f41b fix(parser): null pointer"

    def test_message_with_body(self) -> None:
        msg = message(_answers(prefix="feat", subject="add export", body="supports CSV and JSON"))
        assert "\u2728 feat: add export" in msg
        assert "supports CSV and JSON" in msg

    def test_message_breaking_change(self) -> None:
        msg = message(_answers(subject="new API", footer="migration guide", is_breaking_change=True))
        assert "BREAKING CHANGE" in msg


class TestSchemaPattern:
    """Tests for the schema_pattern() function."""

    def test_schema_pattern_matches_valid(self) -> None:
        pattern = re.compile(schema_pattern())
        valid_messages = [
            "\u2728 feat: add feature",
            "\U0001f41b fix: resolve bug",
            "\U0001f4dd docs: update readme",
            "\u267b\ufe0f refactor(core): extract helper",
            "\U0001f389 init: begin project",
            "\u26a1 perf: optimize query",
            "\U0001f527 chore: update deps",
        ]
        for msg in valid_messages:
            assert pattern.match(msg), f"Pattern should match: {msg}"

    def test_schema_pattern_rejects_invalid(self) -> None:
        pattern = re.compile(schema_pattern())
        invalid_messages = [
            "random message",
            "feat add feature",
            "feat:",
        ]
        for msg in invalid_messages:
            assert not pattern.match(msg), f"Pattern should reject: {msg}"
