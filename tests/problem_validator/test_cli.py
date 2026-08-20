"""CLI tests for Problem Validator v1."""

from __future__ import annotations

import json
from pathlib import Path

from tools.problem_validator.cli import run
from tests.problem_validator.conftest import knowledge_md, problem_md


def _write_valid(project: Path) -> None:
    (project / "01_知识库" / "K0001.md").write_text(
        knowledge_md(kid="K0001"), encoding="utf-8"
    )
    (project / "02_题目库" / "P0001.md").write_text(problem_md(), encoding="utf-8")


def test_check_clean_exit(project: Path) -> None:
    _write_valid(project)
    assert run(["check", "--root", str(project)]) == 0


def test_check_file(project: Path) -> None:
    _write_valid(project)
    path = project / "02_题目库" / "P0001.md"
    assert run(["check-file", str(path), "--root", str(project)]) == 0


def test_json_format(project: Path) -> None:
    _write_valid(project)
    code = run(["check", "--root", str(project), "--format", "json"])
    assert code == 0


def test_summary(project: Path) -> None:
    _write_valid(project)
    assert run(["check", "--root", str(project), "--summary"]) == 0


def test_verbose(project: Path) -> None:
    _write_valid(project)
    assert run(["check", "--root", str(project), "--verbose"]) == 0


def test_warning_only_normal_exit(project: Path) -> None:
    (project / "01_知识库" / "K0001.md").write_text(
        knowledge_md(kid="K0001"), encoding="utf-8"
    )
    (project / "02_题目库" / "P0001.md").write_text(
        problem_md(extras="foo: bar"), encoding="utf-8"
    )
    assert run(["check", "--root", str(project)]) == 0


def test_strict_warnings_exit(project: Path) -> None:
    (project / "01_知识库" / "K0001.md").write_text(
        knowledge_md(kid="K0001"), encoding="utf-8"
    )
    (project / "02_题目库" / "P0001.md").write_text(
        problem_md(extras="foo: bar"), encoding="utf-8"
    )
    assert run(["check", "--root", str(project), "--strict-warnings"]) == 1


def test_error_exit(project: Path) -> None:
    (project / "01_知识库" / "K0001.md").write_text(
        knowledge_md(kid="K0001"), encoding="utf-8"
    )
    (project / "02_题目库" / "P0001.md").write_text(
        problem_md(pid="P0000"), encoding="utf-8"
    )
    assert run(["check", "--root", str(project)]) == 1


def test_json_loads(project: Path) -> None:
    _write_valid(project)
    import io
    import sys

    captured = io.StringIO()
    old = sys.stdout
    sys.stdout = captured
    try:
        run(["check", "--root", str(project), "--format", "json"])
    finally:
        sys.stdout = old
    payload = json.loads(captured.getvalue())
    assert payload["result"] == "PASS"
