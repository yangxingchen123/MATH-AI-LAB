"""Base field validation tests."""

from __future__ import annotations

from pathlib import Path

from tools.problem_validator.validator import validate_project
from tests.problem_validator.conftest import knowledge_md, problem_md, write_project


def _setup_valid_k(project: Path) -> None:
    kb = project / "01_知识库"
    (kb / "K0001.md").write_text(knowledge_md(kid="K0001"), encoding="utf-8")


def test_valid_draft(project: Path) -> None:
    _setup_valid_k(project)
    (project / "02_题目库" / "P0001.md").write_text(problem_md(), encoding="utf-8")
    result = validate_project(root=project)
    assert result.summary.errors == 0


def test_valid_reviewed(project: Path) -> None:
    _setup_valid_k(project)
    (project / "02_题目库" / "P0001.md").write_text(
        problem_md(status="reviewed", extras="knowledge: []"), encoding="utf-8"
    )
    result = validate_project(root=project)
    assert result.summary.errors == 0


def test_missing_schema_version(project: Path) -> None:
    _setup_valid_k(project)
    text = problem_md().replace("schema_version: 1\n", "")
    (project / "02_题目库" / "P0001.md").write_text(text, encoding="utf-8")
    result = validate_project(root=project)
    assert any(i.rule_id == "P-BASE-E001" for i in result.issues)


def test_schema_version_string(project: Path) -> None:
    _setup_valid_k(project)
    text = problem_md().replace("schema_version: 1", 'schema_version: "1"')
    (project / "02_题目库" / "P0001.md").write_text(text, encoding="utf-8")
    result = validate_project(root=project)
    assert any(i.rule_id == "P-BASE-E002" for i in result.issues)


def test_schema_version_wrong_int(project: Path) -> None:
    _setup_valid_k(project)
    text = problem_md().replace("schema_version: 1", "schema_version: 2")
    (project / "02_题目库" / "P0001.md").write_text(text, encoding="utf-8")
    result = validate_project(root=project)
    assert any(i.rule_id == "P-BASE-E002" for i in result.issues)


def test_invalid_pid(project: Path) -> None:
    _setup_valid_k(project)
    text = problem_md(pid="P001")
    (project / "02_题目库" / "P0001.md").write_text(text, encoding="utf-8")
    result = validate_project(root=project)
    assert any(i.rule_id == "P-BASE-E010" for i in result.issues)


def test_p0000_forbidden(project: Path) -> None:
    _setup_valid_k(project)
    (project / "02_题目库" / "P0000.md").write_text(problem_md(pid="P0000"), encoding="utf-8")
    result = validate_project(root=project)
    assert any(i.rule_id == "P-BASE-E011" for i in result.issues)


def test_wrong_type(project: Path) -> None:
    _setup_valid_k(project)
    text = problem_md().replace("type: problem", "type: knowledge")
    (project / "02_题目库" / "P0001.md").write_text(text, encoding="utf-8")
    result = validate_project(root=project)
    assert any(i.rule_id == "P-BASE-E021" for i in result.issues)


def test_empty_title(project: Path) -> None:
    _setup_valid_k(project)
    text = problem_md(title="   ")
    (project / "02_题目库" / "P0001.md").write_text(text, encoding="utf-8")
    result = validate_project(root=project)
    assert any(i.rule_id == "P-BASE-E030" for i in result.issues)


def test_invalid_status(project: Path) -> None:
    _setup_valid_k(project)
    text = problem_md(status="pending")
    (project / "02_题目库" / "P0001.md").write_text(text, encoding="utf-8")
    result = validate_project(root=project)
    assert any(i.rule_id == "P-STATE-E001" for i in result.issues)


def test_invalid_date(project: Path) -> None:
    _setup_valid_k(project)
    text = problem_md().replace("created: 2026-08-19", "created: not-a-date")
    (project / "02_题目库" / "P0001.md").write_text(text, encoding="utf-8")
    result = validate_project(root=project)
    assert any(i.rule_id == "P-DATE-E001" for i in result.issues)


def test_updated_before_created(project: Path) -> None:
    _setup_valid_k(project)
    text = problem_md().replace("updated: 2026-08-19", "updated: 2026-08-18")
    (project / "02_题目库" / "P0001.md").write_text(text, encoding="utf-8")
    result = validate_project(root=project)
    assert any(i.rule_id == "P-DATE-E003" for i in result.issues)


def test_unknown_field_warning(project: Path) -> None:
    _setup_valid_k(project)
    (project / "02_题目库" / "P0001.md").write_text(
        problem_md(extras="foo: bar"), encoding="utf-8"
    )
    result = validate_project(root=project)
    assert any(i.rule_id == "P-FIELD-W001" for i in result.issues)
    assert result.summary.errors == 0
