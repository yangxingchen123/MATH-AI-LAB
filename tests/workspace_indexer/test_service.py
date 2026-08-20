"""Tests for Workspace Indexer v1.2."""

from __future__ import annotations

import hashlib
from pathlib import Path

from tools.attempt_validator import validate_project as validate_attempt_project
from tools.knowledge_validator import validate_project as validate_knowledge_project
from tools.method_validator import validate_project as validate_method_project
from tools.problem_validator import validate_project as validate_problem_project
from tools.workspace_indexer.builder import build_workspace_snapshot, operational_workflow_from_path
from tools.workspace_indexer.constants import ASSISTANCE_OMITTED_LABEL, INDEX_DIR_RELATIVE, MANAGED_FILES
from tools.workspace_indexer.renderer import render_all, render_evidence_index
from tools.workspace_indexer.service import check_index, rebuild_index, sync_index

from .conftest import ensure_attempt_root, write_attempt, write_problem


def _validated(project: Path):
    kr = validate_knowledge_project(root=project)
    pr = validate_problem_project(root=project, knowledge_result=kr)
    ar = validate_attempt_project(root=project, problem_result=pr)
    mr = validate_method_project(root=project, knowledge_result=kr)
    return kr, pr, ar, mr


def test_deterministic_rebuild(project: Path) -> None:
    write_problem(project, "02_题目库/研究中/P0002_x.md", pid="P0002", title="B")
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
    a = render_all(snap)
    b = render_all(snap)
    assert a == b


def test_index_sorted_by_stable_id(project: Path) -> None:
    from tests.knowledge_indexer.conftest import write_knowledge

    write_knowledge(
        project,
        "01_知识库/z/K0002.md",
        kid="K0002",
        title="后",
        status="reviewed",
        extras="domain: 凸分析\nprerequisites: []\nrelated: []",
    )
    write_knowledge(
        project,
        "01_知识库/a/K0001.md",
        kid="K0001",
        title="先",
        status="reviewed",
        extras="domain: 凸分析\nprerequisites: []\nrelated: []",
    )

    kr, pr, ar, mr = _validated(project)
    snap = build_workspace_snapshot(
        project,
        knowledge_result=kr,
        problem_result=pr,
        attempt_result=ar,
        method_result=mr,
    )
    ids = [r.object_id for r in snap.knowledge_rows]
    assert ids == sorted(ids)


def test_operational_workflow_independent_from_yaml_status(project: Path) -> None:
    write_problem(project, "02_题目库/研究中/P0002_x.md", pid="P0002", title="研究", status="draft")

    kr, pr, ar, mr = _validated(project)
    snap = build_workspace_snapshot(
        project,
        knowledge_result=kr,
        problem_result=pr,
        attempt_result=ar,
        method_result=mr,
    )
    row = next(r for r in snap.problem_rows if r.object_id == "P0002")
    assert row.yaml_status == "draft"
    assert row.operational_workflow == "研究中"


def test_invalid_upstream_blocks_rebuild(project: Path) -> None:
    index_dir = project / INDEX_DIR_RELATIVE
    index_dir.mkdir(parents=True)
    sentinel = index_dir / "项目统计.md"
    sentinel.write_text("KEEP ME", encoding="utf-8")

    write_problem(project, "02_题目库/研究中/P0001_a.md", pid="P0001")
    write_problem(project, "02_题目库/已解决/P0001_b.md", pid="P0001")

    op = rebuild_index(root=project)
    assert op.result.value == "FAIL"
    assert sentinel.read_text(encoding="utf-8") == "KEEP ME"


def test_invalid_attempt_blocks_rebuild(project: Path) -> None:
    index_dir = project / INDEX_DIR_RELATIVE
    index_dir.mkdir(parents=True)
    hashes_before = {
        name: hashlib.sha256((index_dir / name).read_bytes()).hexdigest()
        for name in MANAGED_FILES
        if (index_dir / name).is_file()
    }
    for name in MANAGED_FILES:
        (index_dir / name).write_text(f"KEEP {name}", encoding="utf-8")
        hashes_before[name] = hashlib.sha256((index_dir / name).read_bytes()).hexdigest()

    write_problem(
        project,
        "02_题目库/研究中/P0002_x.md",
        pid="P0002",
        extras="parts:\n  - a\n  - b\n",
    )
    write_attempt(
        project,
        "11_学习证据/尝试记录/A000001.md",
        outcome="maybe",
    )

    op = sync_index(root=project)
    assert op.result.value == "FAIL"
    for name, digest in hashes_before.items():
        assert hashlib.sha256((index_dir / name).read_bytes()).hexdigest() == digest


def test_attempt_registry_in_snapshot(project: Path) -> None:
    write_problem(
        project,
        "02_题目库/研究中/P0002_x.md",
        pid="P0002",
        extras="parts:\n  - a\n  - b\n",
    )
    write_attempt(project, "11_学习证据/尝试记录/A000001.md", aid="A000001", part="b")
    write_attempt(
        project,
        "11_学习证据/尝试记录/A000002.md",
        aid="A000002",
        part="a",
        outcome="partial",
        assistance="independent",
        attempted_at='"2026-08-19T22:05+08:00"',
    )

    kr, pr, ar, mr = _validated(project)
    assert ar.summary.errors == 0
    snap = build_workspace_snapshot(
        project,
        knowledge_result=kr,
        problem_result=pr,
        attempt_result=ar,
        method_result=mr,
    )
    assert len(snap.attempt_rows) == 2
    assert [r.object_id for r in snap.attempt_rows] == ["A000001", "A000002"]


def test_evidence_index_sorted_by_attempt_id(project: Path) -> None:
    write_problem(
        project,
        "02_题目库/研究中/P0002_x.md",
        pid="P0002",
        extras="parts:\n  - a\n  - b\n",
    )
    write_attempt(project, "11_学习证据/尝试记录/A000010.md", aid="A000010", part="a")
    write_attempt(project, "11_学习证据/尝试记录/A000002.md", aid="A000002", part="a")
    write_attempt(project, "11_学习证据/尝试记录/A000001.md", aid="A000001", part="b")

    kr, pr, ar, mr = _validated(project)
    snap = build_workspace_snapshot(
        project,
        knowledge_result=kr,
        problem_result=pr,
        attempt_result=ar,
        method_result=mr,
    )
    text = render_evidence_index(snap)
    pos1 = text.index("A000001")
    pos2 = text.index("A000002")
    pos10 = text.index("A000010")
    assert pos1 < pos2 < pos10


def test_whole_target_display(project: Path) -> None:
    write_problem(project, "02_题目库/研究中/P0001_x.md", pid="P0001")
    write_attempt(
        project,
        "11_学习证据/尝试记录/A000001.md",
        aid="A000001",
        problem="P0001",
        part=None,
        outcome="unsolved",
        assistance=None,
    )

    kr, pr, ar, mr = _validated(project)
    snap = build_workspace_snapshot(
        project,
        knowledge_result=kr,
        problem_result=pr,
        attempt_result=ar,
        method_result=mr,
    )
    row = snap.attempt_rows[0]
    assert row.target == "whole"
    assert row.assistance == ASSISTANCE_OMITTED_LABEL
    assert "whole" in render_evidence_index(snap)


def test_assistance_omission_in_stats(project: Path) -> None:
    write_problem(
        project,
        "02_题目库/研究中/P0002_x.md",
        pid="P0002",
        extras="parts:\n  - a\n  - b\n",
    )
    write_attempt(project, "11_学习证据/尝试记录/A000001.md", assistance="assisted")
    write_attempt(
        project,
        "11_学习证据/尝试记录/A000002.md",
        aid="A000002",
        assistance="independent",
        part="a",
        outcome="partial",
    )
    write_attempt(
        project,
        "11_学习证据/尝试记录/A000003.md",
        aid="A000003",
        assistance=None,
        part="a",
        outcome="unassessed",
        attempted_at='"2026-08-20"',
    )

    kr, pr, ar, mr = _validated(project)
    snap = build_workspace_snapshot(
        project,
        knowledge_result=kr,
        problem_result=pr,
        attempt_result=ar,
        method_result=mr,
    )
    assert snap.attempt_assistance_counts["assisted"] == 1
    assert snap.attempt_assistance_counts["independent"] == 1
    assert snap.attempt_assistance_counts[ASSISTANCE_OMITTED_LABEL] == 1


def test_problem_attempt_count(project: Path) -> None:
    write_problem(project, "02_题目库/研究中/P0002_x.md", pid="P0002", extras="parts:\n  - a\n  - b\n")
    write_problem(project, "02_题目库/已解决/P0001_x.md", pid="P0001", status="reviewed", extras="knowledge: []")
    write_attempt(project, "11_学习证据/尝试记录/A000001.md", problem="P0002")
    write_attempt(
        project,
        "11_学习证据/尝试记录/A000002.md",
        aid="A000002",
        problem="P0002",
        part="a",
        outcome="partial",
        assistance="independent",
    )

    kr, pr, ar, mr = _validated(project)
    snap = build_workspace_snapshot(
        project,
        knowledge_result=kr,
        problem_result=pr,
        attempt_result=ar,
        method_result=mr,
    )
    p2 = next(r for r in snap.problem_rows if r.object_id == "P0002")
    p1 = next(r for r in snap.problem_rows if r.object_id == "P0001")
    assert p2.attempt_count == 2
    assert p1.attempt_count == 0


def test_outcome_counts(project: Path) -> None:
    write_problem(project, "02_题目库/研究中/P0002_x.md", pid="P0002", extras="parts:\n  - a\n  - b\n")
    write_attempt(project, "11_学习证据/尝试记录/A000001.md", outcome="correct")
    write_attempt(
        project,
        "11_学习证据/尝试记录/A000002.md",
        aid="A000002",
        part="a",
        outcome="partial",
        assistance="independent",
    )

    kr, pr, ar, mr = _validated(project)
    snap = build_workspace_snapshot(
        project,
        knowledge_result=kr,
        problem_result=pr,
        attempt_result=ar,
        method_result=mr,
    )
    assert snap.attempt_outcome_counts["correct"] == 1
    assert snap.attempt_outcome_counts["partial"] == 1
    assert snap.attempt_outcome_counts["incorrect"] == 0
    stats = render_all(snap)["项目统计.md"]
    assert "correct: 1" in stats
    assert "partial: 1" in stats
    assert "success rate" not in stats.lower()


def test_sync_current_no_op(project: Path) -> None:
    write_problem(project, "02_题目库/研究中/P0002_x.md", pid="P0002", extras="parts:\n  - a\n  - b\n")
    write_attempt(project, "11_学习证据/尝试记录/A000001.md", part="a")

    rebuild_index(root=project)

    def file_hashes() -> dict[str, str]:
        index_dir = project / INDEX_DIR_RELATIVE
        return {
            name: hashlib.sha256((index_dir / name).read_bytes()).hexdigest()
            for name in MANAGED_FILES
            if (index_dir / name).is_file()
        }

    before = file_hashes()
    op = sync_index(root=project)
    assert op.result.value == "UP_TO_DATE"
    after = file_hashes()
    assert before == after


def test_sync_stale_updates(project: Path) -> None:
    write_problem(project, "02_题目库/研究中/P0002_x.md", pid="P0002", title="T", extras="parts:\n  - a\n  - b\n")
    write_attempt(project, "11_学习证据/尝试记录/A000001.md", part="a")

    rebuild_index(root=project)
    write_problem(project, "02_题目库/研究中/P0002_x.md", pid="P0002", title="Changed", extras="parts:\n  - a\n  - b\n")

    op = sync_index(root=project)
    assert op.result.value == "BUILT"
    check = check_index(root=project)
    assert check.result.value == "CURRENT"


def test_attempt_body_only_change_no_generated_diff(project: Path) -> None:
    write_problem(project, "02_题目库/研究中/P0002_x.md", pid="P0002", extras="parts:\n  - a\n  - b\n")
    path = write_attempt(project, "11_学习证据/尝试记录/A000001.md", body="original body\n")

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
        path.read_text(encoding="utf-8").replace("original body", "completely different reasoning"),
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
    rendered2 = render_all(snap2)
    assert rendered1 == rendered2


def test_check_detects_stale(project: Path) -> None:
    write_problem(project, "02_题目库/研究中/P0002_x.md", pid="P0002", title="T", extras="parts:\n  - a\n  - b\n")
    write_attempt(project, "11_学习证据/尝试记录/A000001.md", part="a")

    rebuild_index(root=project)
    write_problem(project, "02_题目库/研究中/P0002_x.md", pid="P0002", title="Changed", extras="parts:\n  - a\n  - b\n")

    op = check_index(root=project)
    assert op.result.value in ("STALE", "FAIL")


def test_check_mode_read_only(project: Path) -> None:
    write_problem(project, "02_题目库/研究中/P0002_x.md", pid="P0002", extras="parts:\n  - a\n  - b\n")
    write_attempt(project, "11_学习证据/尝试记录/A000001.md", part="a")

    rebuild_index(root=project)

    def snapshot_tree(root: Path) -> dict[str, int]:
        return {
            str(p.relative_to(root)): p.stat().st_mtime_ns
            for p in root.rglob("*")
            if p.is_file()
        }

    before = snapshot_tree(project)
    check_index(root=project)
    after = snapshot_tree(project)
    assert before == after


def test_rebuild_write_boundary(project: Path) -> None:
    write_problem(project, "02_题目库/研究中/P0002_x.md", pid="P0002", title="Orig", extras="parts:\n  - a\n  - b\n")
    write_attempt(project, "11_学习证据/尝试记录/A000001.md", part="a")

    source = project / "02_题目库/研究中/P0002_x.md"
    source_before = source.read_text(encoding="utf-8")

    rebuild_index(root=project)

    assert source.read_text(encoding="utf-8") == source_before
    assert (project / INDEX_DIR_RELATIVE / "证据索引.md").is_file()


def test_output_index_excludes_latex_build_pdf(project: Path) -> None:
    latex_pdf = project / "04_LATEX/专题/main.pdf"
    latex_pdf.parent.mkdir(parents=True)
    latex_pdf.write_bytes(b"%PDF")

    out_pdf = project / "08_成果输出/PDF/正式.pdf"
    out_pdf.parent.mkdir(parents=True)
    out_pdf.write_bytes(b"%PDF")

    kr, pr, ar, mr = _validated(project)
    snap = build_workspace_snapshot(
        project,
        knowledge_result=kr,
        problem_result=pr,
        attempt_result=ar,
        method_result=mr,
    )
    assert snap.pdf_count == 1


def test_knowledge_index_no_attempt_aggregation(project: Path) -> None:
    write_problem(project, "02_题目库/研究中/P0002_x.md", pid="P0002", extras="parts:\n  - a\n  - b\n")
    write_attempt(project, "11_学习证据/尝试记录/A000001.md", part="a")

    kr, pr, ar, mr = _validated(project)
    snap = build_workspace_snapshot(
        project,
        knowledge_result=kr,
        problem_result=pr,
        attempt_result=ar,
        method_result=mr,
    )
    text = render_all(snap)["知识索引.md"]
    assert "Attempt" not in text
