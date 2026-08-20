from __future__ import annotations

from pathlib import Path

from tools.knowledge_validator.validator import validate_project

from .conftest import knowledge_md


def _write(project: Path, name: str, body: str) -> None:
    (project / "01_知识库" / name).write_text(body, encoding="utf-8")


def _ids(result) -> set[str]:
    return {i.rule_id for i in result.issues}


def _severities(result, rule_id: str) -> set[str]:
    return {i.severity.value for i in result.issues if i.rule_id == rule_id}


def test_valid_prerequisite(project: Path) -> None:
    _write(
        project,
        "k2.md",
        knowledge_md(
            kid="K0002",
            status="reviewed",
            aliases="",
            extras="domain: 凸分析\nprerequisites: []\nrelated: []",
        ),
    )
    _write(
        project,
        "k1.md",
        knowledge_md(
            kid="K0001",
            status="reviewed",
            aliases="",
            extras="domain: 凸分析\nprerequisites:\n  - K0002\nrelated: []",
        ),
    )
    r = validate_project(root=project)
    assert r.summary.result == "PASS"


def test_valid_related(project: Path) -> None:
    _write(
        project,
        "k2.md",
        knowledge_md(
            kid="K0002",
            status="reviewed",
            aliases="",
            extras="domain: 凸分析\nprerequisites: []\nrelated: []",
        ),
    )
    _write(
        project,
        "k1.md",
        knowledge_md(
            kid="K0001",
            status="reviewed",
            aliases="",
            extras="domain: 凸分析\nprerequisites: []\nrelated:\n  - K0002",
        ),
    )
    r = validate_project(root=project)
    assert r.summary.result == "PASS"


def test_missing_target(project: Path) -> None:
    _write(
        project,
        "k1.md",
        knowledge_md(kid="K0001", extras="prerequisites:\n  - K0099"),
    )
    r = validate_project(root=project)
    assert "K-REL-001" in _ids(r)


def test_self_prerequisite(project: Path) -> None:
    _write(
        project,
        "k1.md",
        knowledge_md(kid="K0001", extras="prerequisites:\n  - K0001"),
    )
    r = validate_project(root=project)
    assert "K-REL-002" in _ids(r)


def test_self_related(project: Path) -> None:
    _write(project, "k1.md", knowledge_md(kid="K0001", extras="related:\n  - K0001"))
    r = validate_project(root=project)
    assert "K-REL-002" in _ids(r)


def test_duplicate_prerequisite(project: Path) -> None:
    _write(
        project,
        "k2.md",
        knowledge_md(kid="K0002"),
    )
    _write(
        project,
        "k1.md",
        knowledge_md(
            kid="K0001",
            extras="prerequisites:\n  - K0002\n  - K0002",
        ),
    )
    r = validate_project(root=project)
    assert "K-REL-003" in _ids(r)


def test_duplicate_related(project: Path) -> None:
    _write(project, "k2.md", knowledge_md(kid="K0002"))
    _write(
        project,
        "k1.md",
        knowledge_md(kid="K0001", extras="related:\n  - K0002\n  - K0002"),
    )
    r = validate_project(root=project)
    assert "K-REL-003" in _ids(r)


def test_overlap(project: Path) -> None:
    _write(project, "k2.md", knowledge_md(kid="K0002"))
    _write(
        project,
        "k1.md",
        knowledge_md(
            kid="K0001",
            extras="prerequisites:\n  - K0002\nrelated:\n  - K0002",
        ),
    )
    r = validate_project(root=project)
    assert "K-REL-004" in _ids(r)


def test_invalid_relation_id(project: Path) -> None:
    _write(project, "k1.md", knowledge_md(kid="K0001", extras="prerequisites:\n  - ABC"))
    r = validate_project(root=project)
    assert "K-REL-007" in _ids(r)


def test_k0000_target(project: Path) -> None:
    _write(project, "k1.md", knowledge_md(kid="K0001", extras="prerequisites:\n  - K0000"))
    r = validate_project(root=project)
    assert "K-REL-006" in _ids(r)


def test_reviewed_to_draft(project: Path) -> None:
    _write(project, "k2.md", knowledge_md(kid="K0002", status="draft"))
    _write(
        project,
        "k1.md",
        knowledge_md(
            kid="K0001",
            status="reviewed",
            aliases="",
            extras="domain: 凸分析\nprerequisites:\n  - K0002\nrelated: []",
        ),
    )
    r = validate_project(root=project)
    assert "K-REL-005" in _ids(r)


def test_draft_to_reviewed(project: Path) -> None:
    _write(
        project,
        "k2.md",
        knowledge_md(
            kid="K0002",
            status="reviewed",
            aliases="",
            extras="domain: 凸分析\nprerequisites: []\nrelated: []",
        ),
    )
    _write(
        project,
        "k1.md",
        knowledge_md(kid="K0001", status="draft", extras="prerequisites:\n  - K0002"),
    )
    r = validate_project(root=project)
    assert r.summary.result == "PASS"
    assert "K-REL-W001" not in _ids(r)


def test_draft_to_draft_warning(project: Path) -> None:
    _write(project, "k2.md", knowledge_md(kid="K0002", status="draft"))
    _write(
        project,
        "k1.md",
        knowledge_md(kid="K0001", status="draft", extras="prerequisites:\n  - K0002"),
    )
    r = validate_project(root=project)
    assert "K-REL-W001" in _ids(r)
    assert "WARNING" in _severities(r, "K-REL-W001")
    assert r.summary.result == "PASS"
