from __future__ import annotations

from pathlib import Path

from tools.knowledge_validator.validator import validate_project

from .conftest import knowledge_md


def _write(project: Path, name: str, body: str) -> None:
    (project / "01_知识库" / name).write_text(body, encoding="utf-8")


def test_empty_graph_pass(project: Path) -> None:
    _write(project, "k1.md", knowledge_md(kid="K0001"))
    r = validate_project(root=project)
    assert r.summary.result == "PASS"
    assert not any(i.rule_id == "K-GRAPH-001" for i in r.issues)


def test_simple_edge_pass(project: Path) -> None:
    _write(project, "k2.md", knowledge_md(kid="K0002"))
    _write(project, "k1.md", knowledge_md(kid="K0001", extras="prerequisites:\n  - K0002"))
    r = validate_project(root=project)
    assert r.summary.result == "PASS"


def test_two_cycle_fail(project: Path) -> None:
    _write(project, "k1.md", knowledge_md(kid="K0001", extras="prerequisites:\n  - K0002"))
    _write(project, "k2.md", knowledge_md(kid="K0002", extras="prerequisites:\n  - K0001"))
    r = validate_project(root=project)
    cycles = [i for i in r.issues if i.rule_id == "K-GRAPH-001"]
    assert cycles
    assert "->" in cycles[0].message


def test_three_cycle_fail(project: Path) -> None:
    _write(project, "k1.md", knowledge_md(kid="K0001", extras="prerequisites:\n  - K0002"))
    _write(project, "k2.md", knowledge_md(kid="K0002", extras="prerequisites:\n  - K0003"))
    _write(project, "k3.md", knowledge_md(kid="K0003", extras="prerequisites:\n  - K0001"))
    r = validate_project(root=project)
    cycles = [i for i in r.issues if i.rule_id == "K-GRAPH-001"]
    assert cycles
    path = cycles[0].details["cycle_path"]
    assert "K0001" in path and "K0002" in path and "K0003" in path


def test_related_cycle_allowed(project: Path) -> None:
    _write(project, "k1.md", knowledge_md(kid="K0001", extras="related:\n  - K0002"))
    _write(project, "k2.md", knowledge_md(kid="K0002", extras="related:\n  - K0003"))
    _write(project, "k3.md", knowledge_md(kid="K0003", extras="related:\n  - K0001"))
    r = validate_project(root=project)
    assert not any(i.rule_id == "K-GRAPH-001" for i in r.issues)
    assert r.summary.result == "PASS"


def test_cycle_report_full_path(project: Path) -> None:
    _write(project, "k1.md", knowledge_md(kid="K0001", extras="prerequisites:\n  - K0002"))
    _write(project, "k2.md", knowledge_md(kid="K0002", extras="prerequisites:\n  - K0001"))
    r = validate_project(root=project)
    issue = next(i for i in r.issues if i.rule_id == "K-GRAPH-001")
    assert issue.details["cycle"][0] == issue.details["cycle"][-1]
