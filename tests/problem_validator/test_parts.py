"""parts field validation tests."""

from __future__ import annotations

from pathlib import Path

from tools.problem_validator.validator import validate_project
from tests.problem_validator.conftest import knowledge_md, problem_md


def _setup(project: Path, extras: str) -> None:
    (project / "01_知识库" / "K0001.md").write_text(
        knowledge_md(kid="K0001"), encoding="utf-8"
    )
    (project / "02_题目库" / "P0001.md").write_text(
        problem_md(extras=extras), encoding="utf-8"
    )


def test_no_parts_passes(project: Path) -> None:
    _setup(project, "")
    assert validate_project(root=project).summary.errors == 0


def test_valid_parts(project: Path) -> None:
    _setup(project, "parts:\n  - a\n  - b\n  - c")
    assert validate_project(root=project).summary.errors == 0


def test_numeric_string_parts_passes(project: Path) -> None:
    _setup(project, 'parts:\n  - "1"\n  - "2"')
    assert validate_project(root=project).summary.errors == 0


def test_integer_parts_error(project: Path) -> None:
    _setup(project, "parts:\n  - 1\n  - 2")
    assert any(
        i.rule_id == "P-PART-E001"
        for i in validate_project(root=project).issues
    )


def test_non_list_parts(project: Path) -> None:
    _setup(project, "parts: abc")
    assert any(
        i.rule_id == "P-PART-E001"
        for i in validate_project(root=project).issues
    )


def test_empty_part(project: Path) -> None:
    _setup(project, 'parts:\n  - " "\n  - b')
    assert any(
        i.rule_id == "P-PART-E002"
        for i in validate_project(root=project).issues
    )


def test_duplicate_parts(project: Path) -> None:
    _setup(project, "parts:\n  - a\n  - a")
    assert any(
        i.rule_id == "P-PART-E003"
        for i in validate_project(root=project).issues
    )


def test_single_part_error(project: Path) -> None:
    _setup(project, "parts:\n  - a")
    assert any(
        i.rule_id == "P-PART-E004"
        for i in validate_project(root=project).issues
    )
