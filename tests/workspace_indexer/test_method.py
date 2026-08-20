"""Tests for Workspace Indexer Method integration (v1.2)."""

from __future__ import annotations

import hashlib
from pathlib import Path
from unittest.mock import patch

from tools.attempt_validator import validate_project as validate_attempt_project
from tools.knowledge_validator import validate_project as validate_knowledge_project
from tools.method_validator import validate_project as validate_method_project
from tools.problem_validator import validate_project as validate_problem_project
from tools.workspace_indexer.builder import build_workspace_snapshot
from tools.workspace_indexer.constants import INDEX_DIR_RELATIVE, MANAGED_FILES
from tools.workspace_indexer.renderer import render_all, render_method_index
from tools.workspace_indexer.service import check_index, rebuild_index, sync_index

from .conftest import write_attempt, write_method, write_problem


def _validated(project: Path):
    kr = validate_knowledge_project(root=project)
    pr = validate_problem_project(root=project, knowledge_result=kr)
    ar = validate_attempt_project(root=project, problem_result=pr)
    mr = validate_method_project(root=project, knowledge_result=kr)
    return kr, pr, ar, mr


def test_snapshot_from_validated_method_registry(project: Path) -> None:
    write_method(
        project,
        "12_方法库/M0001.md",
        mid="M0001",
        extras="knowledge:\n  - K0001",
    )
    write_method(project, "12_方法库/M0002.md", mid="M0002", title="Second")

    kr, pr, ar, mr = _validated(project)
    assert mr.summary.errors == 0
    snap = build_workspace_snapshot(
        project,
        knowledge_result=kr,
        problem_result=pr,
        attempt_result=ar,
        method_result=mr,
    )
    ids = [r.object_id for r in snap.method_rows]
    assert ids == ["M0001", "M0002"]
    m1 = snap.method_rows[0]
    assert m1.title == "Test Method"
    assert m1.status == "draft"
    assert m1.knowledge == "K0001"
    assert m1.source_path == "12_方法库/M0001.md"
    m2 = snap.method_rows[1]
    assert m2.knowledge == "—"


def test_builder_does_not_scan_method_source(project: Path) -> None:
    write_method(project, "12_方法库/M0001.md", mid="M0001")
    kr, pr, ar, mr = _validated(project)
    with patch("tools.method_validator.parser.parse_markdown_file") as parse_md:
        build_workspace_snapshot(
            project,
            knowledge_result=kr,
            problem_result=pr,
            attempt_result=ar,
            method_result=mr,
        )
        parse_md.assert_not_called()


def test_method_index_sorted_and_omission(project: Path) -> None:
    write_method(project, "12_方法库/z.md", mid="M0002", title="B")
    write_method(
        project,
        "12_方法库/a.md",
        mid="M0001",
        title="A",
        extras="knowledge:\n  - K0001",
    )
    kr, pr, ar, mr = _validated(project)
    snap = build_workspace_snapshot(
        project,
        knowledge_result=kr,
        problem_result=pr,
        attempt_result=ar,
        method_result=mr,
    )
    text = render_method_index(snap)
    assert text.index("M0001") < text.index("M0002")
    assert "K0001" in text
    assert "[]" not in text
    assert "unknown" not in text.lower()


def test_method_status_counts_derived(project: Path) -> None:
    write_method(project, "12_方法库/M0001.md", mid="M0001", status="draft")
    write_method(project, "12_方法库/M0002.md", mid="M0002", status="reviewed")
    write_method(project, "12_方法库/M0003.md", mid="M0003", status="archived")
    kr, pr, ar, mr = _validated(project)
    snap = build_workspace_snapshot(
        project,
        knowledge_result=kr,
        problem_result=pr,
        attempt_result=ar,
        method_result=mr,
    )
    assert len(snap.method_rows) == 3
    assert snap.method_status_counts["draft"] == 1
    assert snap.method_status_counts["reviewed"] == 1
    assert snap.method_status_counts["archived"] == 1
    stats = render_all(snap)["项目统计.md"]
    assert "## Methods" in stats
    assert "total: 3" in stats
    assert "success rate" not in stats.lower()
    assert "mastery" not in stats.lower()


def test_knowledge_index_has_no_methods_column(project: Path) -> None:
    write_method(
        project,
        "12_方法库/M0001.md",
        extras="knowledge:\n  - K0001",
    )
    kr, pr, ar, mr = _validated(project)
    snap = build_workspace_snapshot(
        project,
        knowledge_result=kr,
        problem_result=pr,
        attempt_result=ar,
        method_result=mr,
    )
    text = render_all(snap)["知识索引.md"]
    assert "Method" not in text
    header = [line for line in text.splitlines() if line.startswith("| ID |")][0]
    assert "Methods" not in header


def test_problem_index_has_no_methods_column(project: Path) -> None:
    write_problem(project, "02_题目库/研究中/P0002_x.md", pid="P0002")
    write_method(project, "12_方法库/M0001.md")
    kr, pr, ar, mr = _validated(project)
    snap = build_workspace_snapshot(
        project,
        knowledge_result=kr,
        problem_result=pr,
        attempt_result=ar,
        method_result=mr,
    )
    text = render_all(snap)["题目索引.md"]
    header = [line for line in text.splitlines() if line.startswith("| ID |")][0]
    assert "Method" not in header


def test_evidence_index_has_no_method_column(project: Path) -> None:
    write_problem(project, "02_题目库/研究中/P0002_x.md", pid="P0002", extras="parts:\n  - a\n  - b\n")
    write_attempt(project, "11_学习证据/尝试记录/A000001.md", part="a")
    write_method(project, "12_方法库/M0001.md")
    kr, pr, ar, mr = _validated(project)
    snap = build_workspace_snapshot(
        project,
        knowledge_result=kr,
        problem_result=pr,
        attempt_result=ar,
        method_result=mr,
    )
    text = render_all(snap)["证据索引.md"]
    assert "Method" not in text


def test_invalid_method_aborts_sync_zero_writes(project: Path) -> None:
    index_dir = project / INDEX_DIR_RELATIVE
    index_dir.mkdir(parents=True)
    hashes_before = {}
    for name in MANAGED_FILES:
        (index_dir / name).write_text(f"KEEP {name}", encoding="utf-8")
        hashes_before[name] = hashlib.sha256((index_dir / name).read_bytes()).hexdigest()

    write_method(project, "12_方法库/M0001.md", extras="created: 2026-08-19")
    op = sync_index(root=project)
    assert op.result.value == "FAIL"
    assert op.method_validator_result == "FAIL"
    for name, digest in hashes_before.items():
        assert hashlib.sha256((index_dir / name).read_bytes()).hexdigest() == digest


def test_invalid_knowledge_aborts_zero_writes(project: Path) -> None:
    index_dir = project / INDEX_DIR_RELATIVE
    index_dir.mkdir(parents=True)
    sentinel = index_dir / "项目统计.md"
    sentinel.write_text("KEEP ME", encoding="utf-8")
    (project / "01_知识库" / "bad.md").write_text(
        "---\nschema_version: 1\nid: K0001\ntype: knowledge\ntitle: dup\nstatus: draft\n"
        "created: 2026-08-19\nupdated: 2026-08-19\n---\n",
        encoding="utf-8",
    )
    op = sync_index(root=project)
    assert op.result.value == "FAIL"
    assert sentinel.read_text(encoding="utf-8") == "KEEP ME"


def test_method_title_change_stale_then_sync(project: Path) -> None:
    write_method(project, "12_方法库/M0001.md", title="Old")
    rebuild_index(root=project)
    write_method(project, "12_方法库/M0001.md", title="New")
    check = check_index(root=project)
    assert check.result.value == "STALE"
    op = sync_index(root=project)
    assert op.result.value == "BUILT"
    text = (project / INDEX_DIR_RELATIVE / "方法索引.md").read_text(encoding="utf-8")
    assert "New" in text
    assert check_index(root=project).result.value == "CURRENT"


def test_method_status_change_stale(project: Path) -> None:
    write_method(project, "12_方法库/M0001.md", status="draft")
    rebuild_index(root=project)
    write_method(project, "12_方法库/M0001.md", status="reviewed")
    assert check_index(root=project).result.value == "STALE"
    sync_index(root=project)
    stats = (project / INDEX_DIR_RELATIVE / "项目统计.md").read_text(encoding="utf-8")
    assert "reviewed:" in stats


def test_method_knowledge_change_stale(project: Path) -> None:
    write_method(project, "12_方法库/M0001.md")
    rebuild_index(root=project)
    write_method(project, "12_方法库/M0001.md", extras="knowledge:\n  - K0001")
    assert check_index(root=project).result.value == "STALE"
    sync_index(root=project)
    text = (project / INDEX_DIR_RELATIVE / "方法索引.md").read_text(encoding="utf-8")
    assert "K0001" in text


def test_method_body_only_no_generated_diff(project: Path) -> None:
    path = write_method(project, "12_方法库/M0001.md", body="original body\n")
    kr, pr, ar, mr = _validated(project)
    snap1 = build_workspace_snapshot(
        project,
        knowledge_result=kr,
        problem_result=pr,
        attempt_result=ar,
        method_result=mr,
    )
    rendered1 = render_all(snap1)
    path.write_text(
        path.read_text(encoding="utf-8").replace("original body", "different reasoning"),
        encoding="utf-8",
    )
    kr2, pr2, ar2, mr2 = _validated(project)
    snap2 = build_workspace_snapshot(
        project,
        knowledge_result=kr2,
        problem_result=pr2,
        attempt_result=ar2,
        method_result=mr2,
    )
    assert render_all(snap2) == rendered1


def test_repeated_sync_no_op(project: Path) -> None:
    write_method(project, "12_方法库/M0001.md")
    rebuild_index(root=project)
    index_dir = project / INDEX_DIR_RELATIVE
    before = {
        name: hashlib.sha256((index_dir / name).read_bytes()).hexdigest()
        for name in MANAGED_FILES
        if (index_dir / name).is_file()
    }
    op = sync_index(root=project)
    assert op.result.value == "UP_TO_DATE"
    after = {
        name: hashlib.sha256((index_dir / name).read_bytes()).hexdigest()
        for name in MANAGED_FILES
        if (index_dir / name).is_file()
    }
    assert before == after


def test_deterministic_method_render(project: Path) -> None:
    write_method(project, "12_方法库/M0002.md", mid="M0002")
    write_method(project, "12_方法库/M0001.md", mid="M0001")
    kr, pr, ar, mr = _validated(project)
    snap = build_workspace_snapshot(
        project,
        knowledge_result=kr,
        problem_result=pr,
        attempt_result=ar,
        method_result=mr,
    )
    assert render_all(snap) == render_all(snap)


def test_draft_method_in_index(project: Path) -> None:
    write_method(project, "12_方法库/M0001.md", status="draft")
    kr, pr, ar, mr = _validated(project)
    snap = build_workspace_snapshot(
        project,
        knowledge_result=kr,
        problem_result=pr,
        attempt_result=ar,
        method_result=mr,
    )
    assert snap.method_rows[0].status == "draft"
    assert "draft" in render_method_index(snap)


def test_real_project_method_rows() -> None:
    from pathlib import Path as P

    real = P(__file__).resolve().parents[2]
    kr, pr, ar, mr = _validated(real)
    snap = build_workspace_snapshot(
        real,
        knowledge_result=kr,
        problem_result=pr,
        attempt_result=ar,
        method_result=mr,
    )
    ids = [r.object_id for r in snap.method_rows]
    assert ids == ["M0001", "M0002"]
    m1 = next(r for r in snap.method_rows if r.object_id == "M0001")
    m2 = next(r for r in snap.method_rows if r.object_id == "M0002")
    assert m1.status == "draft"
    assert m2.status == "draft"
    assert "K0001" in m1.knowledge
    assert m2.knowledge == "—"
