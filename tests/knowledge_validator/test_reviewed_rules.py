from __future__ import annotations

from pathlib import Path

from tools.knowledge_validator.validator import validate_project

from .conftest import knowledge_md


def _ids(result) -> set[str]:
    return {i.rule_id for i in result.issues}


def test_reviewed_missing_aliases(project: Path) -> None:
    body = knowledge_md(
        kid="K0001",
        status="reviewed",
        extras="domain: 凸分析\nprerequisites: []\nrelated: []",
    )
    (project / "01_知识库" / "a.md").write_text(body, encoding="utf-8")
    r = validate_project(root=project)
    assert "K-FIELD-007" in _ids(r)


def test_aliases_not_list(project: Path) -> None:
    body = knowledge_md(kid="K0001", status="draft")
    body = body.replace("status: draft", "aliases: hello\nstatus: draft")
    (project / "01_知识库" / "a.md").write_text(body, encoding="utf-8")
    r = validate_project(root=project)
    assert "K-FIELD-001" in _ids(r)


def test_reviewed_missing_domain(project: Path) -> None:
    body = knowledge_md(
        kid="K0001",
        status="reviewed",
        aliases="",
        extras="prerequisites: []\nrelated: []",
    )
    (project / "01_知识库" / "a.md").write_text(body, encoding="utf-8")
    r = validate_project(root=project)
    assert "K-FIELD-008" in _ids(r)


def test_domain_not_string(project: Path) -> None:
    body = knowledge_md(kid="K0001", extras="domain: 1")
    # YAML may parse 1 as int
    (project / "01_知识库" / "a.md").write_text(body, encoding="utf-8")
    r = validate_project(root=project)
    assert "K-FIELD-004" in _ids(r)


def test_domain_empty(project: Path) -> None:
    body = knowledge_md(kid="K0001", extras='domain: "  "')
    (project / "01_知识库" / "a.md").write_text(body, encoding="utf-8")
    r = validate_project(root=project)
    assert "K-FIELD-004" in _ids(r)


def test_reviewed_missing_prerequisites(project: Path) -> None:
    body = knowledge_md(
        kid="K0001",
        status="reviewed",
        aliases="",
        extras="domain: 凸分析\nrelated: []",
    )
    (project / "01_知识库" / "a.md").write_text(body, encoding="utf-8")
    r = validate_project(root=project)
    assert "K-FIELD-009" in _ids(r)


def test_prerequisites_not_list(project: Path) -> None:
    body = knowledge_md(kid="K0001", extras="prerequisites: K0002")
    (project / "01_知识库" / "a.md").write_text(body, encoding="utf-8")
    r = validate_project(root=project)
    assert "K-FIELD-005" in _ids(r)


def test_reviewed_missing_related(project: Path) -> None:
    body = knowledge_md(
        kid="K0001",
        status="reviewed",
        aliases="",
        extras="domain: 凸分析\nprerequisites: []",
    )
    (project / "01_知识库" / "a.md").write_text(body, encoding="utf-8")
    r = validate_project(root=project)
    assert "K-FIELD-010" in _ids(r)


def test_related_not_list(project: Path) -> None:
    body = knowledge_md(kid="K0001", extras="related: K0002")
    (project / "01_知识库" / "a.md").write_text(body, encoding="utf-8")
    r = validate_project(root=project)
    assert "K-FIELD-006" in _ids(r)


def test_empty_arrays_legal_for_reviewed(project: Path) -> None:
    body = knowledge_md(
        kid="K0001",
        status="reviewed",
        aliases="",
        extras="domain: 凸分析\nprerequisites: []\nrelated: []",
    )
    (project / "01_知识库" / "a.md").write_text(body, encoding="utf-8")
    r = validate_project(root=project)
    assert r.summary.result == "PASS"
