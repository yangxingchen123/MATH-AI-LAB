"""Base field validation tests."""

from __future__ import annotations

from pathlib import Path

from tools.method_validator.validator import validate_project
from tests.method_validator.conftest import knowledge_md, method_md


def _k(project: Path, kid: str = "K0001") -> None:
    (project / "01_知识库" / f"{kid}.md").write_text(
        knowledge_md(kid=kid), encoding="utf-8"
    )


def _m(project: Path, name: str, content: str) -> None:
    (project / "12_方法库" / name).write_text(content, encoding="utf-8")


def test_missing_required_field(project: Path) -> None:
    _k(project)
    _m(
        project,
        "M0001.md",
        "---\nschema_version: 1\nid: M0001\ntype: method\nstatus: draft\n---\n",
    )
    result = validate_project(root=project)
    assert any(i.rule_id == "M-BASE-E030" for i in result.issues)


def test_unknown_field_error(project: Path) -> None:
    _k(project)
    _m(project, "M0001.md", method_md(extras="created: 2026-08-19"))
    result = validate_project(root=project)
    assert any(i.rule_id == "M-FIELD-E001" for i in result.issues)


def test_invalid_method_id(project: Path) -> None:
    _k(project)
    _m(project, "M0001.md", method_md(mid="BAD"))
    result = validate_project(root=project)
    assert any(i.rule_id == "M-BASE-E010" for i in result.issues)


def test_m0000_sentinel(project: Path) -> None:
    _k(project)
    _m(project, "M0000.md", method_md(mid="M0000"))
    result = validate_project(root=project)
    assert any(i.rule_id == "M-BASE-E011" for i in result.issues)


def test_wrong_type(project: Path) -> None:
    _k(project)
    text = method_md().replace("type: method", "type: procedure")
    _m(project, "M0001.md", text)
    result = validate_project(root=project)
    assert any(i.rule_id == "M-BASE-E021" for i in result.issues)


def test_empty_title(project: Path) -> None:
    _k(project)
    _m(project, "M0001.md", method_md(title='""'))
    result = validate_project(root=project)
    assert any(i.rule_id == "M-BASE-E030" for i in result.issues)


def test_whitespace_title(project: Path) -> None:
    _k(project)
    _m(project, "M0001.md", method_md(title='"   "'))
    result = validate_project(root=project)
    assert any(i.rule_id == "M-BASE-E030" for i in result.issues)


def test_invalid_status(project: Path) -> None:
    _k(project)
    _m(project, "M0001.md", method_md(status="candidate"))
    result = validate_project(root=project)
    assert any(i.rule_id == "M-STATE-E001" for i in result.issues)


def test_draft_status_passes(project: Path) -> None:
    _k(project)
    _m(project, "M0001.md", method_md(status="draft"))
    result = validate_project(root=project)
    assert result.summary.errors == 0


def test_reviewed_status_passes(project: Path) -> None:
    _k(project)
    _m(project, "M0001.md", method_md(status="reviewed"))
    result = validate_project(root=project)
    assert result.summary.errors == 0


def test_archived_status_passes(project: Path) -> None:
    _k(project)
    _m(project, "M0001.md", method_md(status="archived"))
    result = validate_project(root=project)
    assert result.summary.errors == 0


def test_schema_version_not_string(project: Path) -> None:
    _k(project)
    text = method_md().replace("schema_version: 1", 'schema_version: "1"')
    _m(project, "M0001.md", text)
    result = validate_project(root=project)
    assert any(i.rule_id == "M-BASE-E002" for i in result.issues)
