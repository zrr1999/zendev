#!/usr/bin/env python3
"""Validate title text using zendev.commit (CI / composite action)."""

from __future__ import annotations

import importlib.util
import os
import sys
from pathlib import Path
from types import ModuleType


def load_commit_module() -> ModuleType:
    action_path = os.environ.get("GITHUB_ACTION_PATH")
    if action_path:
        root = Path(action_path).resolve().parents[2]
        commit_path = root / "src" / "zendev" / "commit.py"
        spec = importlib.util.spec_from_file_location("zendev_commit", commit_path)
        if spec is None or spec.loader is None:
            raise RuntimeError(f"Unable to load zendev.commit from {commit_path}")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module

    from zendev import commit as module

    return module


commit = load_commit_module()


def main() -> int:
    text = os.environ.get("INPUT_TEXT", "")
    normalized = commit.normalize_commit_message(text)
    print("::group::PR / title check")
    print(f"Text: {normalized!r}")
    print("::endgroup::")

    if commit.is_valid_commit_message(normalized):
        print("Title format is valid.")
        return 0

    commit.report_invalid_commit_message(normalized, context="ci", file=sys.stdout)
    return 1


if __name__ == "__main__":
    sys.exit(main())
