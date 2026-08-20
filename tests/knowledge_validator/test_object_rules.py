from __future__ import annotations

from pathlib import Path

from tools.knowledge_validator.validator import validate_project

from .conftest import knowledge_md


def _run(project: Path, body: str, name: str = "obj.md"):
    path = project / "01_知识库" / name
    path.write_text(body, encoding="utf-8")
    return validate_project(root=project)


def _rule_ids(result) -> set[str]:
    return {i.rule_id for i in result.issues}


def test_valid_draft(project: Path) -> None:
    r = _run(project, knowledge_md(kid="K0001", status="draft"))
    assert r.summary.result == "PASS"
    assert r.summary.errors == 0


def test_valid_reviewed(project: Path) -> None:
    body = knowledge_md(
        kid="K0001",
        status="reviewed",
        aliases="",
        extras="domain: 凸分析\nprerequisites: []\nrelated: []",
    )
    r = _run(project, body)
    assert r.summary.result == "PASS"


def test_invalid_schema_version(project: Path) -> None:
    body = knowledge_md(kid="K0001").replace("schema_version: 1", 'schema_version: "1"')
    r = _run(project, body)
    assert "K-BASE-002" in _rule_ids(r)


def test_missing_id(project: Path) -> None:
    body = knowledge_md(kid="K0001").replace("id: K0001\n", "")
    # still candidate via type knowledge
    r = _run(project, body)
    assert "K-BASE-012" in _rule_ids(r)


def test_invalid_id(project: Path) -> None:
    r = _run(project, knowledge_md(kid="K1"))
    assert "K-BASE-010" in _rule_ids(r)


def test_real_k0000(project: Path) -> None:
    r = _run(project, knowledge_md(kid="K0000"), name="real_k0000.md")
    assert "K-BASE-011" in _rule_ids(r)


def test_missing_type(project: Path) -> None:
    body = knowledge_md(kid="K0005").replace("type: knowledge\n", "")
    r = _run(project, body)
    assert "K-BASE-020" in _rule_ids(r)


def test_invalid_type(project: Path) -> None:
    body = knowledge_md(kid="K0005").replace("type: knowledge", "type: theorem")
    r = _run(project, body)
    assert "K-BASE-021" in _rule_ids(r)


def test_empty_title(project: Path) -> None:
    body = knowledge_md(kid="K0005", title="   ")
    # knowledge_md still writes title:    
    r = _run(project, body.replace("title:    ", 'title: "   "'))
    assert "K-BASE-030" in _rule_ids(r)


def test_invalid_status(project: Path) -> None:
    body = knowledge_md(kid="K0005").replace("status: draft", "status: Reviewed")
    r = _run(project, body)
    assert "K-STATE-001" in _rule_ids(r)


def test_invalid_created(project: Path) -> None:
    # Keep as quoted string so object-level date rules run (not YAML timestamp ctor).
    body = knowledge_md(kid="K0005").replace(
        "created: 2026-08-19", 'created: "2026-02-30"'
    )
    r = _run(project, body)
    assert "K-DATE-001" in _rule_ids(r)


def test_invalid_updated(project: Path) -> None:
    body = knowledge_md(kid="K0005").replace("updated: 2026-08-19", "updated: not-a-date")
    r = _run(project, body)
    assert "K-DATE-002" in _rule_ids(r)


def test_updated_before_created(project: Path) -> None:
    body = knowledge_md(kid="K0005").replace(
        "created: 2026-08-19\nupdated: 2026-08-19",
        "created: 2026-08-19\nupdated: 2026-08-01",
    )
    r = _run(project, body)
    assert "K-DATE-003" in _rule_ids(r)
