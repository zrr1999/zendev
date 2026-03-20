"""Tests for zendev.cz — emoji commitizen plugin."""

from __future__ import annotations

import re

import pytest
from commitizen.config.base_config import BaseConfig

from zendev.cz import EMOJI_MAP, ZendevCz


class TestEmojiMap:
    """Tests for emoji mapping."""

    def test_all_types_have_emoji(self) -> None:
        expected_types = {"init", "feat", "fix", "docs", "refactor", "test", "ci", "perf", "chore", "style", "build"}
        assert set(EMOJI_MAP.keys()) == expected_types

    def test_emoji_values_are_nonempty(self) -> None:
        for type_name, emoji in EMOJI_MAP.items():
            assert len(emoji) > 0, f"{type_name} has empty emoji"


class TestZendevCz:
    """Tests for the commitizen plugin."""

    @pytest.fixture()
    def cz(self) -> ZendevCz:
        config = BaseConfig()
        return ZendevCz(config)

    def test_questions_returns_list(self, cz: ZendevCz) -> None:
        qs = cz.questions()
        assert isinstance(qs, list)
        assert len(qs) > 0
        assert qs[0]["name"] == "prefix"

    def test_message_format(self, cz: ZendevCz) -> None:
        answers = {"prefix": "feat", "scope": "", "subject": "add dark mode", "body": "", "footer": "", "is_breaking_change": False}
        msg = cz.message(answers)
        assert msg == "✨ feat: add dark mode"

    def test_message_with_scope(self, cz: ZendevCz) -> None:
        answers = {"prefix": "fix", "scope": "parser", "subject": "null pointer", "body": "", "footer": "", "is_breaking_change": False}
        msg = cz.message(answers)
        assert msg == "🐛 fix(parser): null pointer"

    def test_message_with_body(self, cz: ZendevCz) -> None:
        answers = {"prefix": "feat", "scope": "", "subject": "add export", "body": "supports CSV and JSON", "footer": "", "is_breaking_change": False}
        msg = cz.message(answers)
        assert "✨ feat: add export" in msg
        assert "supports CSV and JSON" in msg

    def test_message_breaking_change(self, cz: ZendevCz) -> None:
        answers = {"prefix": "feat", "scope": "", "subject": "new API", "body": "", "footer": "migration guide", "is_breaking_change": True}
        msg = cz.message(answers)
        assert "BREAKING CHANGE" in msg

    def test_schema_pattern_matches_valid(self, cz: ZendevCz) -> None:
        pattern = re.compile(cz.schema_pattern())
        valid_messages = [
            "✨ feat: add feature",
            "🐛 fix: resolve bug",
            "📝 docs: update readme",
            "♻️ refactor(core): extract helper",
            "🎉 init: begin project",
            "⚡ perf: optimize query",
            "🔧 chore: update deps",
        ]
        for msg in valid_messages:
            assert pattern.match(msg), f"Pattern should match: {msg}"

    def test_schema_pattern_rejects_invalid(self, cz: ZendevCz) -> None:
        pattern = re.compile(cz.schema_pattern())
        invalid_messages = [
            "random message",
            "feat add feature",
            "feat:",
        ]
        for msg in invalid_messages:
            assert not pattern.match(msg), f"Pattern should reject: {msg}"

    def test_example(self, cz: ZendevCz) -> None:
        ex = cz.example()
        assert "feat" in ex

    def test_schema(self, cz: ZendevCz) -> None:
        s = cz.schema()
        assert "type" in s.lower() or "emoji" in s.lower()

    def test_info(self, cz: ZendevCz) -> None:
        info = cz.info()
        assert len(info) > 0
