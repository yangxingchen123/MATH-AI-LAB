"""CLI tests for Attempt Validator."""

from __future__ import annotations

from pathlib import Path

from tools.attempt_validator.cli import run
from tests.attempt_validator.conftest import setup_p0002_multipart, write_attempt_project, write_single_attempt


def test_cli_check_passes(tmp_path: Path) -> None:
    project = write_attempt_project(tmp_path)
    setup_p0002_multipart(project)
    write_single_attempt(project)
    code = run(["check", "--root", str(project)])
    assert code == 0


def test_cli_check_file_passes(tmp_path: Path) -> None:
    project = write_attempt_project(tmp_path)
    setup_p0002_multipart(project)
    target = write_single_attempt(project)
    code = run(["check-file", str(target), "--root", str(project)])
    assert code == 0
