#!/usr/bin/env python3
"""Validate title text using zendev.commit.is_valid_commit_message (CI / composite action)."""

from __future__ import annotations

import os
import sys

from zendev.commit import EMOJI_MAP, is_valid_commit_message, suggest_commit_message


def _print_help() -> None:
    print("")
    print("Title must match zendev emoji commit conventions (same as zendev-commit-msg).")
    print("")
    print("  Expected: <emoji> <type>(<scope>): <description>")
    print("")
    print("  Type table:")
    table = [
        ("init", "Project initialization"),
        ("feat", "New feature"),
        ("fix", "Bug fix"),
        ("refactor", "Refactoring"),
        ("perf", "Performance"),
        ("docs", "Documentation"),
        ("test", "Tests"),
        ("build", "Build / dependencies"),
        ("ci", "CI configuration"),
        ("chore", "Miscellaneous"),
        ("style", "Code style"),
    ]
    for name, desc in table:
        emoji = EMOJI_MAP[name]
        print(f"    {emoji} {name:8} {desc}")
    print("")
    print("  Merge, Revert, fixup!, and squash! prefixes are allowed (git-generated).")
    print("")
    print("  Examples:")
    print("    ✨ feat: add JSON logging mode")
    print("    🐛 fix(parser): handle null token")
    print("    📦 build: add pytest-cov dependency")
    print("")


def main() -> int:
    text = os.environ.get("INPUT_TEXT", "")
    print("::group::PR / title check")
    print(f"Text: {text!r}")
    print("::endgroup::")

    if is_valid_commit_message(text):
        print("Title format is valid.")
        return 0

    print("::error::Title does not match zendev emoji commit conventions.")
    _print_help()
    suggestion = suggest_commit_message(text)
    if suggestion:
        first = suggestion.splitlines()[0]
        print(f"Maybe you meant: `{first}`.")
    print(f"Got: {text!r}")
    return 1


if __name__ == "__main__":
    sys.exit(main())
