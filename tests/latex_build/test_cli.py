"""CLI tests for latex_build."""

from __future__ import annotations

from tools.latex_build.cli import run


def test_cli_check_unknown_project(tmp_path, repo_root):
    code = run(["check", "04_LATEX/missing", "--root", str(repo_root)])
    assert code != 0
