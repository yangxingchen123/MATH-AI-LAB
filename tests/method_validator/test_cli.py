"""CLI tests for Method Validator v1."""

from __future__ import annotations

from pathlib import Path

from tools.method_validator.cli import run
from tests.method_validator.conftest import knowledge_md, method_md


def test_cli_check_passes(project: Path) -> None:
    (project / "01_知识库" / "K0001.md").write_text(
        knowledge_md(kid="K0001"), encoding="utf-8"
    )
    (project / "12_方法库" / "M0001.md").write_text(method_md(), encoding="utf-8")
    code = run(["check", "--root", str(project), "--summary"])
    assert code == 0


def test_cli_check_fails_on_error(project: Path) -> None:
    (project / "01_知识库" / "K0001.md").write_text(
        knowledge_md(kid="K0001"), encoding="utf-8"
    )
    (project / "12_方法库" / "M0001.md").write_text(
        method_md(extras="created: 2026-08-19"), encoding="utf-8"
    )
    code = run(["check", "--root", str(project), "--summary"])
    assert code == 1


def test_cli_check_file(project: Path) -> None:
    (project / "01_知识库" / "K0001.md").write_text(
        knowledge_md(kid="K0001"), encoding="utf-8"
    )
    path = project / "12_方法库" / "M0001.md"
    path.write_text(method_md(), encoding="utf-8")
    code = run(["check-file", str(path), "--root", str(project), "--summary"])
    assert code == 0
