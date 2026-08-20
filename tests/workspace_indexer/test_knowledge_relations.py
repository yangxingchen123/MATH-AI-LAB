"""Workspace integration tests for Formal Knowledge Relations (P5)."""

from __future__ import annotations

import hashlib
from pathlib import Path

from tools.attempt_validator import validate_project as validate_attempt_project
from tools.knowledge_validator import validate_project as validate_knowledge_project
from tools.knowledge_relations.models import RelationEdge
from tools.method_validator import validate_project as validate_method_project
from tools.problem_validator import validate_project as validate_problem_project
from tools.workspace_indexer.builder import build_workspace_snapshot
from tools.workspace_indexer.constants import INDEX_DIR_RELATIVE, MANAGED_FILES
from tools.workspace_indexer.renderer import render_all, render_knowledge_relations
from tools.workspace_indexer.service import check_index, sync_index

from tests.knowledge_indexer.conftest import write_knowledge
from tests.workspace_indexer.conftest import write_problem


def _validated(project: Path):
    kr = validate_knowledge_project(root=project)
    pr = validate_problem_project(root=project, knowledge_result=kr)
    ar = validate_attempt_project(root=project, problem_result=pr)
    mr = validate_method_project(root=project, knowledge_result=kr)
    return kr, pr, ar, mr


def test_generated_knowledge_relations_file(project: Path) -> None:
    kr, pr, ar, mr = _validated(project)
    snap = build_workspace_snapshot(
        project,
        knowledge_result=kr,
        problem_result=pr,
        attempt_result=ar,
        method_result=mr,
    )
    rendered = render_all(snap)
    assert "知识关系.md" in rendered
    assert "Formal Relation Derived View" in rendered["知识关系.md"]
    assert "K0001" in rendered["知识关系.md"]


def test_relation_added_marks_stale(project: Path) -> None:
    kr, pr, ar, mr = _validated(project)
    snap = build_workspace_snapshot(
        project,
        knowledge_result=kr,
        problem_result=pr,
        attempt_result=ar,
        method_result=mr,
    )
    index_dir = project / INDEX_DIR_RELATIVE
    index_dir.mkdir(parents=True, exist_ok=True)
    (index_dir / "知识关系.md").write_text("OLD", encoding="utf-8")
    for name, content in render_all(snap).items():
        if name != "知识关系.md":
            (index_dir / name).write_text(content, encoding="utf-8")

    op = check_index(root=project)
    assert op.result.value in {"STALE", "MISSING"}


def test_relation_removed_marks_stale(project: Path) -> None:
    write_problem(
        project,
        "02_题目库/已解决/P0001_x.md",
        pid="P0001",
        title="A",
        status="reviewed",
        extras="knowledge:\n  - K0001\n",
    )
    kr, pr, ar, mr = _validated(project)
    snap = build_workspace_snapshot(
        project,
        knowledge_result=kr,
        problem_result=pr,
        attempt_result=ar,
        method_result=mr,
    )
    index_dir = project / INDEX_DIR_RELATIVE
    index_dir.mkdir(parents=True, exist_ok=True)
    for name, content in render_all(snap).items():
        (index_dir / name).write_text(content, encoding="utf-8")

    write_problem(
        project,
        "02_题目库/已解决/P0001_x.md",
        pid="P0001",
        title="A",
        status="reviewed",
        extras="knowledge: []\n",
    )
    op = check_index(root=project)
    assert op.result.value == "STALE"


def test_title_change_marks_stale(project: Path) -> None:
    kr, pr, ar, mr = _validated(project)
    snap = build_workspace_snapshot(
        project,
        knowledge_result=kr,
        problem_result=pr,
        attempt_result=ar,
        method_result=mr,
    )
    index_dir = project / INDEX_DIR_RELATIVE
    index_dir.mkdir(parents=True, exist_ok=True)
    for name, content in render_all(snap).items():
        (index_dir / name).write_text(content, encoding="utf-8")

    write_knowledge(
        project,
        "01_知识库/数学变换/勒让德变换.md",
        kid="K0001",
        title="新标题",
        status="reviewed",
        aliases="Legendre transform",
        extras="domain: 凸分析\nprerequisites:\n  - K0002\nrelated: []",
    )
    op = check_index(root=project)
    assert op.result.value == "STALE"


def test_body_only_change_no_relation_diff(project: Path) -> None:
    kr, pr, ar, mr = _validated(project)
    snap_before = build_workspace_snapshot(
        project,
        knowledge_result=kr,
        problem_result=pr,
        attempt_result=ar,
        method_result=mr,
    )
    rel_before = render_knowledge_relations(snap_before)

    write_problem(project, "02_题目库/研究中/P0002_x.md", pid="P0002", title="Body test")
    path = project / "02_题目库/研究中/P0002_x.md"
    path.write_text(path.read_text(encoding="utf-8") + "\n\nBody mention K9999\n", encoding="utf-8")

    kr2, pr2, ar2, mr2 = _validated(project)
    snap_after = build_workspace_snapshot(
        project,
        knowledge_result=kr2,
        problem_result=pr2,
        attempt_result=ar2,
        method_result=mr2,
    )
    rel_after = render_knowledge_relations(snap_after)
    assert rel_before == rel_after


def test_attempt_only_change_no_relation_diff(project: Path) -> None:
    from tests.workspace_indexer.conftest import write_attempt

    write_problem(
        project,
        "02_题目库/研究中/P0002_x.md",
        pid="P0002",
        extras="parts:\n  - a\n  - b\n",
    )
    kr, pr, ar, mr = _validated(project)
    snap_before = build_workspace_snapshot(
        project,
        knowledge_result=kr,
        problem_result=pr,
        attempt_result=ar,
        method_result=mr,
    )
    rel_before = render_knowledge_relations(snap_before)

    write_attempt(project, "11_学习证据/尝试记录/A000099.md", aid="A000099", outcome="correct")
    kr2, pr2, ar2, mr2 = _validated(project)
    snap_after = build_workspace_snapshot(
        project,
        knowledge_result=kr2,
        problem_result=pr2,
        attempt_result=ar2,
        method_result=mr2,
    )
    rel_after = render_knowledge_relations(snap_after)
    assert rel_before == rel_after


def test_repeated_sync_zero_writes_when_current(project: Path) -> None:
    kr, pr, ar, mr = _validated(project)
    snap = build_workspace_snapshot(
        project,
        knowledge_result=kr,
        problem_result=pr,
        attempt_result=ar,
        method_result=mr,
    )
    index_dir = project / INDEX_DIR_RELATIVE
    index_dir.mkdir(parents=True, exist_ok=True)
    for name, content in render_all(snap).items():
        (index_dir / name).write_text(content, encoding="utf-8")

    op = sync_index(root=project)
    assert op.result.value == "UP_TO_DATE"


def test_no_attempt_evidence_in_knowledge_relations(project: Path) -> None:
    kr, pr, ar, mr = _validated(project)
    snap = build_workspace_snapshot(
        project,
        knowledge_result=kr,
        problem_result=pr,
        attempt_result=ar,
        method_result=mr,
    )
    text = render_knowledge_relations(snap)
    assert "mastery" not in text.lower()
    assert "correct" not in text.lower() or "K0001" in text
    assert "associated attempt" not in text.lower()


def test_formal_edge_from_problem_knowledge(project: Path) -> None:
    write_problem(
        project,
        "02_题目库/已解决/P0001_x.md",
        pid="P0001",
        title="A",
        status="reviewed",
        extras="knowledge:\n  - K0001\n  - K0002\n",
    )
    kr, pr, ar, mr = _validated(project)
    snap = build_workspace_snapshot(
        project,
        knowledge_result=kr,
        problem_result=pr,
        attempt_result=ar,
        method_result=mr,
    )
    edges = snap.knowledge_relations.edges if snap.knowledge_relations else ()
    assert RelationEdge("P0001", "knowledge", "K0001") in edges
    assert RelationEdge("P0001", "knowledge", "K0002") in edges


def test_invalid_upstream_zero_writes(project: Path) -> None:
    index_dir = project / INDEX_DIR_RELATIVE
    index_dir.mkdir(parents=True, exist_ok=True)
    hashes_before = {}
    for name in MANAGED_FILES:
        path = index_dir / name
        path.write_text(f"KEEP {name}", encoding="utf-8")
        hashes_before[name] = hashlib.sha256(path.read_bytes()).hexdigest()

    write_problem(project, "02_题目库/研究中/P0001_a.md", pid="P0001")
    write_problem(project, "02_题目库/已解决/P0001_b.md", pid="P0001")

    op = sync_index(root=project)
    assert op.result.value == "FAIL"
    for name, digest in hashes_before.items():
        assert hashlib.sha256((index_dir / name).read_bytes()).hexdigest() == digest


def test_relation_builder_internal_failure_zero_writes(project: Path, monkeypatch) -> None:
    """Validated upstream + relation builder exception must abort with 0 writes."""
    from tools.knowledge_relations.builder import KnowledgeRelationBuildError

    first = sync_index(root=project)
    assert first.result.value in {"BUILT", "UP_TO_DATE"}
    index_dir = project / INDEX_DIR_RELATIVE
    hashes_before = {
        name: hashlib.sha256((index_dir / name).read_bytes()).hexdigest()
        for name in MANAGED_FILES
        if (index_dir / name).is_file()
    }
    assert hashes_before

    def _boom(*_args, **_kwargs):
        raise KnowledgeRelationBuildError("injected relation builder failure")

    monkeypatch.setattr(
        "tools.workspace_indexer.builder.build_knowledge_relations",
        _boom,
    )

    op = sync_index(root=project)
    assert op.result.value == "FAIL"
    assert any(
        "relation" in issue.message.lower() or issue.rule_id.startswith("WI-DERIVE")
        for issue in op.issues
    )
    for name, digest in hashes_before.items():
        assert hashlib.sha256((index_dir / name).read_bytes()).hexdigest() == digest
