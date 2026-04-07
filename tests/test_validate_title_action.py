"""Regression tests for the validate-title composite action runtime path."""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VALIDATE_SCRIPT = ROOT / ".github" / "actions" / "validate-title" / "validate.py"


def run_validate_from_source_checkout(tmp_path: Path, title: str) -> subprocess.CompletedProcess[str]:
    checkout = tmp_path / "action-checkout"
    shutil.copytree(ROOT / "src", checkout / "src")

    action_dir = checkout / ".github" / "actions" / "validate-title"
    action_dir.mkdir(parents=True)
    shutil.copy2(VALIDATE_SCRIPT, action_dir / "validate.py")

    env = os.environ.copy()
    env["INPUT_TEXT"] = title
    env["PYTHONPATH"] = str(checkout / "src")

    return subprocess.run(
        [sys.executable, str(action_dir / "validate.py")],
        capture_output=True,
        check=False,
        env=env,
        text=True,
    )


def test_validate_title_script_runs_without_git_metadata(tmp_path: Path) -> None:
    result = run_validate_from_source_checkout(tmp_path, "✨ feat: portable action")

    assert result.returncode == 0
    assert "Title format is valid." in result.stdout


def test_validate_title_script_reports_invalid_titles_without_git_metadata(tmp_path: Path) -> None:
    result = run_validate_from_source_checkout(tmp_path, "feat: missing emoji")

    assert result.returncode == 1
    assert "::error::Title does not match zendev emoji commit conventions." in result.stdout
